# coding=utf-8

from setuptools import setup, find_packages
from os.path import join, dirname
from clusterp import __version__ as version

setup(
    name='clusterp',
    version=version,
    packages=find_packages(exclude=['*.tests.*']),
    url='https://github.com/abdelkafiahmed/clusterp',
    license='Apache License Version 2.0',
    author='Ahmed Abdelkafi',
    author_email='abdelkafiahmed@yahoo.fr',
    maintainer='Ahmed Abdelkafi',
    maintainer_email= 'abdelkafiahmed@yahoo.fr',
    description='Clusterp : Cluster profiling made easy',
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    download_url='https://github.com/abdelkafiahmed/clusterp/archive/{}.tar.gz'.format(version),
    platforms='ALL',
    install_requires=['matplotlib', 'pandas', 'numpy', 'fabric', 'pyyaml', 'file_read_backwards'],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'clusterp = clusterp.main:main',
        ]
    },
    classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Unix',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2 :: Only',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Clustering',
          'Topic :: System :: Software Distribution',
          'Topic :: System :: Systems Administration',
    ],
)
