from setuptools import setup

setup(
    name = 'pyscbwrapper',
    packages = ['pyscbwrapper'],
    version = '0.0.3a',
    description = "Python wrapper for Statistics Sweden's API",
    author = 'Kira Coder Gylling',
    author_email = 'kira.gylling@gmail.com',
    url = 'https://github.com/kirajcg/pyscbwrapper',
    download_url = 'https://github.com/kirajcg/pyscbwrapper/tarball/0.0.3',
    install_requires = ['requests>=2.12.4'],
    license = 'GPL 3.0',
    keywords = ['scb', 'json', 'wrapper', 'data', 'statistics'],
    classifiers = [],
)
