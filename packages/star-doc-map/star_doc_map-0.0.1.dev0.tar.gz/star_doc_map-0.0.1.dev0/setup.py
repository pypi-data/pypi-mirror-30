import os
import sys
from setuptools import setup

def get_packages(package):
    """Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]

setup(
    name='star_doc_map',
    version='0.0.1dev',
    description='Mapping API properties to ORM properties',
    packages=get_packages('star_doc_map'),
    install_requires=[
        'SQLAlchemy',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'console_scripts': [
            'star_doc_map=star_doc_map:main'
        ],
    },
)
