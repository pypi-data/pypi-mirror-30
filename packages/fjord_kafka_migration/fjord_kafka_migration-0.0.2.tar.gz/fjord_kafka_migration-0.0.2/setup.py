'''
Created on Feb 21, 2018

@author: jliu
'''
from setuptools import setup
from setuptools import find_packages

from fjord_kafka_migration import __version__


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='fjord_kafka_migration',
      version=__version__,
      description='fjord kafka migration tools.',
      long_description=readme(),
      keywords='fjord kafka migration tools built specific for aws environment.',
      author='Tony Liu',
      packages=find_packages(exclude=["tests", ]),
      install_required=[
          'paramiko', 'scp'
      ],
      scripts=['scripts/fjord_kafka_migration'],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "Intended Audience :: System Administrators",
          "Operating System :: POSIX",
          "Operating System :: MacOS :: MacOS X",
      ],
      include_package_date=True,
      zip_safe=False
      )

