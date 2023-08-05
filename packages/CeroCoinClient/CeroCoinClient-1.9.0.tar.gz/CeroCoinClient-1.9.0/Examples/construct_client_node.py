#!/usr/bin/env python

##  construct_cerocoin_node.py

##  After installing the CeroCoinClient module, you would need to execute the script
##  shown in in this file in the different laptops you are using for your classroom
##  or network lab demo.

##  As explained in the main doc page, it is a good idea to use different values for
##  for the constructor parameters starting_pow_difficulty and
##  num_transactions_in_block in the different clients in your demo.  That gives you
##  a gentler start for the demo --- although eventually all the laptops will change
##  their proof-of-work difficulty level in order for this parameter to be consistent
##  across the network.  By gentler start for the demo, I mean you showing the
##  formation of coins, the formation of transaction, and the construction of blocks
##  without becoming overwhelmed by the blocks going back and forth in the network.

import CeroCoinClient


network = ['192.168.43.12','10.0.0.11','10.252.137.41','192.168.43.244']

ceronode = CeroCoinClient.CeroCoinClient(  
                              cerocoin_network           =  network,
                              modulus_size               =  512,    # intentionally small for demos
                              starting_pow_difficulty    =  251,     
#                             starting_pow_difficulty    =  240,    
                              num_transactions_in_block  =  2,
#                             num_transactions_in_block  =  4,
                              max_iterations_debug_mode  =  200,
           )                                  

ceronode.initialize_node_and_run()    



