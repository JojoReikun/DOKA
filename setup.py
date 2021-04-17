#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LizardDLCAnalysis Toolbox
© Johanna T. Schultz
© Fabian Plum
Licensed under MIT License
"""

import setuptools

setuptools.setup(
    name='lizardanalysis',
    version='0.1',
    author='Jojo Schultz',
    #py_modules=['lizardanalysis'],
    install_requires=[
        'Click', 'ipython', 'numpy', 'scipy', 'pandas', 'matplotlib', 'os', 'glob', 'ruamel.yaml', 'tkinter',
        'tkFileDialog', 'uncertainties', 'tqdm'
    ],
    packages=setuptools.find_packages(),
    data_files=[('lizardanalysis',['lizardanalysis/config.yaml'])],
    include_package_data=True,
    entry_points='''
        [console_scripts]
        lizardanalysis=lizardanalysis:main
    ''',
)