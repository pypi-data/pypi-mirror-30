#!/usr/bin/env python

### setup.py

#from distutils.core import setup

from setuptools import setup, find_packages
import sys, os

setup(name='CeroCoinClient',
      version='2.0.1',
      author='Avinash Kak',
      author_email='kak@purdue.edu',
      maintainer='Avinash Kak',
      maintainer_email='kak@purdue.edu',
      url='https://engineering.purdue.edu/kak/distCeroCoin/CeroCoinClient-2.0.1.html',
      download_url='https://engineering.purdue.edu/kak/distCeroCoin/CeroCoinClient-2.0.1.tar.gz',
      description='A Python based educational platform for learning and teaching the basic concepts of crypto currencies',
      long_description=''' 


Consult the module API page at 

      https://engineering.purdue.edu/kak/distCeroCoin/CeroCoinClient-2.0.1.html

for all information related to this module, including
information regarding the latest changes to the code. The
page at the URL shown above lists all of the module
functionality you can invoke in your own code.  That page
also explains how the module can be used in a classroom
setting to explain the following three fundamental concepts
in crypto currencies: (1) What it means to mine a coin; (2)
How the ownership of a coin is transferred from one CeroCoin
client to another; and (3) How the notion of blockchain is
used to prevent "double-spending".

**Version 2.0.1** is a Python 3.x compliant version of the CeroCoinClient module.  This
version should work with both Python 2.x and Python 3.x

**Version 1.9.1** includes enhanced and cleaned-up documentation. The module
implementation code remains unchanged.

Typical usage syntax for creating a CeroCoin client after you have installed the module:

::

        ceronode = CeroCoinClient.CeroCoinClient(
                                          cerocoin_network           =  network,
                                          modulus_size               =  M,
                                          starting_pow_difficulty    =  N,
                                          num_transactions_in_block  =  K,
                                          max_iterations_debug_mode  =  200,
                   )
        ceronode.initialize_node_and_run()


          ''',

      license='Python Software Foundation License',
      keywords='crypto currencies, hashing, public-key cryptography',
      platforms='All platforms',
      classifiers=['Topic :: Scientific/Engineering :: Information Analysis', 'Programming Language :: Python :: 2.7', 'Programming Language :: Python :: 3.5'],
      packages=['CeroCoinClient','SHA256','PrimeGenerator']
)
