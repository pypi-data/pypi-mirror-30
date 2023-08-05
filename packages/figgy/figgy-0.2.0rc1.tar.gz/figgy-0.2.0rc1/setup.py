from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

version = '0.2.0.rc1'

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()

setup(
    name='figgy',
    version=version,
    description='Creates and populates configs for an app at first-time setup.',
    long_description=long_description,
    url='https://github.com/dyspop/figgy',
    author='Dan Black',
    author_email='dyspop@gmail.com',
    license='GPL-3.0+',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords=['config', 'configuration', 'generator', 'configuration generator', 'dev tool', 'json', 'tty', 'cli-like'],
    packages=find_packages(exclude=[]),
    install_requires=[],
    download_url='https://github.com/dyspop/figgy/archive/{v}.tar.gz'.format(v=version)
)
