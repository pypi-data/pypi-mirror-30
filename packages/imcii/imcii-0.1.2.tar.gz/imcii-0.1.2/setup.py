# coding=utf-8

from setuptools import setup

version = '0.1.2'

entry_points = {
    'console_scripts': [
        'imcii=imcii.ascii',
    ],
}

setup(
    name='imcii',
    packages=['imcii'],
    version=version,
    description='imcii = Image to ASCII',
    author='Windard Yang',
    author_email='windard@qq.com',
    url='https://windard.com',

    license="MIT",
    entry_points=entry_points,
)
