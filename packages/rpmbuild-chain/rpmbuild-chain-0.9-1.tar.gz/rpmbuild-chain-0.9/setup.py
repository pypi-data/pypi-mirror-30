import re
import os
from setuptools import setup

def get_version():
    data = open('rpmbuild_chain/rpmbuild_chain.py', 'r').read()
    m = re.search('^__version__ = [\'"]([^\'"]+)[\'"]', data, re.M)
    if m:
        return m.group(1)
    else:
        raise RuntimeError('Unable to find version string')

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    long_description = f.read()

setup(
    name='rpmbuild-chain',
    version=get_version(),
    description='Build a series of SRPMs with rpmbuild',
    long_description=long_description,
    url='https://github.com/jwmullally/rpmbuild-chain',
    author='Joseph Mullally',
    author_email='jwmullally@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    packages=['rpmbuild_chain'],
    install_requires=[
        ],
    test_suite='nose.collector',
    tests_require=[
        'nose',
        ],
    entry_points={
        'console_scripts': [
            'rpmbuild-chain = rpmbuild_chain.rpmbuild_chain:cli'
            ]
        },
)
