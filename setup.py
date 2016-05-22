#!/usr/bin/python 

# needed modules : psutil,pyudev
#- psutil python module (https://pypi.python.org/pypi/psutil)
#- pyudev (https://pyudev.readthedocs.org/en/latest/)
#- numpy
#  matplotlib 

# apt packages 
# libpng-dev , libfreetype6-dev

from setuptools import setup

def readme():
    with open('README.txt') as f:
        return f.read()

setup(name='pg_pybench',
      version='1.6',
      description='PostgreSQL benchmarking',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Benchmark',
      ],
      url='https://github.com/rugging24/pg_pybench',
      author='Olakunle Olaniyi',
      author_email='rugging24@gmail.com',
      license='PostgreSQL License',
      packages=['pg_pybench'],
      install_requires=[
          'psycopg2',
	  'psutil',
	  'pyudev',
      ],
      scripts=['bin/pg_pybench'],
      include_package_data=True,
      zip_safe=False)
