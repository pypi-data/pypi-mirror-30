from distutils.core import setup
from os import walk
import os
import sys


def 讀(檔名):
    return open(os.path.join(os.path.dirname(__file__), 檔名)).read()


def 揣工具包(頭):
    'setup的find_packages無支援windows中文檔案'
    工具包 = []
    for 目錄, _, 檔案 in walk(頭):
        if '__init__.py' in 檔案:
            工具包.append(目錄.replace('/', '.'))
    return 工具包


setup(
    name='twisas',
    packages=揣工具包('twisas'),
    version='0.1.0',
    description='twisas',
    long_description=讀('README.md'),
    author='薛丞宏',
    author_email='ihcaoe@gmail.com',
    keywords=[
        'Corpus', '語料庫',
        'Taiwan', 'Taiwanese',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=[
        'tai5-uan5_gian5-gi2_hok8-bu7',
    ]
)
