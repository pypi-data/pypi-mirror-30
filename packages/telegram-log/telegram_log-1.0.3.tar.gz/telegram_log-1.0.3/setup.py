# coding: utf-8
from setuptools import setup, find_packages

import telegram_log

setup(
    name='telegram_log',
    version=telegram_log.__version__,
    author='Ruslan Gilfanov',
    author_email='rg@informpartner.com',
    packages=find_packages(),
    package_dir={'telegram_log': 'telegram_log'},
    install_requires=[
        'python-telegram-bot',
    ],
)
