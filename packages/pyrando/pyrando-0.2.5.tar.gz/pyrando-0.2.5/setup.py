from codecs import open
from os import path

from setuptools import setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyrando',
    version='0.2.5',
    description='Python module for Random.org JSON API',
    long_description=long_description,
    url='https://github.com/dfundingsland/pyrando',
    author='David Fundingsland',
    author_email='david@fundings.land',
    license='MIT',
    download_url='https://github.com/dfundingsland/pyrando/master.zip',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    packages=["pyrando"],
    install_requires=['requests >= 2.18.4'],
    python_requires='>=3'
)
