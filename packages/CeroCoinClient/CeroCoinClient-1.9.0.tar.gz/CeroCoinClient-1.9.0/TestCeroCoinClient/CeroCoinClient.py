__version__ = '1.9.0'
__author__  = "Avinash Kak (kak@purdue.edu)"
__date__    = '2018-March-20'
__url__     = 'https://engineering.purdue.edu/kak/distCeroCoin/CeroCoinClient-1-9.0.html'
__copyright__ = "(C) 2018 Avinash Kak. Python Software Foundation."


__doc__ = '''

CeroCoinClient.py

Version: ''' + __version__ + '''

Author: Avinash Kak (kak@purdue.edu)

Date: ''' + __date__ + '''

@tag_changes
CHANGES:

  Version 1.9.0

    This version includes improved inter-thread coordination among the miner
    thread, the transaction maker thread, and the block maker thread.  While
    this version uses boolean flags for thread coordination, I am planning to
    use Event based logic for doing the same in a future version of this module.


@tag_intro
INTRODUCTION:

    The purpose of this educational module is to serve as a platform for
    explaining the following three key notions of crypto currencies: (1) What it
    means to mine a coin; (2) How the ownership of a coin is transferred from
    one client to another in a network; and (3) How the notion of blockchain is
    used to prevent "double-spending".

    The presentation on crypto currencies is a part of Lecture 15 in my class on
    computer and network security at Purdue University.  The idea is for the
    students to learn about crypto currencies after they have become proficient
    with public-key cryptography and hashing functions.

    By its very definition, a crypto currency (CC) requires for its existence a
    network of hosts that (1) compete in discovering new coins at a prescribed
    level of proof-or-work difficulty; (2) that allow for coin ownership to be
    transferred through the notion of a transaction that requires the buyer to
    send its public key to the seller; and (3) that allows for all the prior
    transactions that were accepted by the network to be embedded in the next
    transaction through the magic of hashing.

    This solely network-based existence of CC makes it challenging to present
    the ideas involved in a classroom setting.  It is to address this challenge
    that I created the CeroCoinClient module.

    The simplest classroom presentation with this module involves two networked
    laptops that you can take with you to class. I will refer to the two laptops
    (which can obviously be any two digital devices capable of executing Python)
    as two CeroCoin clients. In one client, you execute this module with a
    relatively low level of proof-of-work (PoW) difficulty and, in the the other
    client, with a much higher PoW difficulty level.  This makes it highly
    likely that the client with the lower PoW difficulty will be the producer of
    new coins and the other laptop would serve as the "buyer" of those coins.
    By connecting the coin producing client to the overhead screen, you can
    demonstrate (1) the production of coins; (2) the making of a transaction,
    which requires the buyer to supply its public-key to the coin miner, and for
    the seller to sign off on the coin to which was appended the buyer's public
    key; and, finally, (3) the making of a block that is a packaging of a
    certain number of transactions.

    But note that PoW you assign to a client is just for getting started.  After
    the network has accepted a block, the client would have no choice but to
    make its PoW value consistent with what is in the received block.

    In any case, the two-laptop based presentation I have described above allows
    you to demonstrate in a classroom setting how a CeroCoin client abandons its
    current search for a new coin when it receives a block with a longer
    blockchain length and/or with a PoW difficulty level that exceeds the level
    being used in the current search. 

    This demonstration of how a CeroCoin client abandons its current search for
    a new coin when it receives a block of transactions with a longer blockchain
    length, or, for a given blockchain length, a higher level of PoW difficulty
    is made visually compelling by the fact that the students can see for
    themselves the change in the name of the coin miner thread in the display
    you project on the overhead screen.

    You can create even more interesting classroom demonstrations with more than
    two laptops, with all laptops running the CeroCoinClient module at a
    prescribed level of PoW difficulty that changes as blocks are received from
    the network.  You can demonstrate the blocks being transferred between the
    laptops and ongoing coin search in the individual laptops being replaced by
    new search upon receipt of blocks with longer blockchain lengths and/or
    blocks with higher levels of PoW difficulty.

    The best venue for giving multi-laptop demonstrations is a computer network
    lab where you can simultaneously project the outputs from the different
    laptops on different overhead screens.


@tag_whattodo
WHAT TO DO AFTER YOU HAVE INSTALLED THIS MODULE:

    The easiest thing to do after you have installed the module is to execute
    the script:

@begincode
        construct_client_node.py
@endcode

    that you will find in the Examples directory of the distribution.  For
    obvious reasons, you must execute this script in each of the clients you are
    using for your demo.  It is a good idea to use different values for the
    constructor parameters starting_pow_difficulty and num_transactions_in_block
    in the different clients. That gives you a gentler start for the demo ---
    although eventually all the clients will change their proof-of-work
    difficulty level in order for this parameter to be consistent across the
    network.  By gentler start for the demo, I mean you showing the formation of
    the coins, the formation of the transactions, and the construction of blocks
    without becoming overwhelmed by the blocks going back and forth in the
    network.

@tag_multi
CeroCoinClient --- A MULTITHREADED IMPLEMENTATION:

    A working demonstration of the principles that underlie CC requires an
    implementation that must either be multithreaded or one that is based on
    multiprocessing.  There are two important reasons for that: (1) The search
    for a new coin is a completely random process in which the time taken to
    discover the next coin cannot be predicted in advance. And (2) The ongoing
    search for a new coin must be abandoned immediately when a block of
    transactions is received from another client in the network if the received
    block has a blockchain length that is longer than what is being used in the
    current search, or, for a given blockchain length, if the received block has
    a PoW difficultly level that is higher than what is being used in the
    current search.

    That implies that, at the least, you must execute the coin mining code and
    the code that is in charge of receiving and validating incoming blocks in
    two separate threads or processes.  Since a client can construct a new block
    using mixture of transactions some of which are based on the coins
    discovered by the client, while others are based on the coins acquired from
    other clients, you are going to have to also run the block construction code
    in a separate thread or a process of its own.

    I have chosen a multithreaded implementation for CeroCoinClient that launches
    the following six different threads when you fire up the code in the
    CeroCoinClient module: (1) A server thread that monitors the server port
    6404 for requests for connection from other CeroCoinClient hosts in a
    network; (2) When the request for a connection is accepted by the server
    socket running in the server thread, it hands over the connection to a
    client connection thread that maintains that connection going forward; (3) A
    network scanner thread that establishes connections with the other CeroCoin
    hosts in the network; (4) A coin miner thread that is constantly searching
    for a new coin at a specified level of PoW difficulty; (5) A transaction
    maker thread that springs into action when a client discovers a new coin,
    offering the coin to the list of CeroCoin clients discovered by the scanner
    thread after this list is randomized; and, finally, (6) A block maker thread
    that springs into action when it sees a certain minimum number of
    transactions for packaging into a block.

    In what follows, I will first present the CeroCoin class whose instances
    represent the new coins that are discovered by the coin mining process, and
    then present what is accomplished in several of the threads listed above in
    an order that reflects how central a thread is to the overall demonstration
    of how the coins are discovered, validated, and traded in a CeroCoin
    network.


@tag_cerocoin
THE CeroCoin CLASS:

    A coin must contain all the information necessary for establishing its
    authenticity by the other CeroCoin clients in a network.  The coin must show
    the genesis string and the nonce whose combination led to the hash value
    that met the proof-of-work condition.  For obvious reasons, the coin
    definition must also include the PoW difficulty level used for discovering
    the coin. In the definition of CeroCoin, I have also included the identity
    of the miner, which is the SHA256 hash of the miner's public key.  Finally,
    the miner must sign the coin that was discovered.  Shown below is what a
    coin looks like before it is embedded in a transaction.

@begincode
    CEROCOIN_BEGIN 
    COIN_ID=e8e95b71
    COIN_MINER=7048aeaf64a9581e7937b73743984033ffbc71798b0e0f563508044fd5b4f566
    MINER_PUB_KEY=CEROCOIN_PUBKEY,mod=bf7945e8da95c52f509fa3357a3c7f415faead2a4e8b36856
          c06c9282da2838634d5c79cb64328a4e52b16ad39e0f877d9215c545f9e479244989638cd70db87,e=10001
    GENESIS_STRING=6629f94e11003069b3433b6d7acaf239aaf1007c06a99aa5668cce2a05110821884b
          0fb5996026f33e578e83300642ae20aa5bc07d1f6911a9e952871fe06c7efbadbae3391d562343
          dea79920b44e7d4eb1c861dc96dad5d47e60b91a7c7e748b7bc349fc17d4694ddf81c6c8ca14c8
          e14b89f9c38591dd874653cf6f657ae2
    NONCE=fbadbae3391d562343dea79920b44e7d4eb1c861dc96dad5d47e60b91a7c7e748b7bc349fc17d4
                                                694ddf81c6c8ca14c8e14b89f9c38591dd874653cf6f657ae2
    POW_DIFFICULTY=252 TIMESTAMP=1521231331.09
    HASHVAL=0347908fe169610afa4512b3b3cec9f1a7c12d6cb2359158d31f30ecea354528
    SELLER_SIGNATURE=5d2333fad828291b237f0c8668c52e77dbedeca3a78b6d9c53c7b8c5df4de9ace38
                                     db4486d18e8b682467ab3a60e82362f6e64b39b4cc8fd8f529783cf13a79d
    CEROCOIN_END
@endcode
    
    The display shown above has placed each field of the coin in a new line.
    That is just for ease of visualizing the structure of a coin.  The internal
    representation used for a coin does not include any newline characters.
    Note, too, that every coin has associated with it a 32-bit randomly
    generated ID as shown by the eight hex characters for the COIN_ID field.


@tag_miner
THE COIN MINER THREAD:

    The job assigned to the miner thread is to compute a hash of a string that
    is a combination of what I referred to as a genesis string and a nonce. For
    the very first coin in a network, the genesis string is a pseudorandomly
    generally bit vector of length 256.  However, after the clients start
    broadcasting blocks, a client would have no choice but to use the latest
    accepted block for creating the genesis string in its miner thread.
    Obviously, every CeroCoin client has the freedom to start at ground zero
    with a pseudorandomly generated genesis string.  However, after a block is
    accepted by the network, such a coin would not be accepted by the network
    because the length of the blockchain incorporated in it would be shorter
    than what is in the block that was accepted. The nonce is always generated
    pseudorandomly.

    The goal of the miner thread is keep on trying different possible values for
    the nonce until a hash value is discovered that corresponds to the current
    proof-of-value (PoW) difficulty level.  The PoW difficulty level is
    expressed as the acceptable upperbound for the hash value.  Since this
    module uses the SHA256 for hashing, the hash values produced are 256 bit
    wide. Setting PoW to, say, 240 means that we would want the hash value to be
    less than 2^240 in order to be acceptable for the discovery of a new
    coin. So the smaller the value of PoW difficulty, the the greater the
    challenge in discovering a new coin. Since a 256-bit hash implies 2^256
    different possible values for the hash, a PoW difficulty of K would
    translate into the ratio (2^K / 2^256) as the probability associated with
    coin discovery.  This probability can be made arbitrarily small by choosing
    a sufficiently small value for K.

    The miner thread presents the following sort of output as it searches for a
    new coin:

@begincode
    Thread-3 -- Try 1 -- hashval: 345ff09985e0adf08995de72ad427057d34e84ef83c380b22003ee8c4f18bc39
    Thread-3 -- Try 2 -- hashval: 4a46e047e4c4c5efcc51202275216617dcea433b424d0b5c091a23aa126b51be
    Thread-3 -- Try 3 -- hashval: 1366538d6213c2abf951fdeed5838f417c64bd704c9cd5613ff8937ccaa70062
    Thread-3 -- Try 4 -- hashval: 9542a932a80bb761869ad4c4c1919447205d5c21f4e991bee558ffdc7505c047
    Thread-3 -- Try 5 -- hashval: b776f4d8d35302504196a2c738c9bfb07c60535b00ba57979b03ea6afd8b96a1
    Thread-3 -- Try 6 -- hashval: 67ec79c047c41fdb5ed2ad598a9f364fde601f3b0c6925300f97775c45b656a1
    Thread-3 -- Try 7 -- hashval: a0b6e4dda5a0ef40e12cc247fab09bf05ebf8ea0c7dc1b57f69c83ecdf83ee2c
    Thread-3 -- Try 8 -- hashval: a7c267f63a34e381bc66a777b515eef215b3d8eaba63109e7f6388a9b1411372
                ...
                ...
                ...
@endcode

    It is important to note the name of the thread, "Thread-3" in the display
    shown above, in which the miner is running.  As mentioned earlier, when a
    client receives a new block that incorporates a blockchain length that
    exceeds the blockchain length in the genesis string being used currently, it
    must abandon the ongoing work at mining and start over with a new genesis
    string based on the new block.  This can be seen by the change in the name
    of the miner thread.  When such an event takes place, you will see the
    following sort of output in the terminal screen of the client that is
    abandoning the present coin search and starting over:

@begincode
        ========> received blockchain length:         12
        ========> self.blockchain_length:             8
        ========> received_block_pow_difficulty:      251
        ========> self.pow_difficulty:                251

        ========> WILL ASK THE CURRENT MINER THREAD TO STOP
        >>>>>>>>> CURRENT MINER THREAD TERMINATED SUCCESSFULLY <<<<<<<<<<<<
        ========> STARTING A NEW COIN MINER THREAD WITH POW DIFFICULTY OF 251 AND BLOCKCHAIN LENGTH OF 12
@endcode

@tag_transactor
THE TRANSACTION MAKER THREAD:

    In the code, I have abbreviated the name of this thread to "transactor"
    thread. (Sorry if you find the word "transactor" ugly.)

    The job assigned to the transactor thread is to find another client in the
    network who wants to acquire a coin.  This other client must express its
    willingness for becoming new owner of the coin by supplying its public key
    to the transactor.  The transactor thread appends the new owner's public key
    to the coin being traded, places a timestamp on the coin thus augmented, and
    digitally signs the resulting string. The output of these steps is referred
    to as a transaction.  Shown below is an example of such a transaction:

@begincode
    ----CEROCOIN_TRANSACTION_BEGIN
    TRANSACTION_ID=c64a8969 
    CEROCOIN_BEGIN 
    COIN_ID=e8e95b71
    COIN_MINER=7048aeaf64a9581e7937b73743984033ffbc71798b0e0f563508044fd5b4f566
    MINER_PUB_KEY=CEROCOIN_PUBKEY,mod=bf7945e8da95c52f509fa3357a3c7f415faead2a4e8b36856
              c06c9282da2838634d5c79cb64328a4e52b16ad39e0f877d9215c545f9e479244989638cd70db87,e=10001
    GENESIS_STRING=6629f94e11003069b3433b6d7acaf239aaf1007c06a99aa5668cce2a05110821884b0
              fb5996026f33e578e83300642ae20aa5bc07d1f6911a9e952871fe06c7efbadbae3391d562
              343dea79920b44e7d4eb1c861dc96dad5d47e60b91a7c7e748b7bc349fc17d4694ddf81c6c
              8ca14c8e14b89f9c38591dd874653cf6f657ae2
    NONCE=fbadbae3391d562343dea79920b44e7d4eb1c861dc96dad5d47e60b91a7c7e748b7bc349fc17d46
              94ddf81c6c8ca14c8e14b89f9c38591dd874653cf6f657ae2
    POW_DIFFICULTY=252 TIMESTAMP=1521231331.09
    HASHVAL=0347908fe169610afa4512b3b3cec9f1a7c12d6cb2359158d31f30ecea354528
    SELLER_SIGNATURE=5d2333fad828291b237f0c8668c52e77dbedeca3a78b6d9c53c7b8c5df4de9ace38db
              4486d18e8b682467ab3a60e82362f6e64b39b4cc8fd8f529783cf13a79d
    CEROCOIN_END
    SELLER=7048aeaf64a9581e7937b73743984033ffbc71798b0e0f563508044fd5b4f566
    SELLER_PUB_KEY=CEROCOIN_PUBKEY,mod=bf7945e8da95c52f509fa3357a3c7f415faead2a4e8b36856c0
                6c9282da2838634d5c79cb64328a4e52b16ad39e0f877d9215c545f9e479244989638cd70db87,e=10001
    BUYER_PUB_KEY=CEROCOIN_PUBKEY,mod=bf7945e8da95c52f509fa3357a3c7f415faead2a4e8b36856c06c
                  9282da2838634d5c79cb64328a4e52b16ad39e0f877d9215c545f9e479244989638cd70db87,e=10001
    TIMESTAMP=1521231336.11
    SELLER_TRANX_SIGNATURE=27b55110b47dad71378f5747d815e4ad5bc6ca130c45f871ed4b83d43c94a4f38
                  52e0eab033645c7287865d9a32eeb0009b04e6fb899c75d40f1220f31fb5c7e
    CEROCOIN_TRANSACTION_END---
@endcode

    Note again that the newlines in the display shown above are just to make it
    easier for the reader to see the different fields.  The internal
    representation of a transaction is just one continuous string without any
    newline characters in it.

@tag_blockmaker
THE BLOCK MAKER THREAD:

    The job assigned to the block maker thread is to (1) package the generated
    transactions into a block; (2) extend the blockchain length from the value
    used in the previous block whose hash is incorporated in the new block, the
    length being extended by the number of transactions in the current block;
    (3) incorporate a timestamp in the new block; (4) digitally sign the block
    with the private key of the client; and, finally, (5) broadcast the block
    the CeroCoin network.

    Note that a generated transaction cannot be treated on par with a received
    transaction for the purpose of constructing a block.  As mentioned earlier,
    a transaction has a particular structure that, at least at the beginning,
    indicates who produced the coin in the first place and to whom was the coin
    ownership transferred subsequently. More generally, though, a transaction
    indicates the change in ownership of a coin from a previous owner to its new
    owner. For a block maker to create a block from both the self discovered
    coins and the coins acquired from other clients, it would first need to
    extract the coins from the received transactions.  Subsequently, such coins
    could be treated in the same way as the self-generated coins.  This logic
    does not yet exist in the CeroCoinClient module. I plan to include it in 
    a later version.

@tag_smartphone
USING YOUR SMARTPHONE WiFi HOTSPOT FOR PORTABLE CeroCoin DEMOS:

    As mentioned earlier, a crypto currency has no existence outside a network.
    What that implies is that you cannot demonstrate the workings of crypto
    currency algorithms with a single digital device. (This statement of mine
    does not apply if you can create multiple virtual machines on a laptop. A
    network of VMs would obviously allow you to demonstrate all of the key
    concepts mentioned so far with a single laptop.)
    
    If you want to give demos with CeroCoinClient in different networking
    environments, you'd need to manually enter the IP addresses of all the
    digital devices you plan to use in your demo in the constructor call for the
    CeroCoinClient class.
    
    This can get to be tiring after a while.
    
    The easiest solution to the problem is to use the WiFi hotspot on your
    personal smartphone as a means to network all the digital devices you wish
    to use in your demo.  Say you create a two or three laptops based demo of
    CeroCoin at home, with all the laptops connected with the WiFi hotspot on
    your personal home.  The first time you do this, you will have to manually
    enter the IP addresses of the different laptops (as assigned by the
    smartphone WiFi hotspot) in the value of the constructor parameter.
    Subsequently, if you use same WiFi hotspot in your classroom for networking
    the laptops, you won't have to change a thing the IP addresses programmed
    into the CeroCoinClient constructor call.  This works because when
    connecting with a WiFi access point a digital device's first preference to
    ask for the same IP address as it had the last time.  If that address got
    assigned to some other client, your laptop would get a different IP address.
    So just make sure that you connect your demo laptops to your smartphone AP
    before you invite any of your students to join in through their own laptops.
    

@tag_usage
USAGE:

    To create a CeroCoinClient node in a network, all you have to do is to
    execute the following constructor call:

@begincode
        network = ['192.168.43.12','192.168.43.181','192.168.43.41','192.168.43.244']
        M       =  choose a value for the RSA modulus
        N       =  choose a value for proof-of-work difficulty level
        K       =  choose a value for how many transactions to pack into a block
        ceronode = CeroCoinClient.CeroCoinClient(  
                                          cerocoin_network           =  network,
                                          modulus_size               =  M,
                                          starting_pow_difficulty    =  N,         
                                          num_transactions_in_block  =  K,
                                          max_iterations_debug_mode  =  200,
                   )                                  
        ceronode.initialize_node_and_run()    
@endcode

    The next section elaborates on the four constructor parameters shown in
    the constructor call.

@tag_params
CONSTRUCTOR PARAMETERS:

    cerocoin_network:

        The IP addresses I have shown in the 'network' variable are typical of
        what I get for the hosts with my Android phone based WiFi hotspot.

        As I mentioned earlier in this doc page, using your own smartphone WiFi
        hotspot would make it much easier to create a portable demo with the
        CeroCoinClient module since it would save you the bother of having to
        manually enter the IP addresses in the cerocoin_network list each time
        you run the demo (especially if the demos are meant to be run in
        different network environments) with the same set of laptops.

    modulus_size:

        This is for the modulus to be used by a client in the RSA algorithm for
        generating its public/private key pair.

        For a classroom demonstration, you are better off using a small value
        like 512 for the modulus since that keeps size of the keys small enough
        so that you can conveniently display a transaction as a part of the demo
        (recall that a transaction must contain the public key of the buyer of
        the coin).  Obviously, using a small value like 512 for the modulus
        gives you no security at all in this day and age.  But that's okay for
        for just the demos.

    starting_pow_difficulty:

        This constructor parameter sets the proof-of-work difficulty level when
        a client first starts searching for a coin.  The smaller this integer,
        the greater the difficulty of finding an acceptable combination of the
        genesis string and a nonce whose hash value would not exceed 2^N.  This
        is just the starting value for PoW.  After the first block produced by
        any node in the CeroCoin network has been accepted by the network
        (including by the client in question), the client will change its PoW
        difficulty level in order to be consistent with that block.

        If you are giving a demo involving just two networked clients, my
        recommendation would be to set starting_pow_difficulty to something like
        252 in one client and to something like 240 in the other client.  This
        will make it highly likely that, at least at the beginning, the client
        with pow_difficulty set to 252 will generate enough coins to demonstrate
        the important crypto currency concepts during the limited time available
        in a classroom demonstration.  The client with pow_difficulty set to 240
        will act mostly as the "buyer" of the coins generated by the other
        client.  Obviously, after the latter client has accepted a block from
        the former client on account of blockchain length consideration, the
        former client will alter its own PoW difficulty level to what is found
        in the block.  Subsequently, both clients will start exchanging blocks
        on an equal basis as they discover new coins.

        The beginning phase of this interaction between the two clients will
        make it easier for you to demonstrate what is meant by a transaction and
        how the client that receives a block from the other client abandons its
        ongoing search for a coin and starts a fresh search using a new genesis
        string that is based on the received block.

        If you are giving a demo involving three clients, I'd recommend using
        starting_pow_difficulty levels for 252, 251, and 240 in the clients.
        This would allow the the clients running with starting_pow_difficulty
        levels of 252 and 251 to exchange transactions and blocks right from the
        beginning and the remaining client to act mostly as a receiver of the
        transactions and blocks (before it accepts a block from either of the
        other two clients).  Now you can illustrate how the first two clients
        set and reset their coin searches as each receives a new block from the
        other and so on.

    num_transactions_in_block:

        A client uses this value to decide when to pack the generated
        transactions into a block.  By using different values for this parameter
        in the different clients in a classroom demo, you can control the rate
        at which each client broadcasts its blocks to the rest of the network
        for a smoother explanation of the interaction between the clients.
        
    max_iterations_debug_mode:

        It is good to set some upper bound for this parameter especially if you
        are tinkering with the code.  Recall that a CeroCoinClient works through
        half a dozen different threads and several of the operations are carried
        out inside try-except clauses.  So it is possible for the coin miner
        thread to keep on working even when you have run into problems in some
        other thread.
        

@tag_install
INSTALLATION:

    The CeroCoinClient class was packaged using setuptools.  For installation,
    execute the following command-line in the source directory (this is the
    directory that contains the setup.py file after you have downloaded and
    uncompressed the package):

@begincode
            sudo python setup.py install
@endcode

    On Linux distributions, this will install the module file at a location that
    looks like

@begincode
             /usr/local/lib/python2.7/dist-packages/
@endcode

    If you do not have root access, you have the option of working directly off
    the directory in which you downloaded the software by simply placing the
    following statements at the top of your scripts that use the CeroCoinClient
    class:

@begincode
            import sys
            sys.path.append( "pathname_to_CeroCoinClient_directory" )
@endcode

    To uninstall the module, simply delete the source directory, locate where
    the CeroCoinClient module was installed with "locate CeroCoinClient" and
    delete those files.  As mentioned above, the full pathname to the installed
    version is likely to look like
    /usr/local/lib/python2.7/dist-packages/CeroCoinClient*

    If you want to carry out a non-standard install of the CeroCoinClient
    module, look up the on-line information on Disutils by pointing your browser
    to

              http://docs.python.org/dist/dist.html

@tag_bugs
BUGS:

    Please notify the author if you encounter any bugs.  When sending email,
    please place the string 'CeroCoin' in the subject line.


@tag_future
FUTURE PLANS:

    You will soon see a version of the module that will work with both Python 2
    and 3 (as is the case with all of my other Python modules).  Additionally, I
    am also planning to replace the inter-thread coordination logic with one
    based on events.


@tag_author
ABOUT THE AUTHOR:

    The author, Avinash Kak, recently finished a 17-year long "Objects Trilogy
    Project" with the publication of the book "Designing with Objects" by
    John-Wiley. If interested, visit his web page at Purdue to find out what
    this project was all about. You might like "Designing with Objects"
    especially if you enjoyed reading Harry Potter as a kid (or even as an
    adult, for that matter).

    For all issues related to this module, contact the author at kak@purdue.edu

    If you send email, please place the string "CeroCoin" in your subject line
    to get past the author's spam filter.


@tag_copyright
COPYRIGHT:

    Python Software Foundation License

    Copyright 2018 Avinash Kak

@endofdocs
'''

import ctypes
import sys,os,socket,signal,time
import threading
import string
import PrimeGenerator    # bundled with the CeroCoinClient module
import SHA256            # a BitVector based implementation bundled with the CeroCoinClient module
import random
import binascii

def interrupt_sig_handler( signum, frame ):                  
    print "=======> terminating all threads with kill"
    os.kill( os.getpid(), signal.SIGKILL )                           
    
signal.signal( signal.SIGINT,  interrupt_sig_handler )       

def message_hash(message):
    hasher = SHA256.SHA256(message = message)
    return hasher.sha256()  

def gcd(a,b):
    while b:
        a,b = b, a%b
    return a

def MI(num, mod):
    '''
    This function uses ordinary integer arithmetic implementation of the
    Extended Euclid's Algorithm to find the MI of the first-arg integer
    vis-a-vis the second-arg integer.
    '''
    NUM = num; MOD = mod
    x, x_old = 0, 1
    y, y_old = 1, 0
    while mod:
        q = num // mod
        num, mod = mod, num % mod
        x, x_old = x_old - q * x, x
        y, y_old = y_old - q * y, y
    if num == 1:
        MI = (x_old + MOD) % MOD
        return MI
    else:
        sys.exit("MI called with two args when first arg has no MI w.r.t the second arg")

def modular_exp(a,b,n):
    '''
    Python comes with a highly efficient implementation of modular exponentiation.  Nonetheless,
    let's have our own in order to make this demonstration consistent with the other demos in
    my class on computer and network security. The code snippet shown below is from
    Lecture 12 notes.
    '''
    result = 1
    while b > 0:
        if b & 1:
            result = (result * a) % n
        b = b >> 1
        a = (a * a) % n
    return result

lock = threading.Lock()

##########################################  class CeroCoinClient  ############################################

class CeroCoinClient( object ):                                     

    def __init__( self, **kwargs ):                                     
        run_miner_only=modulus_size=pub_exponent=None
        transaction=transactions=block=starting_pow_difficulty=debug=cerocoin_network=None
        max_iterations_debug_mode=num_transactions_in_block=None    
        local_ip_address=None
        if 'no_mining_just_trading' in kwargs    : no_mining_just_trading = kwargs.pop('no_mining_just_trading')
        if 'run_miner_only' in kwargs            : run_miner_only = kwargs.pop('run_miner_only')
        if 'cerocoin_network' in kwargs          : cerocoin_network = kwargs.pop('cerocoin_network')
        if 'modulus_size' in kwargs              : modulus_size = kwargs.pop('modulus_size')            
        if 'pub_exponent' in kwargs              : public_exponent = kwargs.pop('pub_exponent')            
        if 'starting_pow_difficulty' in kwargs   : starting_pow_difficulty = kwargs.pop('starting_pow_difficulty')
        if 'local_ip_address' in kwargs          : local_ip_address = kwargs.pop('local_ip_address')    
        if 'max_iterations_debug_mode' in kwargs : max_iterations_debug_mode = kwargs.pop('max_iterations_debug_mode')
        if 'num_transactions_in_block' in kwargs : num_transactions_in_block = kwargs.pop('num_transactions_in_block')
        if 'debug' in kwargs                     :     debug = kwargs.pop('debug')          
        self.local_ip_address                       =  local_ip_address
        self.run_miner_only                         =  run_miner_only 
        self.cerocoin_network                       =  cerocoin_network
        self.max_iterations_debug_mode              =  max_iterations_debug_mode if max_iterations_debug_mode else 200
        self.modulus_size                           =  modulus_size 
        self.prime_size                             =  modulus_size >> 1 if modulus_size else None
        self.p                                      =  None
        self.q                                      =  None
        self.modulus                                =  None
        self.pub_exponent                           =  pub_exponent if pub_exponent else 65537       
        self.priv_exponent                          =  None
        self.totient                                =  None
        self.pub_key                                =  None
        self.priv_key                               =  None
        self.pub_key_string                         =  None
        self.priv_key_string                        =  None
        self.ID                                     =  None
        self.pow_difficulty                         =  starting_pow_difficulty if starting_pow_difficulty else 251
        self.num_transactions_in_block              =  num_transactions_in_block
        self.transaction                            =  transaction
        self.prev_transaction                       =  None
        self.transactions_generated                 =  []
        self.transactions_received                  =  []
        self.num_transactions_sent                  =  0
        self.coins_acquired_from_others             =  []
        self.block                                  =  None
        self.prev_block                             =  None
        self.blockchain_length                      =  0
        self.coins_mined                            =  []
        self.coins_currently_owned_digitally_signed =  []
        self.nonce                                  =  None
        self.outgoing_client_sockets                =  []
        self.server_socket                          =  None
        self.server_port                            =  6404
        self.t_miner                                =  None
        self.miner_iteration_index                  =  0
        self.transactor_flag                        =  False
        self.blockmaker_flag                        =  False
        self.blockvalidator_flag                    =  False
        self.debug                                  =  debug

    #initialize
    def initialize_node_and_run(self):
        self.local_ip_address = self.find_local_ip_address()
        t_miner = None
        self.gen_rsa_primes(modulus_size = self.modulus_size)
        self.gen_private_exponent()
        self.gen_key_pair()
        self.write_key_pair_to_files()
        self.set_my_id()
        t_server =  ThreadedServer(self)
        t_server.daemon = True
        t_server.start()
        t_scanner = ThreadedScanner(self)
        t_scanner.daemon = True
        t_scanner.start()
        t_miner   = ThreadedMiner( self )
        t_transactor = ThreadedTransactor( self )
        t_blocks     = ThreadedBlockMaker( self )
        t_miner.daemon = True
        t_miner.start()
        t_transactor.daemon = True
        t_transactor.start()
        t_blocks.daemon = True
        t_blocks.start()
        self.t_miner = t_miner
        self.t_transactor = t_transactor
        while True: 
            time.sleep(1)
            
    def initialize_node_and_run_miner_only(self):
        print "\n\nInitializing the node and running only the miner"
        self.gen_rsa_primes(modulus_size = self.modulus_size)
        self.gen_private_exponent()
        self.gen_key_pair()
        self.write_key_pair_to_files()
        self.set_my_id()
        self.t_miner   = ThreadedMiner( self )
        self.t_miner.daemon = True
        self.t_miner.start()
        t_miner_supervisor = ThreadedMinerSupervisor( self )
        t_miner_supervisor.daemon = True
        t_miner_supervisor.start()
        while True: 
            time.sleep(1)

    def run_hasher(self, num_iterations):
        genesis_string = binascii.b2a_hex(os.urandom(64))
        for iter_index in range(num_iterations):
            nonce = binascii.b2a_hex(os.urandom(64))
            string_to_be_hashed = genesis_string + nonce
            hasher = SHA256.SHA256(message_in_ascii = string_to_be_hashed)
            hashval = hasher.sha256()  
            print "for try %d, hashval: %s" % (iter_index, hashval)
            if iter_index == 0:
                return string_to_be_hashed,hashval

    def find_local_ip_address(self):
        '''
        Finds the local IP address for the host on which the CeroCoin client is running. 
        The IPv4 address '8.8.8.8' that you see in the second statement shown below is for 
        the Google Public DNS. Using a connection with this DNS in order to figure out your 
        own IPv4 address is an idea I picked up at stackoverflow.com.
        '''
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        soc.connect(("8.8.8.8", 80))
        local_addr  = soc.getsockname()[0]
        print "\nlocal IPv4 address: ", local_addr
        soc.close()
        while True:
            ans = raw_input("\nIs %s for your local IPv4 address correct? Enter 'y' for 'yes' and 'n' for 'no': " % local_addr)
            ans = ans.strip()
            if ans == 'y' or ans == 'yes':
                return local_addr
            elif ans == 'n' or ans == 'no':
                while True:
                    ans = raw_input("\nEnter your local IPv4 address:  ")
                    try:
                        socket.inet_pton(socket.AF_INET, ans)
                        local_addr = ans                
                        break
                    except:
                        print "The IPv4 address you entered does not look right.  Try again."
                return local_addr
            else:
                print "\nYour answer can only be 'y' or 'n'.  Try again!"

    def minor_supervisor(self):
        print "\n\n=======STARTING A MINER SUPERVISOR THREAD======\n\n"
        while self.t_miner is None: time.sleep(2)
        while True:
            if  self.miner_iteration_index > 0 and self.miner_iteration_index % 30 == 0:
                print "\n\nMiner supervisor terminating the miner thread\n"
                while self.t_miner is None: time.sleep(2)             
                self.terminate_thread( self.t_miner )
                time.sleep(5)
                print "\n\n=======STARTING A NEW MINER THREAD======\n\n"
                self.t_miner = ThreadedMiner( self )
                self.t_miner.start()
            time.sleep(2)   

    def scan_the_network_for_cerocoin_nodes(self):
        ip_block_to_scan = self.cerocoin_network[:]
        try:
            del ip_block_to_scan[ip_block_to_scan.index(self.local_ip_address)]
        except:
            print "\nYour local IP address is not included in the list of network addresses supplied in your constructor call. !!!ABORTING!!!\n"
            os.kill( os.getpid(), signal.SIGKILL )                           
        print "\n Will scan the IP addresses: ", ip_block_to_scan
        remote_server_port = self.server_port
        max_num_of_tries_for_establishing_network = 3
        while True:
            if max_num_of_tries_for_establishing_network == 0:
                print "\n\nUnable to establish a network for CeroCoin demonstrations.  !!!ABORTING!!!\n\n"
                os.kill( os.getpid(), signal.SIGKILL )                                           
            for host in ip_block_to_scan:
                try:
                    print "\nTrying to connect with host %s\n" % host
                    sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )   
                    sock.settimeout(3)    
                    sock.connect( (host, remote_server_port) )                                 
                    sock.settimeout(None)      
                    print "\nDiscovering CeroCoinClient Nodes: -- Made connection with host: %s\n" % host
                    self.outgoing_client_sockets.append(sock)
                except:
                    print "        no connection possible with %s" % host
            if len(self.outgoing_client_sockets) == 1:
                print "\n\nWARNING: Only one other CeroCoin node found. Only trivial blockchain demo possible\n\n"
                break
            elif len(self.outgoing_client_sockets) == 0:
                max_num_of_tries_for_establishing_network -= 1
                print "\n\n\nNo CeroCoin clients found.  Will sleep for 5 sec and try again. (Max num of tries: 3)"
                time.sleep(5)
            else: 
                break
    #server
    def set_up_server(self):
        mdebug = True
        port = self.server_port
        try:
            if mdebug:
                print "\n\nWill set up a server on port %d\n\n" % port
            server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_sock.bind( ('', port) )        
            server_sock.listen(5)                 
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket = server_sock
            print "\n\nSUCCESSFULLY CREATED A SERVER SOCKET ON PORT %d\n\n" % port
        except socket.error, (value, message):       
            if server_sock:                         
                server_sock.close()                 
                print "\nCould not establish server socket: " + message  
                os.killpg(0, signal.SIGKILL)
        while True:       
            (client_sock, address) = server_sock.accept()                   
            print "\nConnection request from address: ", address
            t_connection = ThreadedClientConnection(self, client_sock, address)
            t_connection.daemon = True
            t_connection.start()

    #clientcon
    def client_connection(self, client_socket, ip_address):
        mdebug = False
        while True:                                               
            print "\nserver in interactive mode with client\n"
            client_line = ''                                   
            while 1:                                           
                client_byte = client_socket.recv(1)              
                if client_byte == '\n' or client_byte == '\r': 
                    break                                      
                else:                                          
                    client_line += client_byte                 
            if mdebug:
                print "\n::::::::::::::line received from remote: %s\n" % client_line
            if client_line == "Send pub key for a new transaction":
                if self.pub_key_string is None:
                    sys.exit("buyer ID not yet created")
                client_socket.send( "BUYER_PUB_KEY=" + ",".join(self.pub_key_string.split()) + "\n" )
            elif client_line.startswith("----CEROCOIN_TRANSACTION_BEGIN"):    
                print "\nTransaction received: %s\n" % client_line
                transaction_received = client_line
                print "\nValidating transaction\n"
                lock.acquire()
                if self.is_transaction_valid( transaction_received ):
                    self.prev_transaction = self.transaction
                    print "\n\nAdding new transaction to the list in 'self.transactions_received'\n"
                    self.transactions_received.append( transaction_received )
                    print "\n\nNumber of transactions in 'self.transactions_received': %d\n" % len(self.transactions_received)
                lock.release()
            elif client_line == "Sending new block":    
                client_socket.send("OK to new block\n")
            elif client_line.startswith("CEROCOIN_BLOCK_BEGIN"):
                self.blockvalidator_flag = True
                print "\n\nNew block received: %s\n" % client_line
                block_received = client_line
                if self.is_block_valid( block_received ):
                    print "\nreceived block validated\n"
                    lock.acquire()
                    (received_blockchain_len, received_block_pow_difficulty) = self.get_block_prop(block_received,
                                                                ('BLOCKCHAIN_LENGTH', 'POW_DIFFICULTY'))
                    received_blockchain_len = int(received_blockchain_len)
                    received_block_pow_difficulty = int(received_block_pow_difficulty)
                    print "\n========> received blockchain length:    ", received_blockchain_len
                    print "\n========> self.blockchain_length: ", self.blockchain_length
                    print "\n========> received_block_pow_difficulty: ", received_block_pow_difficulty
                    print "\n========> self.pow_difficulty: ", self.pow_difficulty
                    if self.block is None:
                        self.block = block_received
                        self.blockchain_length = received_blockchain_len
                        print "\n========> WILL ASK THE CURRENT MINER THREAD TO STOP\n"
                        self.terminate_thread( self.t_miner )
                        self.t_miner = None
                        time.sleep(2)
                        self.block = block_received
                        self.blockchain_length = received_blockchain_len                            
                        self.pow_difficulty = received_block_pow_difficulty
                        print "\n========> STARTING A NEW COIN MINER THREAD WITH POW DIFFICULTY OF %d AND BLOCKCHAIN LENGTH OF %d\n\n" % (self.pow_difficulty, self.blockchain_length)
                        self.t_miner = ThreadedMiner( self )
                        self.t_miner.daemon = True
                        self.t_miner.start()
                        time.sleep(5)
                        self.t_miner_changed = False
                    elif (received_blockchain_len > self.blockchain_length) and \
                                         (received_block_pow_difficulty <= self.pow_difficulty):
                        print "\n========> WILL ASK THE CURRENT MINER THREAD TO STOP\n"
                        self.terminate_thread( self.t_miner )
                        self.t_miner = None
                        time.sleep(2)
                        self.block = block_received
                        self.blockchain_length = received_blockchain_len                            
                        self.pow_difficuly = received_block_pow_difficulty
                        print "\n========> STARTING A NEW COIN MINER THREAD WITH POW DIFFICULTY OF %d AND BLOCKCHAIN LENGTH OF %d\n\n" % (self.pow_difficulty, self.blockchain_length)
                        self.t_miner = ThreadedMiner( self )
                        self.t_miner.daemon = True
                        self.t_miner.start()
                        time.sleep(5)
                        self.t_miner_changed = False
                    else:
                        print "\nNo reason to abandon the current miner thread\n" 
                    lock.release()
                else:
                    print "\n\nNOTICE: An illegal block received --- Ignoring the received block\n"
                self.blockvalidator_flag = False
            else:
                print "buyer:  We should not be here"

    def gen_rand_bits_with_set_bits(self, bitfield_size):               
        candidate = random.getrandbits( bitfield_size )      
        if candidate & 1 == 0: candidate += 1            
        candidate |= (1 << bitfield_size - 1)                  
        candidate |= (2 << bitfield_size - 3)                  
        return "%x" % candidate

    #prepare
    def prepare_new_transaction(self, coin, buyer_pub_key):
        '''
        Before the seller digitally signs the coin, it must include the buyer's public key.
        '''
        mdebug = False
        if mdebug:
            print "\n\nPrepareTranx::Buyer pub key:  %s\n" % buyer_pub_key
        new_tranx = CeroCoinTransaction( transaction_id       = self.gen_rand_bits_with_set_bits(32),
                                         coin                 = str(coin),
                                         seller_id            = self.ID,
                                         buyer_pub_key        = buyer_pub_key,
                                         seller_pub_key       = ",".join(self.pub_key_string.split()),
                                         pow_difficulty       = self.pow_difficulty,
                                         timestamp            = str(time.time()),
                                       )
        digitally_signed_tranx = self.digitally_sign_transaction(new_tranx)
        return digitally_signed_tranx

    #miner
    def mine_a_coin(self):
        mdebug = True
        if not self.run_miner_only:
            while len(self.outgoing_client_sockets) == 0: time.sleep(2)
        while True:
            while self.transactor_flag or self.blockmaker_flag or self.blockvalidator_flag: time.sleep(2)
            if self.num_transactions_sent >= 2:
                print "\n\nadditional sleep of 10 secs for the miner for the next round\n\n"
                time.sleep(10)
            time.sleep(2)
            hashval_int = 1 << 260
            iteration_control = 0
            genesis_string = string_to_be_hashed = None
            if self.block is None:
                print "\n\nFresh mining with a RANDOM genesis message string\n\n" 
                genesis_string = binascii.b2a_hex(os.urandom(64))
            else:
                print "\n\nUsing the new block for forming the genesis string\n\n"
                (transactions,prev_block_hash,timestamp) = self.get_block_prop(self.block, ('TRANSACTIONS',
                                                                                            'PREV_BLOCK_HASH',
                                                                                            'TIMESTAMP'))
                genesis_string = message_hash(transactions + prev_block_hash + timestamp)
            threadname = self.t_miner.getName()
            while  hashval_int > 1 << self.pow_difficulty:
                while self.transactor_flag or self.blockmaker_flag or self.blockvalidator_flag: time.sleep(2)
                time.sleep(1)
                iteration_control += 1
                self.miner_iteration_index += 1
                if iteration_control == self.max_iterations_debug_mode: 
                    sys.exit("max iterations for debugging reached - exiting")
                nonce = binascii.b2a_hex(os.urandom(64))
                string_to_be_hashed = genesis_string + nonce                
                hasher = SHA256.SHA256(message_in_ascii = string_to_be_hashed)
                hashval = hasher.sha256()  
                if len(hashval) < 64:
                    hashval = [0] * (64 - len(hashval)) + hashval
                print "%s -- Try %d at mining a new coin -- hashval: %s" % (threadname, iteration_control, hashval)
                hashval_int = int(hashval, 16)
            print "\n\n***SUCCESS***  -- A coin mined successfully with hashval %s\n" % hashval
            coin_id = self.gen_rand_bits_with_set_bits(32)
            while self.transactor_flag or self.blockmaker_flag or self.blockvalidator_flag: time.sleep(2)
            newcoin =  CeroCoin( coin_id                = coin_id,
                                 coin_miner             = self.ID,
                                 miner_pub_key          = ",".join(self.pub_key_string.split()),
                                 genesis_string         = genesis_string,
                                 nonce                  = nonce,
                                 pow_difficulty         = self.pow_difficulty,
                                 timestamp              = str(time.time()),
                                 hashval                = hashval,
                               )
            print "\n\nInside miner: new coin mined: %s\n\n" % str(newcoin)
            signed_newcoin = self.digitally_sign_coin(newcoin)
            while self.transactor_flag or self.blockmaker_flag or self.blockvalidator_flag: time.sleep(2)
            self.add_to_coins_owned_digitally_signed(signed_newcoin)

    def terminate_thread(self, thread):
        """
        Thread termination logic as suggested by Johan Dahlin at stackoverflow.com
        """
        if not thread.isAlive():
            return
        exc = ctypes.py_object(SystemExit)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread.ident), exc)
        if res == 0:
            raise ValueError("nonexistent thread id")
        elif res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")
        else:
            print ">>>>>>>>> CURRENT MINER THREAD TERMINATED SUCCESSFULLY <<<<<<<<<<<<" 

    #findbuyer #buyer #transactor
    def find_buyer_for_new_coin_and_make_a_transaction(self):
        '''
        We now look for a remote client with whom the new coin can be traded in the form of a
        transaction. The remote client must first send over its public key in order to construct
        the transaction.
        '''
        mdebug = False
        while len(self.outgoing_client_sockets) == 0: time.sleep(2)
        while len(self.coins_currently_owned_digitally_signed) == 0: time.sleep(2)
        time.sleep(4)
        while True:
            while len(self.coins_currently_owned_digitally_signed) == 0: time.sleep(2)
            while self.blockmaker_flag or self.blockvalidator_flag: time.sleep(2)
            self.transactor_flag = True
            print "\n\nLOOKING FOR A CLIENT FOR MAKING A TRANSACTION\n\n"
            coin = self.coins_currently_owned_digitally_signed.pop()
            if coin is not None: 
                print "\nNew outgoing coin:  ", coin
            buyer_sock = None
            new_transaction = None
            random.shuffle(self.outgoing_client_sockets)
            sock = self.outgoing_client_sockets[0]
            sock.send("Send pub key for a new transaction\n")
            try:
                while True: 
                    while self.blockmaker_flag or self.blockvalidator_flag: time.sleep(2)
                    message_line_from_remote = ""
                    while True:
                        byte_from_remote = sock.recv(1)               
                        if byte_from_remote == '\n' or byte_from_remote == '\r':   
                            break                                        
                        else:                                            
                            message_line_from_remote += byte_from_remote
                    if mdebug:
                        print "\n:::::::::::::message received from remote: %s\n" % message_line_from_remote
                    if message_line_from_remote == "Do you have a coin to sell?":
                        sock.send( "I do. If you want one, send public key.\n" )
                    elif message_line_from_remote.startswith("BUYER_PUB_KEY="):
                        while self.blockmaker_flag or self.blockvalidator_flag: time.sleep(2)
                        buyer_pub_key = message_line_from_remote
                        print "\nbuyer pub key: ", buyer_pub_key
                        new_transaction = self.prepare_new_transaction(coin, buyer_pub_key)
                        self.old_transaction = self.transaction
                        self.transaction = new_transaction
                        self.transactions_generated.append(new_transaction)
                        print "\n\nNumber of tranx in 'self.transactions_generated': %d\n" % \
                                                                        len(self.transactions_generated)
                        print "\n\nsending to buyer: %s\n"  % new_transaction
                        sock.send( str(new_transaction) + "\n" )
                        self.num_transactions_sent += 1
                        break
                    else:
                        print "seller side: we should not be here"
            except:
               print "\n\n>>>Seller to buyer: Could not maintain socket link with remote for %s\n" % str(socket)
            self.transactor_flag = False
            time.sleep(10)

    #blockmaker
    def construct_a_new_block_and_broadcast_the_block_to_cerocoin_network(self):
        '''
        We pack the newly generated transactions in a new block for broadcast to the network
        '''
        mdebug = False
        time.sleep(10)
        while len(self.transactions_generated) < self.num_transactions_in_block: time.sleep(2)
        while True:
            while len(self.transactions_generated) < self.num_transactions_in_block: time.sleep(2)
            self.blockmaker_flag = True
            print "\n\n\nPACKING THE ACCUMULATED TRANSACTIONS INTO A NEW BLOCK\n\n"
            current_block_hash = min_pow_difficulty = None
            if self.block is None:
                current_block_hash = self.gen_rand_bits_with_set_bits(256)
                min_pow_difficulty = self.pow_difficulty              
                self.blockchain_length = len(self.transactions_generated)
            else:
                current_block_hash = self.get_hash_of_block(self.block)       
                min_pow_difficulty = 0
                for tranx in self.transactions_generated:
                    tranx_pow = self.get_tranx_prop(self.block, 'POW_DIFFICULTY')
                    if tranx_pow  > min_pow_difficulty:
                        min_pow_difficulty = tranx_pow
                self.blockchain_length += len(self.transactions_generated)
            new_block = CeroCoinBlock( block_id            =  self.gen_rand_bits_with_set_bits(32),
                                       block_creator       =  self.ID,
                                       transactions        =  str(self.transactions_generated),
                                       pow_difficulty      =  min_pow_difficulty,
                                       prev_block_hash     =  current_block_hash,
                                       blockchain_length   =  self.blockchain_length,
                                       timestamp           =  str(time.time()),
                                     )
            self.transactions_generated = []
            new_block_with_signature = self.digitally_sign_block( str(new_block) )
            print "\n\n\nWILL BROADCAST THIS SIGNED BLOCK: %s\n\n\n" % new_block_with_signature
            self.block = new_block_with_signature
            for sock in self.outgoing_client_sockets:   
                sock.send("Sending new block\n")
                try:
                    while True: 
                        message_line_from_remote = ""
                        while True:
                            byte_from_remote = sock.recv(1)               
                            if byte_from_remote == '\n' or byte_from_remote == '\r':   
                                break                                        
                            else:                                            
                                message_line_from_remote += byte_from_remote
                        if mdebug:
                            print "\n::::::::::BLK: message received from remote: %s\n" % message_line_from_remote
                        if message_line_from_remote == "OK to new block":
                            sock.send( self.block + "\n" )
                            break
                        else:
                            print "sender side for block upload: we should not be here"
                except:
                    print "Block upload: Could not maintain socket link with remote for %s\n" % str(sockx)
            self.blockmaker_flag = False
            time.sleep(10)

    def get_hash_of_block(self, block):
        (transactions,prev_block_hash,timestamp) = self.get_block_prop(self.block, ('TRANSACTIONS',
                                                                                    'PREV_BLOCK_HASH',
                                                                                    'TIMESTAMP'))
        return message_hash(transactions + prev_block_hash + timestamp)

    #verifycoin
    def verify_coin(self, coin):
        '''
        This method verifies the signature on a coin for the buyer of the coin
        '''
        mdebug = True
        coin_splits = coin.split()
        miner_pub_key=pub_exponent=None
        for item in coin_splits:
            if item.startswith('MINER_PUB_KEY'):
                miner_pub_key = item[ item.index('=')+1 : ]
                break
        pubkey_splits = miner_pub_key.split(",")
        mod=e=None
        for item in pubkey_splits:
            if "=" in item:
                if item.startswith("mod"): mod = int(item[ item.index('=')+1 : ], 16)
                if item.startswith("e"):   e   = int(item[ item.index('=')+1 : ], 16)
        if mdebug:       
            print "\nVerifier: modulus: %d    public exponent: %d" % (mod, e)
        coin_without_signature, coin_signature_string = " ".join(coin_splits[1:-2]), coin_splits[-2]
        hasher = SHA256.SHA256(message = str(coin_without_signature))
        hashval = hasher.sha256()  
        hashval_int = int(hashval, 16)
        print "\nVerifier: coin hashval as int:  ", hashval_int
        coin_signature = int( coin_signature_string[ coin_signature_string.index('=')+1 : ], 16 )
        coin_checkval_int = modular_exp( coin_signature, e, mod )        
        print "\nVerifier: coin checkval as int: ", coin_checkval_int
        if hashval_int == coin_checkval_int: 
            print "\nVerifier: Since the coin hashval is equal to the coin checkval, the coin is authentic\n"
            return True
        else: 
            return False

    def add_to_coins_owned_digitally_signed(self, signed_coin):
        how_many_currently_owned = len(self.coins_currently_owned_digitally_signed)
        print "\n\nAdding the digitally signed new coin (#%d) to the 'currently owned and digitally signed' collection\n" % (how_many_currently_owned + 1)
        self.coins_currently_owned_digitally_signed.append(signed_coin)

    def add_to_coins_acquired_from_others(self, newcoin):
        how_many_previously_bought = len(self.coins_acquired_from_others)
        print "\nChecking authenticity of the coin"
        check = self.verify_coin(newcoin)
        if check is True:
            print "\nCoin is authentic"
        print "\nAdding the received coin (#%d) to the 'previously bought' collection\n" % (how_many_previously_bought + 1)
        self.coins_acquired_from_others.append(newcoin)

    def set_my_id(self):
        if self.pub_key_string is None or self.priv_key_string is None:
            sys.exit("set_my_id() can only be called after you have generated the public and private keys for your id") 
        hasher = SHA256.SHA256(message = self.pub_key_string)
        self.ID = hasher.sha256()  
        
    def gen_rsa_primes(self, modulus_size):
        assert modulus_size % 2 == 0, "The size of the modulus must be an even number" 
        generator = PrimeGenerator.PrimeGenerator( bits = self.prime_size )
        modulus=p=q=totient=None
        while True:
            p = generator.findPrime()
            q = generator.findPrime()
            if p != q and gcd(p - 1, self.pub_exponent) == 1 and gcd(q - 1, self.pub_exponent) == 1:
                modulus = p * q
                totient = (p-1) * (q-1)    
            if gcd(totient, self.pub_exponent) == 1:
                break
            else: next
        self.modulus,self.p,self.q,self.totient = modulus,p,q,totient
        return modulus, p, q, totient

    def gen_private_exponent(self):
        self.priv_exponent = MI(self.pub_exponent, self.totient)

    def gen_key_pair(self):
        p,q = self.p,self.q
        p_inv_mod_q = MI(p, q)
        q_inv_mod_p = MI(q, p)
        self.Xp  = q * q_inv_mod_p
        self.Xq  = p * p_inv_mod_q
        self.pub_key_string   = "CEROCOIN_PUBKEY mod=%x e=%x" % (self.modulus, self.pub_exponent)
        self.priv_key_string  = "CEROCOIN-PRIVKEY mod=%x e=%x d=%x p=%x q=%x totient=%x Xp=%x Xq=%x" %  \
                    (self.modulus,self.pub_exponent,self.priv_exponent,self.p,self.q,self.totient,self.Xp,self.Xq)

    def write_key_pair_to_files(self):
        if (self.pub_key_string is None) or (self.priv_key_string is None):
            sys.exit("you must first call gen_key_pair() before calling write_key_pair_to_files()")
        with open('CeroCoinClientKey_pub.txt', "w") as outfile:
            outfile.write(self.pub_key_string)
        with open('CeroCoinClientKey_priv.txt', "w") as outfile:
            outfile.write(self.priv_key_string)

    #digisigncoin
    def digitally_sign_coin(self, coin):
        mdebug = True
        modulus,e,d,p,q,Xp,Xq = self.modulus,self.pub_exponent,self.priv_exponent,self.p,self.q,self.Xp,self.Xq
        if mdebug:  
            print "\nDIGI_SIGN -- modulus: ", modulus
            print "\nDIGI_SIGN -- public exp: ", e
            print "\nDIGI_SIGN -- private exp: ", d
            print "\nDIGI_SIGN -- p: ", p
            print "\nDIGI_SIGN -- q: ", q
        splits = str(coin).split()
        coin_without_ends = " ".join(str(coin).split()[1:-1])
        hasher = SHA256.SHA256(message = str(coin_without_ends))
        hashval = hasher.sha256()  
        if mdebug:
            print "\nDIGI_SIGN: hashval for coin as int: ", int(hashval, 16)
        hashval_int = int(hashval, 16)
        Vp = modular_exp(hashval_int, d, p)
        Vq = modular_exp(hashval_int, d, q)
        coin_signature = (Vp * Xp) % modulus + (Vq * Xq) % modulus
        if mdebug:
            print "\nDIGI_SIGN: coin signature as int: ", coin_signature
        coin_signature_in_hex = "%x" % coin_signature
        coin_with_signature = self.insert_miner_signature_in_coin(str(coin), coin_signature_in_hex)
        checkval_int = modular_exp(coin_signature, e, modulus)
        if mdebug:
            print "\nDIGI_SIGN: coin hashval as int:   ", hashval_int
            print "\nDIGI_SIGN: coin checkval as int:  ", checkval_int
        assert hashval_int == checkval_int, "coin hashval does not agree with coin checkval"
        if mdebug:
            print "\nThe coin is authentic since its hashval is equal to its checkval"
        return coin_with_signature

    def insert_miner_signature_in_coin(self, coin, coin_signature_in_hex):
        return  'CEROCOIN_BEGIN ' + " ".join(coin.split()[1:-1]) + " MINER_SIGNATURE=" + coin_signature_in_hex  + ' CEROCOIN_END'

    #digisigntranx
    def digitally_sign_transaction(self, tranx):
        mdebug = False
        modulus,e,d,p,q,Xp,Xq = self.modulus,self.pub_exponent,self.priv_exponent,self.p,self.q,self.Xp,self.Xq
        tranx_without_ends = " ".join(str(tranx).split()[1:-1])
        hasher = SHA256.SHA256(message = tranx_without_ends)
        hashval = hasher.sha256()  
        if mdebug:
            print "\nTR: transaction hashval as int: ", int(hashval, 16)
        hashval_int = int(hashval, 16)
        Vp = modular_exp(hashval_int, d, p)
        Vq = modular_exp(hashval_int, d, q)
        tranx_signature = (Vp * Xp) % modulus + (Vq * Xq) % modulus
        if mdebug:
            print "\nTR: transaction signature as int: ", tranx_signature
        tranx_signature_in_hex = "%x" % tranx_signature
        tranx_with_signature = '----CEROCOIN_TRANSACTION_BEGIN ' + tranx_without_ends + " SELLER_TRANX_SIGNATURE=" + tranx_signature_in_hex + ' CEROCOIN_TRANSACTION_END----'
        checkval_int = modular_exp(tranx_signature, e, modulus)
        print "\nTR: Transaction hashval as int:   ", hashval_int
        print "\nTR: Transaction checkval as int:  ", checkval_int
        assert hashval_int == checkval_int, "tranx hashval does not agree with tranx checkval"
        print "\nTransaction is authenticated since its hashval is equal to its checkval"
        return tranx_with_signature

    #digisignblock
    def digitally_sign_block(self, block):
        '''
        Even though the method 'get_hash_of_block()' only hashes the transactions, prev_block hash,
        and the timestamp, we use the entire block, sans its two end delimiters, for the block 
        creator's digital signature.
        '''
        print "\n\nBlock creator putting digital signature on the block\n\n"
        mdebug = True
        modulus,e,d,p,q,Xp,Xq = self.modulus,self.pub_exponent,self.priv_exponent,self.p,self.q,self.Xp,self.Xq
        block_without_ends = " ".join(block.split()[1:-1])
        hasher = SHA256.SHA256(message = block_without_ends)
        hashval = hasher.sha256()  
        if mdebug:
            print "\nTR: hashval for block as int: ", int(hashval, 16)
        hashval_int = int(hashval, 16)
        Vp = modular_exp(hashval_int, d, p)
        Vq = modular_exp(hashval_int, d, q)
        block_signature = (Vp * Xp) % modulus + (Vq * Xq) % modulus
        if mdebug:
            print "\nTR: block signature as int: ", block_signature
        block_signature_in_hex = "%x" % block_signature
        block_with_signature = 'CEROCOIN_BLOCK_BEGIN ' + block_without_ends + " BLOCK_CREATOR_SIGNATURE=" + block_signature_in_hex + ' CEROCOIN_BLOCK_END'
        checkval_int = modular_exp(block_signature, e, modulus)
        if mdebug:
            print "\nTR: block hashval as int:   ", hashval_int
            print "\nTR: block checkval as int:  ", checkval_int
        assert hashval_int == checkval_int, "block hashval does not agree with block checkval"
        return block_with_signature

    #isvalid
    # Yet to be fully implemented.  At this time, the code shown is just a place holder
    def is_transaction_valid(self, transaction):
        splits = transaction.split()
        if not splits[0].startswith('----CEROCOIN_TRANSACTION_BEGIN'):
            return False
        for item in splits[1:]:
            if item not in ['CEROCOIN_BEGIN','CEROCOIN_END','----CEROCOIN_TRANSACTION_BEGIN','CEROCOIN_TRANSACTION_END----','BLOCK_BEGIN','BLOCK_END'] and '=' not in item:
                return False
        return True    

    #isvalid
    # Yet to be fully implemented.  At this time, the code shown is just a place holder
    def is_block_valid(self, block):
        splits = block.split()
        if not splits[0].startswith('CEROCOIN_BLOCK_BEGIN'):
            return False
        for item in splits[1:]:
#            print "\nitem in validating block: ", item
            if (item not in ['CEROCOIN_BEGIN','CEROCOIN_END','----CEROCOIN_TRANSACTION_BEGIN','CEROCOIN_TRANSACTION_END----','CEROCOIN_BLOCK_BEGIN','CEROCOIN_BLOCK_END']) and ('=' not in item):
                return False
        return True    

    #getter
    def get_coin_prop(self, coin, prop):
        splits = coin.split()
        for item in splits:
            if '=' in item:
                if item[:item.index('=')] == prop:
                    return item[item.index('=')+1:]
    #getter
    def get_tranx_prop(self, transaction, prop):
        splits = transaction.split()
        for item in splits:
            if '=' in item:
                if item[:item.index('=')] == prop:
                    return item[item.index('=')+1:]

    #getter
    def get_block_prop(self, block, prop):
        '''
        When 'prop' is a scalar for an attribute name in a block, it returns the value associated
        with that attribute.  On the other hand, when 'prop' is a tuple of attribute names, it
        returns a list of the corresponding attribute values.
        '''
        splits = block.split()
        if isinstance(prop, (tuple)):
            answer_dict = {prop[i] : None for i in range(len(prop))}
            for item in splits:
                if '=' in item:                
                    if item[:item.index('=')] in prop:
                        answer_dict[item[:item.index('=')]] = item[item.index('=')+1:]
            return [answer_dict[item] for item in prop] 
        else:
            for item in splits:
                if '=' in item:
                    if item[:item.index('=')] == prop:
                        return item[item.index('=')+1:]


#threaded
############################################  Multithreaded Classes  #############################################

class ThreadedServer( threading.Thread ):
    def __init__(self, network_node):
        self.network_node = network_node
        threading.Thread.__init__(self)
    def run(self):
        self.network_node.set_up_server()

class ThreadedScanner( threading.Thread ):
    def __init__(self, network_node):
        self.network_node = network_node
        threading.Thread.__init__(self)
    def run(self):
        self.network_node.scan_the_network_for_cerocoin_nodes()    

class ThreadedMiner( threading.Thread ):
    def __init__(self, network_node):
        self.network_node = network_node
        threading.Thread.__init__(self)
    def run(self):
        self.network_node.mine_a_coin()

class ThreadedTransactor( threading.Thread ):
    def __init__(self, network_node):
        self.network_node = network_node
        threading.Thread.__init__(self)
    def run(self):
        self.network_node.find_buyer_for_new_coin_and_make_a_transaction()

class ThreadedBlockMaker( threading.Thread ):
    def __init__(self, network_node):
        self.network_node = network_node
        threading.Thread.__init__(self)
    def run(self):
        self.network_node.construct_a_new_block_and_broadcast_the_block_to_cerocoin_network()

class ThreadedClientConnection( threading.Thread ):
    def __init__(self, network_node, client_socket, client_ip_address):
        self.network_node = network_node
        self.client_socket = client_socket
        self.client_ip_address = client_ip_address
        threading.Thread.__init__(self)
    def run(self):
        self.network_node.client_connection(self.client_socket, self.client_ip_address)

class ThreadedMinerSupervisor( threading.Thread ):
    def __init__(self, network_node):
        self.network_node = network_node
        threading.Thread.__init__(self)
    def run(self):
        self.network_node.minor_supervisor()

################################################  class CeroCoin  #################################################
class CeroCoin:                                     
    def __init__( self, **kwargs ):                                     
        coin_id=coin_miner=miner_pub_key=genesis_string=pow_difficulty=hashval=nonce=timestamp=debug=None    
        if 'coin_id' in kwargs              :        coin_id = kwargs.pop('coin_id')
        if 'coin_miner' in kwargs           :        coin_miner = kwargs.pop('coin_miner')
        if 'miner_pub_key' in kwargs        :        miner_pub_key = kwargs.pop('miner_pub_key')
        if 'genesis_string' in kwargs       :        genesis_string = kwargs.pop('genesis_string')
        if 'pow_difficulty' in kwargs       :        pow_difficulty = kwargs.pop('pow_difficulty')
        if 'nonce' in kwargs                :        nonce = kwargs.pop('nonce')        
        if 'timestamp' in kwargs            :        timestamp = kwargs.pop('timestamp')        
        if 'hashval' in kwargs              :        hashval = kwargs.pop('hashval')
        if 'debug' in kwargs                :        debug = kwargs.pop('debug')
        self.coin_id = coin_id if coin_id else sys.exit("A coin MUST have a 32-bit ID")
        self.coin_miner = coin_miner if coin_miner else sys.exit("A coin MUST have the miner associated with it")
        self.miner_pub_key = miner_pub_key
        self.nonce = nonce
        self.genesis_string = genesis_string if genesis_string else None
        self.hashval  =  hashval if hashval else None
        self.pow_difficulty = pow_difficulty
        self.timestamp  = timestamp 
        self.coin_signature = None

    def __str__(self):
        'To create a string representation of a coin'
        return " ".join(['CEROCOIN_BEGIN',
                         'COIN_ID='+self.coin_id, 
                         'COIN_MINER='+self.coin_miner, 
                         'MINER_PUB_KEY='+self.miner_pub_key,
                         'GENESIS_STRING='+self.genesis_string,
                         'NONCE='+self.nonce, 
                         'POW_DIFFICULTY='+str(self.pow_difficulty),
                         'TIMESTAMP='+self.timestamp, 
                         'HASHVAL='+self.hashval,
                         'CEROCOIN_END'
                       ])

##########################################  class CeroCoinTransaction  ############################################

class CeroCoinTransaction:                                     
    def __init__( self, **kwargs ):                                     
        transaction_id=coin=seller_id=buyer_id=transaction=prev_transaction=nonce=pow_difficulty=None
        timestamp=debug=None    
        if 'transaction_id' in kwargs          :        transaction_id = kwargs.pop('transaction_id')
        if 'coin' in kwargs                    :        coin = kwargs.pop('coin')
        if 'seller_id' in kwargs               :        seller_id = kwargs.pop('seller_id')
        if 'seller_pub_key' in kwargs          :        seller_pub_key = kwargs.pop('seller_pub_key')
        if 'buyer_pub_key' in kwargs           :        buyer_pub_key = kwargs.pop('buyer_pub_key')
        if 'pow_difficulty' in kwargs          :        pow_difficulty = kwargs.pop('pow_difficulty')
        if 'timestamp' in kwargs               :        timestamp = kwargs.pop('timestamp')
        if 'debug' in kwargs                   :        debug = kwargs.pop('debug')
        self.transaction_id = transaction_id
        self.coin = coin
        self.seller_id = seller_id
        self.seller_pub_key = seller_pub_key
        self.buyer_id = buyer_id
        self.buyer_pub_key = buyer_pub_key
        self.timestamp = timestamp

    def get_pow_difficulty_level( self ):
        return self.pow_difficulty

    def __str__(self):
        'To create a string representation of a transaction'
        return " ".join(['----CEROCOIN_TRANSACTION_BEGIN', 
                         'TRANSACTION_ID='+self.transaction_id, 
                         self.coin,
                         'SELLER='+self.seller_id, 
                         'SELLER_PUB_KEY='+self.seller_pub_key, 
                         'BUYER_PUB_KEY='+self.seller_pub_key, 
                         'TIMESTAMP='+self.timestamp, 
                         'CEROCOIN_TRANSACTION_END----' 
                        ])

#############################################  class CeroCoinBlock  ###############################################
#block
class CeroCoinBlock:                                     
    def __init__( self, **kwargs ):                                     
        block_id=block_creator=transactions=pow_difficulty=prev_block_hash=timestamp=None
        blockchain_length=debug=None    
        if 'block_id' in kwargs          :        block_id = kwargs.pop('block_id')
        if 'block_creator' in kwargs     :        block_creator = kwargs.pop('block_creator')
        if 'transactions' in kwargs      :        transactions = kwargs.pop('transactions')
        if 'pow_difficulty' in kwargs    :        pow_difficulty = kwargs.pop('pow_difficulty')       
        if 'prev_block_hash' in kwargs   :        prev_block_hash = kwargs.pop('prev_block_hash')
        if 'blockchain_length' in kwargs :        blockchain_length = kwargs.pop('blockchain_length') 
        if 'timestamp' in kwargs         :        timestamp = kwargs.pop('timestamp')        
        if 'debug' in kwargs             :        debug = kwargs.pop('debug')
        self.block_id = block_id
        self.block_creator = block_creator if block_creator else sys.exit("A block MUST have the creator associated with it")
        self.transactions = transactions
        self.pow_difficulty = pow_difficulty
        self.prev_block_hash = prev_block_hash
        self.blockchain_length = blockchain_length
        self.timestamp  = timestamp 

    def __str__(self):
        'To create a string representation of a block'
        transactions = str(self.transactions)
#        transactions = transactions.replace(' ', '')
        transactions = transactions.replace(' ', ':')
        return " ".join(['CEROCOIN_BLOCK_BEGIN', 
                         'BLOCK_ID='+self.block_id, 
                         'BLOCK_CREATOR='+self.block_creator, 
                         'TRANSACTIONS='+transactions, 
                         'POW_DIFFICULTY='+str(self.pow_difficulty),
                         'PREV_BLOCK_HASH='+self.prev_block_hash, 
                         'BLOCKCHAIN_LENGTH='+str(self.blockchain_length), 
                         'TIMESTAMP='+self.timestamp, 
                         'CEROCOIN_BLOCK_END'
                        ])

