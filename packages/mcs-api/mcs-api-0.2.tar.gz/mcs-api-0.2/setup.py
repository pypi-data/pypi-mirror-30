from setuptools import setup, find_packages
import mcs

setup(
    name = 'mcs-api',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    version=mcs.__version__,
    description = 'A simple Python wrapper around the Macquarie Cloud Services API',
    author = 'Aaron Foley',
    license='MIT',
    author_email = 'afoley@macquariecloudservices.com',
    url = 'https://bitbucket.org/AaronFoleyMT/mci-api/',
    download_url = 'https://bitbucket.org/AaronFoleyMT/mci-api/get/0.1.tar.gz',
    keywords = ['macqaurie cloud services', 'api'],
    install_requires=[
        'requests',
    ],
)