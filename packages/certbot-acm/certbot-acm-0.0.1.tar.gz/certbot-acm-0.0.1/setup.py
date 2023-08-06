# coding: utf-8
from setuptools import setup, find_packages


setup(
    name='certbot-acm',
    version='0.0.1',
    description='ACM installer plugin for Certbot client',
    url='https://github.com/selu/certbot-acm',
    author='Szabolcs Seláf',
    author_email='selu@selu.org',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'certbot',
        'zope.interface',
        'boto3'
    ],
    keywords=['certbot', 'acm'],
    entry_points={
        'certbot.plugins': [
            'installer = certbot_acm.installer:Installer'
        ]
    }
)
