import os
from setuptools import setup


def readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
        return f.read()


setup(
    name='template-file-parser',
    version='0.14',
    description='Tiny wrapper over string templates which works with files',
    long_description=readme(),
    url='https://github.com/david-gang/template-file-parser',
    author='David Gang',
    author_email='michaelgang@gmail.com',
    license='Apache 2.0',
    packages=['template_file_parser'],
    python_requires=">=3.4",
    zip_safe=False)
