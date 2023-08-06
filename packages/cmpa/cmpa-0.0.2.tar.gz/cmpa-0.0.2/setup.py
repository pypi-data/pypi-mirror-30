
from setuptools import setup

from cmpa import __version__, __title__, __author__, __author_email__, __url__, __download_url__

with open('index.rst', encoding='utf-8') as f:
    long_description = '\n' + f.read()

setup(
    name=__title__,
    description='Comparison utility',
    long_description=long_description,
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    license='MIT License',
    url=__url__,
    download_url=__download_url__,
    keywords=['directory', 'file', 'comparison', 'utility'],
    packages=[__title__],
    package_data={'': ['index.rst']},
    install_requires=[],
    classifiers=[]
)
