# coding=utf-8

from setuptools import setup

version = '0.1.1'

entry_points = {
    'console_scripts': [
        'imcii=imcii.ascii:test',
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
    install_requires=[
        "click==6.7",
    ],
    entry_points=entry_points,
)
