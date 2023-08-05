#!/usr/bin/env python
"""
This program builds a series of SRPMs with rpmbuild.

Each resulting RPM is added to a local YUM repository, making them
available as build dependencies for subsequent SRPMs. This is similar
in operation to mockchain, except the RPMs are built in the local system
instead of a dedicated build chroot. This is useful for building a small
series of RPMs that will be installed onto the same system, e.g. during
container builds.

Optionally, any RPMs installed or removed to satisify build dependencies
can be rolled back after the build has finished, provided they are still
available in the configured YUM repositories.

Warning: Installed packages and changes to the system may unknowingly
affect the produced RPMs between builds. In almost every case,
mock/mockchain is the recommended way to build RPMs using consistent
reproducible clean buildroots, especially if they are to be redistributed
to other systems. When satisifying build-dependencies, some packages
may be temporarily uninstalled, so its not recommended to run this on
live production hosts.

This program must be run as "root" in order to install any missing build
dependencies. All other commands (e.g. rpmbuild) are executed under the
specified non-root user to improve security.
"""

# URL: https://github.com/jwmullally/rpmbuild_chain
# LICENSE: MIT
# Copyright 2018 Joseph Mullally
# 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import argparse
import datetime
import errno
import fcntl
import glob
import grp
import gzip
import logging
import os
import pprint
import pwd
import re
import shutil
import subprocess
import sys
import tempfile

__all__ = [
        ]

__version__ = '0.9'

def parse_args(argv):
    parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description=__doc__)
    parser.add_argument('--srpms', nargs='+', default=[],
            help='Input SRPM files to build. If directory, recursively scan for RPMs. Use "-" to read list from STDIN')
    parser.add_argument('--user', required=True,
            help='Non-privileged user to run rpmbuild')
    parser.add_argument('--repo-path', default='rpmbuild-chain',
            help='Destination directory to store the built RPMs')
    parser.add_argument('--repo-name', default='rpmbuild-chain',
            help='Name for the YUM repository configuration')
    parser.add_argument('--build-path',
            help='Directory to build the RPMs in. Use tmpfs for faster builds. Default: tmpdir')
    parser.add_argument('--order', nargs='+', default=[],
            help='Package build order, given by list of package names')
    parser.add_argument('--order-files', nargs='+', default=[],
            type=argparse.FileType('r'), help='Read --order from files')
    parser.add_argument('--no-rollback-builddep', action='store_true',
            help='Do not automatically rollback installed RPM BuildRequires')
    parser.add_argument('--keep-repo-config', action='store_true',
            help='Keep YUM repository configured after exiting')
    parser.add_argument('--allow-scriptlets', action='store_true',
            help='Do not abort if RPM scriptlets are found. Warning: scriptlets will be run as root when package is installed')
    parser.add_argument('--hookdir', nargs='+', default=[],
            help='Hook script directory(s). Valid subdirectories: {}'.format(' '.join(Plugin.VALID_HOOKS)))
    parser.add_argument('--lint', action='store_true',
            help='Run rpmlint on every package')
    parser.add_argument('--verbose', dest='loglevel', action='store_const', const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('--version', action='version', version='%(prog)s {}'.format(__version__))
    args = parser.parse_args(argv[1:])
    return args


class RunCmdError(subprocess.CalledProcessError):
    def __init__(self, returncode, cmd, output, cwd, run_as_user):
        super(RunCmdError, self).__init__(returncode, cmd, output)
        self.cwd = cwd
        self.run_as_user = run_as_user
        self.args = (returncode, cmd, output, cwd, run_as_user)

    def __str__(self):
        return 'cmd={}, cwd={}, run_as_user={}: exited with return code: {}, output:\n{}'.format(self.cmd, self.cwd, self.run_as_user, self.returncode, self.output)


class RunAsUser(object):
    def __init__(self, user):
        self.user = str(user)
        pw = pwd.getpwnam(user)
        self.uid = pw.pw_uid
        self.gid = pw.pw_gid
        self.groups = [g.gr_gid for g in grp.getgrall() if user in g.gr_mem]

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.user)

    def __str__(self):
        return '<{}: user={}, uid={}, gid={}, groups={}>'.format(
                self.__class__.__name__, self.user, self.uid, self.gid, self.groups)

    def _popen_preexec_fn(self):
        os.setgroups(self.groups)
        os.setgid(self.gid)
        os.setuid(self.uid)

    def run_cmd(self, cmd, cwd=None, check_call=True, verbose=True, outfile=None):
        logging.debug('run_cmd({}) user=\'{}\''.format(cmd, self.user))
        with SetEUID(0, 0):
            proc = subprocess.Popen(
                    cmd, cwd=cwd, env={},
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    preexec_fn=self._popen_preexec_fn)
        outlines = []
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            if verbose:
                logging.debug('STDOUT: {}'.format(line.rstrip()))
            outlines.append(bytes(line).decode())
            if outfile:
                outfile.write(line)
        output = ''.join(outlines)
        rc = proc.wait()
        logging.debug('run_cmd(): return code: {}'.format(rc))
        if check_call and rc != 0:
            raise RunCmdError(rc, cmd, output, cwd, self)
        return rc, output


class CWD(object):
    def __init__(self, cwd):
        self.cwd = cwd

    def __enter__(self):
        self.old_cwd = os.getcwd()
        os.chdir(self.cwd)

    def __exit__(self, *args):
        os.chdir(self.old_cwd)
 

class SetEUID(object):
    def __init__(self, euid, egid):
        self.euid = euid
        self.egid = egid

    def __enter__(self):
        self.old_euid = os.geteuid()
        self.old_egid = os.getegid()
        os.setegid(self.egid)
        os.seteuid(self.euid)

    def __exit__(self, *args):
        os.setegid(self.old_egid)
        os.seteuid(self.old_euid)


def cmd_exists(cmd):
    return any(
            os.access(os.path.join(path, cmd), os.X_OK) 
            for path in os.environ['PATH'].split(os.pathsep)
            )


USE_DNF = cmd_exists('dnf')


def mkdir(path, erase=False):
    if os.path.exists(path) and erase == True:
        shutil.rmtree(path)
    if not os.path.isdir(path):
        os.mkdir(path)


class RPMLock(object):

    PATH='/var/lib/rpm/.rpm.lock'

    def __init__(self):
        pass

    def __enter__(self):
        logging.debug('Acquiring RPM DB lock on {}'.format(self.PATH))
        with SetEUID(0, 0):
            self.fd = os.open(self.PATH, os.O_RDWR)
        try:
            fcntl.lockf(self.fd, fcntl.LOCK_EX)
        except:
            logging.exception('Unable to acquire RPM DB lock on {}'.format(self.PATH))
            os.close(self.fd)
            raise
        logging.debug('Acquired RPM DB lock')

    def __exit__(self, *args):
        logging.debug('Releasing RPM DB lock')
        fcntl.lockf(self.fd, fcntl.LOCK_UN)
        os.close(self.fd)


class YUMRepoConfig(object):

    VALID_NAME = re.compile('^[a-zA-Z0-9_-]+$')
    TEMPLATE = """\
[{name}]
name={name}
baseurl=file://{path}
enabled=1
gpgcheck=0
metadata_expire=0
"""
    CONFIG_DIR = '/etc/yum.repos.d'

    def __init__(self, name, path, keep=False):
        if not self.VALID_NAME.match(name):
            raise ValueError('YUMRepo: name="{}" doesnt match regex "{}"'.format(name, self.VALID_NAME))
        self.name = name
        with open(os.path.join(path, 'repodata/repomd.xml'), 'r'):
            pass
        self.path = os.path.abspath(path)
        self.keep = bool(keep)
        self.config = self.TEMPLATE.format(name=self.name, path=self.path)
        self.config_path = os.path.join(self.CONFIG_DIR, '{}.repo'.format(self.name))

    def __enter__(self):
        logging.info('Adding YUM repo config: {}'.format(self.config_path))
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as infile:
                if infile.read() != self.config:
                    raise OSError(errno.EEXIST, os.strerror(errno.EEXIST), self.config_path)
        else:
            with SetEUID(0, 0):
                with open(self.config_path, 'w') as outfile:
                    outfile.write(self.config)

    def __exit__(self, *args):
        if not self.keep:
            logging.info('Removing YUM repo config: {}'.format(self.config_path))
            with SetEUID(0, 0):
                os.remove(self.config_path)


class RPMHistoryRollback(object):

    def __init__(self, history_path, root=None, active=False):
        self.history_path = history_path
        self.root = root if root else RunAsUser('root')
        self.active = bool(active)

    def __enter__(self):
        if self.active:
            logging.info('Checkpointing current RPM transaction ID to "{}"'.format(self.history_path))
            if os.path.exists(self.history_path):
                with open(self.history_path, 'r') as history_file:
                    self.tx_id = int(history_file.read())
                logging.info('Read RPM transaction ID from previous run: {}'.format(self.tx_id))
            else:
                if USE_DNF:
                    _, output = self.root.run_cmd(['dnf', 'history', 'info'])
                else:
                    _, output = self.root.run_cmd(['yum', 'history', 'info'])
                self.tx_id = int(re.search('^Transaction ID .* ([0-9]+)$', output, re.M).groups()[0])
                with open(self.history_path, 'w') as history_file:
                    history_file.write(str(self.tx_id))
                logging.info('Saved current RPM transaction ID: {}'.format(self.tx_id))

    def __exit__(self, *args):
        if self.active:
            logging.info('Rolling back installed packages to RPM transaction ID: {}'.format(self.tx_id))
            if USE_DNF:
                self.root.run_cmd(['dnf', 'history', '-y', 'rollback', str(self.tx_id)])
            else:
                self.root.run_cmd(['yum', 'history', '-y', 'rollback', str(self.tx_id)])
            os.remove(self.history_path)


class RPMBuild(object):
    def __init__(self, topdir, pkg, filepath, user, root, plugins, allow_scriptlets=False):
        self.topdir = os.path.abspath(topdir)
        self.pkg = pkg
        if not os.path.exists(filepath):
            raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), filepath)
        if not filepath.endswith('.rpm'):
            raise ValueError('Not a valid RPM file: {}'.format(filepath))
        self.filepath = os.path.abspath(filepath)
        self.user = user
        self.root = root
        self.plugins = plugins
        self.allow_scriptlets = bool(allow_scriptlets)

    def run(self):
        with CWD(self.topdir):
            try:
                if self.filepath.endswith('.src.rpm'):
                    logging.info('{}: Building SRPM...'.format(self.pkg))
                    self.build_srpm()
                    self.clean_rpmbuild_dir()
                else:
                    logging.info('{}: Prebuilt RPM, importing...'.format(self.pkg))
                    self.copy_prebuilt_rpm(filepath)
                self.plugins.run('post_build', self.topdir)
                self.post_build_checks()
            except:
                logging.exception('{}: Build failed'.format(self.pkg))
                with open('fail', 'w') as fail_file:
                    fail_file.write('undone')
                raise
            with open('success', 'w') as success_file:
                success_file.write('done')
            logging.info('{}: Build succeeded'.format(self.pkg))
            for fn in sorted(os.listdir('.')):
                if fn.endswith('.rpm'):
                    logging.info('{}: Result: {}'.format(self.pkg, fn))

    def build_srpm(self):
        rpm_opts = ['--verbose', '--define', '_topdir {}'.format(os.getcwd())]
        self.user.run_cmd(['rpm'] + rpm_opts + ['-i', self.filepath])

        spec = glob.glob('SPECS/*')[0]
        self.user.run_cmd(['rpmbuild'] + rpm_opts + ['-bs', spec])
        new_srpm = glob.glob('SRPMS/*')[0]

        if USE_DNF:
            self.root.run_cmd(['dnf', 'builddep', '-y', new_srpm])
        else:
            self.root.run_cmd(['yum-builddep', '-y', new_srpm])
        with RPMLock():
            self.plugins.run('pre_build', os.getcwd())
            with open('build.log', 'w') as build_log:
                self.user.run_cmd(['rpmbuild'] + rpm_opts + ['--clean', '-bb', spec], outfile=build_log)

        self.user.run_cmd(['rpmbuild'] + rpm_opts + ['--rmsource', spec])

    def clean_rpmbuild_dir(self):
        for subdir in ['BUILD', 'BUILDROOT', 'SOURCES']:
            os.rmdir(subdir)
        for subdir in ['RPMS', 'SRPMS', 'SPECS']:
            for root, subdirs, files in sorted(os.walk(subdir)):
                for filename in sorted(files):
                    shutil.move(os.path.join(root, filename), '.')
            shutil.rmtree(subdir)

    def copy_prebuilt_rpm(self):
        destfile = os.path.join(os.getcwd(), os.path.basename(self.filepath))
        shutil.copyfile(self.filepath, destfile)

    def post_build_checks(self):
        for filepath in glob.glob('*.rpm'):
            if not self.allow_scriptlets:
                rc, output = self.user.run_cmd(['rpm', '-qp', '--scripts', filepath])
                if output:
                    raise ValueError('RPM {} contains scriptlets:\n{}'.format(filepath, output))


class RPMBuild_Chain(object):

    def __init__(self, repo_name, repo_path, build_path, run_as_user, run_as_root, no_rollback_builddep=False, keep_repo_config=False, allow_scriptlets=False, plugins=None):

        self.repo_name = str(repo_name)
        self.repo_path = str(repo_path)
        self.user = run_as_user
        self.root = run_as_root
        if build_path:
            self.build_path = str(build_path)
        else:
            with SetEUID(self.user.uid, self.user.gid):
                self.build_path = tempfile.mkdtemp(prefix='rpmbuild-chain.')
        self.no_rollback_builddep = bool(no_rollback_builddep)
        self.keep_repo_config = bool(keep_repo_config)
        self.allow_scriptlets = bool(allow_scriptlets)

        self.plugins = Plugins(plugins)

        self.history_path = os.path.join(self.build_path, 'RPM_HISTORY_ID')

    def list_rpms(self, rpm_paths):
        results = []
        for rpm_path in rpm_paths:
            if os.path.isdir(rpm_path):
                for root, subdirs, files in sorted(os.walk(rpm_path)):
                    for filename in sorted(files):
                        if filename.endswith('.rpm'):
                            results.append(os.path.join(root, filename))
            else:
                if not rpm_path.endswith('.rpm'):
                    raise ValueError('Not a valid RPM file: {}'.format(filepath))
                results.append(rpm_path)
        return results

    def order_srpms(self, srpms, order):
        order_idx = {pkg:idx for idx,pkg in enumerate(order)}
        indexed = []
        unordered = []
        for srpm in srpms:
            _, pkg = self.user.run_cmd(['rpm', '-qp', '--qf', '%{NAME}', srpm])
            if pkg in order_idx:
                indexed.append((order_idx[pkg], srpm))
            else:
                unordered.append(srpm)
        return [srpm for idx, srpm in sorted(indexed)] + unordered

    def repo_create(self):
        self.user.run_cmd(['createrepo_c', '--excludes=_failed/*', self.repo_path])

    def repo_update(self):
        self.user.run_cmd(['createrepo_c', '--excludes=_failed/*', '--update', self.repo_path])

    def repo_contents(self):
        rc, output = self.user.run_cmd(['repoquery', '-qa', '--repoid={}'.format(self.repo_name)])
        return output

    def package_string(self, filepath):
        if filepath.endswith('.src.rpm'):
            qfmt = '%{NAME}-%{VERSION}-%{RELEASE}'
        else:
            qfmt = '%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}'
        rc, output = self.user.run_cmd(['rpm', '-qp', '--qf', qfmt, filepath])
        return output

    def build_srpm(self, filepath):
        logging.info('Processing "{}"'.format(filepath))
        filepath = os.path.abspath(filepath)
        if not os.path.exists(filepath):
            raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), filepath)
        if not filepath.endswith('.rpm'):
            raise ValueError('Not a valid RPM file: {}'.format(filepath))
        pkg = self.package_string(filepath)
        repo_dest = os.path.join(self.repo_path, pkg)
        if os.path.exists(repo_dest):
            logging.info('{}: Already built, skipping...'.format(pkg))
        else:
            topdir = os.path.join(self.build_path, pkg)
            mkdir(topdir, erase=True)
            try:
                RPMBuild(topdir, pkg, filepath, self.user, self.root, self.plugins, self.allow_scriptlets).run()
            except:
                mkdir(os.path.join(self.repo_path, '_failed'))
                failed_dest = os.path.join(self.repo_path, '_failed', pkg)
                if os.path.exists(failed_dest):
                    shutil.rmtree(failed_dest)
                shutil.move(topdir, os.path.join(self.repo_path, '_failed', pkg))
                raise
            shutil.move(topdir, repo_dest)
            self.repo_update()
        logging.info('{}: Done'.format(pkg))
        return pkg

    def build_srpms(self, filepaths, order=None):
        order = order if order else []
        filepaths = self.order_srpms(self.list_rpms(filepaths), order)
        logging.info('Starting build...')
        logging.info('Paramaters: {}'.format(pprint.pformat(vars(self))))
        logging.info('Filepaths: {}'.format(filepaths))
        logging.info('Order: {}'.format(order))
        n_pkgs = 0
        time_start = datetime.datetime.now()
        with SetEUID(self.user.uid, self.user.gid):
            mkdir(self.repo_path)
            mkdir(self.build_path, erase=True)
            self.repo_create()
            with RPMHistoryRollback(self.history_path, self.root, not self.no_rollback_builddep):
                with YUMRepoConfig(self.repo_name, self.repo_path, self.keep_repo_config):
                    self.plugins.run('pre_run', self.repo_path)
                    for filepath in filepaths:
                        try:
                            self.build_srpm(filepath)
                            n_pkgs += 1
                        except:
                            logging.exception('Failed to build "{}"'.format(filepath))
                            raise
                    self.plugins.run('post_run', self.repo_path)
                    logging.info('Built packages:\n{}'.format(self.repo_contents()))
            os.rmdir(self.build_path)
        time_end = datetime.datetime.now()
        logging.info('Built {} packages in {}'.format(n_pkgs, time_end - time_start))
        logging.info('Build complete')


class Plugins(object):
    def __init__(self, plugins=None):
        self.plugins = list(plugins) if plugins else []

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.plugins)

    def run(self, hook, cwd, *args):
        logging.debug('Running {} hooks...'.format(hook))
        for plugin in self.plugins:
            with CWD(cwd):
                plugin.run(hook, *args)
        logging.debug('Finished {} hooks...'.format(hook))


class Plugin(object):

    VALID_HOOKS = [
            'pre_run',      # cwd: repo dir
            'pre_build',    # cwd: rpmbuild topdir
            'post_build',   # cwd: rpmbuild topdir
            'post_run'      # cwd: repo dir
            ]

    def __init__(self, run_as_user):
        self.user = run_as_user

    def __repr__(self):
        return '<{} object at {}>'.format(self.__class__.__name__, hex(id(self)))

    def run(self, hook, *args):
        func = getattr(self, hook, None)
        if func:
            logging.debug('Running {}.{}'.format(self.__class__.__name__, hook))
            func(*args)


class Plugin_HookDir(Plugin):

    def __init__(self, run_as_user, hookdir):
        super(Plugin_HookDir, self).__init__(run_as_user)
        self.hookdir = os.path.abspath(hookdir)
        for hook in os.listdir(self.hookdir):
            if not hook in self.VALID_HOOKS:
                raise ValueError('{} contains unrecognized hook {}. Accepted: {}'.format(self.hookdir, hook, self.VALID_HOOKS))

    def run(self, hook, *args):
        if hook in os.listdir(self.hookdir):
            for exe in sorted(glob.glob(os.path.join(self.hookdir, hook, '*'))):
                logging.debug('Running {} {}'.format(exe, hook))
                self.user.run_cmd([exe])


class Plugin_PackageState(Plugin):

    PKG_STATE_QF = '%{nevra} %{buildtime} %{size} %{pkgid} installed'

    def pre_build(self):
        with gzip.open('installed_pkgs.log.gz', 'w') as ipl:
            self.user.run_cmd(['rpm', '-qa', '--qf', self.PKG_STATE_QF], outfile=ipl, verbose=False)


class Plugin_ParsedSpec(Plugin):

    def pre_build(self):
        spec = glob.glob('SPECS/*')[0]
        with open('{}.parsed'.format(spec), 'w') as pspec_out:
            self.user.run_cmd(['rpmspec', '-P', spec], outfile=pspec_out)


class Plugin_Lint(Plugin):

    def post_build(self):
        with open('rpmlint.log', 'w') as rpmlint_log:
            self.user.run_cmd(['rpmlint'] + glob.glob('*.rpm'), outfile=rpmlint_log)


class Plugin_RepoList(Plugin):

    def pre_run(self):
        with open('repolist.log', 'w') as repos_log:
            if USE_DNF:
                self.user.run_cmd(['dnf', '-v', 'repolist', 'enabled'], outfile=repos_log)
            else:
                self.user.run_cmd(['yum', '-v', 'repolist', 'enabled'], outfile=repos_log)


def main(args):
    logging.basicConfig(level=args.loglevel)
    logging.info('Called with {}'.format(args))

    if not os.geteuid() == 0:
        raise ValueError('Program needs to be run as root')

    if args.srpms == ['-']:
        args.srpms = [line.rstrip() for line in sys.stdin]
    for order_file in args.order_files:
        args.order.extend(order_file.read().splitlines())

    run_as_user = RunAsUser(args.user)
    run_as_root = RunAsUser('root')

    plugins = [
            Plugin_ParsedSpec(run_as_user),
            Plugin_PackageState(run_as_user),
            Plugin_RepoList(run_as_root),
            ]
    for hookdir in args.hookdir:
        plugins.append(Plugin_HookDir(run_as_user, hookdir))
    if args.lint:
        plugins.append(Plugin_Lint(run_as_user))

    rpmbuilder = RPMBuild_Chain(
            args.repo_name,
            args.repo_path,
            run_as_user=run_as_user,
            run_as_root=run_as_root,
            build_path=args.build_path,
            no_rollback_builddep=args.no_rollback_builddep,
            keep_repo_config=args.keep_repo_config,
            allow_scriptlets=args.allow_scriptlets,
            plugins=plugins)
    rpmbuilder.build_srpms(args.srpms, order=args.order)


def cli():
    main(parse_args(sys.argv))


if __name__ == '__main__':
    cli()
