# -*- coding: utf-8 -*-
from setuptools import setup
packages = ['rpi-rf-tag']
install_requires = ['pi-rc522', 'rpi-rf']

setup(
    name='rpi-rf-tag',
    version='0.1.1',
    url='https://github.com/NetoBreba/rpi-rf-tag',
    license='MIT License',
    author='José Antonio da Silva Neto',
    author_email='jose.silvaneto@dce.ufpb.br',
    keywords=['python', 'raspberry', 'iot', 'rf', 'tag', 'automation'],
    description='Uma interface para abstrair todo de envio de messagem via rf e tag',
    packages=packages,
    install_requires=install_requires,
)