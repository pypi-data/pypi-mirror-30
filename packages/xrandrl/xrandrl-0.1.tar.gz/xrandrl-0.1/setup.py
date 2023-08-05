from setuptools import setup

import glob

version = '0.1'

setup(
    name='xrandrl',
    version=version,
    description='',
    author='Fabian Peter Hammerle',
    author_email='fabian@hammerle.me',
    url='https://github.com/fphammerle/xrandrl',
    download_url = 'https://github.com/fphammerle/xrandrl/tarball/{}'.format(version),
    keywords=[],
    classifiers=[],
    scripts=glob.glob('scripts/*'),
    install_requires=[],
    tests_require=['pytest'],
)
