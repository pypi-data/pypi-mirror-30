#!/usr/bin/env python

### setup.py

#from distutils.core import setup

from setuptools import setup, find_packages
import sys, os

setup(name='CeroCoinClient',
      version='1.9.0',
      author='Avinash Kak',
      author_email='kak@purdue.edu',
      maintainer='Avinash Kak',
      maintainer_email='kak@purdue.edu',
      url='https://engineering.purdue.edu/kak/distCeroCoin/CeroCoinClient-1.9.0.html',
      download_url='https://engineering.purdue.edu/kak/distCeroCoin/CeroCoinClient-1.9.0.tar.gz#md5=05d60c7779421d54cacafc1f374b5a18',
      description='A Python based educational platform for teaching the basic concepts of crypto currencies',
      long_description=''' 


Consult the module API page at 

      https://engineering.purdue.edu/kak/distCeroCoin/CeroCoinClient-1.9.0.html

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
      classifiers=['Topic :: Scientific/Engineering :: Information Analysis', 'Programming Language :: Python :: 2.7'],
      packages=['CeroCoinClient','SHA256','PrimeGenerator']
)
