# -*- coding: utf-8 -*-
"""
create on 2018-03-28 下午11:49

author @heyao
"""

from setuptools import setup, find_packages

from april3rd.memories import memory_path

with (memory_path.parent / 'VERSION').open(mode='rb') as f:
    version = f.read().strip().decode('ascii')

with (memory_path.parent / 'LONG').open(mode='rb') as f:
    long_description = f.read().decode('utf-8').strip()

setup(
    name='april3rd',
    author='heyao',
    version=version,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.6'
    ],
    author_email='syhens@163.com',
    url='https://github.com/Syhen/april3rd',
    install_requires=['python-dateutil', 'pathlib', 'pycrypto'],
    description="喝药和乖乖的6个月纪念日",
    long_description=long_description,
    packages=find_packages(),
    zip_safe=True,
    package_dir={'april3rd': 'april3rd'},
    package_data={'april3rd': ['memories/*', 'VERSION', 'LONG']}
)
