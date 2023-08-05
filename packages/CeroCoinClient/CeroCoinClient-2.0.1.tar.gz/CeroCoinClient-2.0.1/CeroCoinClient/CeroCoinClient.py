__version__ = '2.0.1'
__author__  = "Avinash Kak (kak@purdue.edu)"
__date__    = '2018-March-24'
__url__     = 'https://engineering.purdue.edu/kak/distCeroCoin/CeroCoinClient-2.0.1.html'
__copyright__ = "(C) 2018 Avinash Kak. Python Software Foundation."


__doc__ = '''

CeroCoinClient.py

Version: ''' + __version__ + '''

Author: Avinash Kak (kak@purdue.edu)

Date: ''' + __date__ + '''

@tag_changes
CHANGES:

  Version 2.0.1:

    This is a Python 3.x compliant version of the CeroCoinClient module.  This
    version should work with both Python 2.x and Python 3.x

  Version 1.9.1:

    I have enhanced and cleaned up the documentation in this version.  The module
    implementation code remains unchanged.

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
        construct_and_run_client_node.py
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
    transactions is received from the network if the received block has a
    blockchain length that is longer than what is being used in the current
    search, or, for a given blockchain length, if the received block has a PoW
    difficultly level that is higher than what is being used in the current
    search.

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


@tag_otherthreads
THE OTHER THREADS:

    As mentioned earlier, the other threads spawned by CeroCoinClient include a
    server thread, which is an instance of the class ThreadedServer, that
    monitors the server port 6404 for incoming connection requests from the
    other clients in a network.  When this thread accepts a connection, it
    spawns a thread of type ThreadedClientConnection for maintaining on a
    continuing basis the connection with the client.  

    Each client also spawns a thread of type ThreadedScanner for scanning the
    network formed by the IP addresses supplied to the CeroCoinClient class
    through its constructor parameter cerocoin_network.  By scanning the
    network, I mean sending a client socket request to the server socket at a
    remote host.  I must add that the logic currently programmed in
    CeroCoinClient for forming a network of clients is much too rudimentary to
    require a separate thread of its own.  However, I foresee using Distributed
    Hash Tables (DHT) to make this logic more sophisticated in a future version
    of the module in order to create a truly distributed peer-to-peer (P2P)
    network from all the CeroCoin clients. This would be along the lines
    presented in the P2P lecture at:

      https://engineering.purdue.edu/kak/compsec/NewLectures/Lecture25.pdf
    

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
    to use in your demo.  Let's say you create a demo at home involving two or
    three laptops, with all the laptops connected through your smartphone based
    WiFi hotspot.  The first time you do this, you will have to manually enter
    the IP addresses of the different laptops (as assigned by the smartphone
    WiFi hotspot) in the value of the CeroCoinClient constructor parameter
    cerocoin_network.  Subsequently, if you use the same WiFi hotspot in your
    classroom for networking the demo laptops, you won't have to change a thing
    in the IP addresses previously entered in the CeroCoinClient constructor
    call.  This works because when connecting with a WiFi access point a digital
    device's first preference is to ask for the same IP address as it had the
    last time.  If that address was assigned to some other client in the
    meantime, your laptop would then obviously get a different IP address.  So
    just make sure that you connect your demo laptops to your smartphone AP
    before you invite any of your students to join in through their own digital
    devices.


@tag_whatsortofdemo
WHAT SORT OF A DEMO YOU CAN EXPECT TO SEE WITH CeroCoinClient:

    I am going to show below the sort of output you will see on the terminal
    screen of one of the laptops in a 2-laptop demonstration of CeroCoinClient
    For this demo, I have intentionally biased one of the laptops (Client1) with
    a lower PoW challenge so that it would produce coins at a reasonably high
    rate for the demonstration and the other laptop (Client2) at a relative high
    PoW so that initially it would be primarily the receiver of transactions.

    This initial disparity between Client1 and Client2 only lasts until Client2
    receives a block from Client1. Subsequently, Client2 automatically adjusts
    its PoW in order to be consistent with Client1.

    Subsequently, Client1 and Client2 compete on an equal basis.  Both clients
    abandon their ongoing searches when they receive a block from the other
    client that contains a longer blockchain length.

    In the demo shown, Client1 is asked to blocks with two transactions at a
    time, whereas Client2 is asked to make blocks with four transactions at a
    time.  This causes Client2 to take much longer to send a block to Client1
    than it takes Client1 to send a block of Client2.  

    I stop the demo when Client2 its longer block to Client1 and the latter
    client abandons its ongoing search for a new coin and starts a new search
    with a new set of parameters.


@begincode

@tag3
Client1 setting up the server and scanning the network for discovering other CeroCoin clients:

    local IPv4 address:  192.168.43.12
    
    Is 192.168.43.12 for your local IPv4 address correct? Enter 'y' for 'yes' and 'n' for 'no': y
    
    
    Will set up a server on port 6404
    
    
    SUCCESSFULLY CREATED A SERVER SOCKET ON PORT 6404
    
    
    Will scan the IP addresses:  ['192.168.43.181','192.168.43.41','192.168.43.244']
    
    Connection request from address:  ('192.168.43.244', 53674)
    
    server in interactive mode with client
    
    Trying to connect with host 192.168.43.181
    
            no connection possible with 192.168.43.181
    
    Trying to connect with host 192.168.43.41
    
            no connection possible with 192.168.43.41
    
    Trying to connect with host 192.168.43.244
    
    
    Discovering CeroCoinClient Nodes: -- Made connection with host: 192.168.43.244
    
@tag3
Client1 issues a warning if only one other client discovered:    
    
    WARNING: Only one other CeroCoin node found -- only the simplest of blockchain demos possible.
    
@tag3
Client1 starts mining:
    
    Fresh mining with a RANDOM genesis message string
    
    Thread-3 -- Try 1 at mining a new coin -- hashval: 8b023360fa502f8d0241abc48985ce5f69524de3c527ece2a1411edc70252356
    Thread-3 -- Try 2 at mining a new coin -- hashval: 5b0239b47408f8f45a5843c668ceb5834458744ec04522851e1639501f1958ba
    Thread-3 -- Try 3 at mining a new coin -- hashval: 0b15a12712f3f560e3e1a7cf00c74db2074dcdbfcdb6796fe3f695721d5b3799
    Thread-3 -- Try 4 at mining a new coin -- hashval: b1a41d90d4f2004c9f3619ee94cb231b7f9fe0f4dc8644f4495505a30aa0cb57
    Thread-3 -- Try 5 at mining a new coin -- hashval: bb0553a091e22c62675f64f470322663772b3eb11af5946bf04f0652bba0fb11
    
                                      ...
                                      ...
                                      ...
@tag3
Client1 discovers a new coin:
    
    ***SUCCESS***  -- A coin mined successfully with hashval 021708d6931d7b78ba78638b7c075679f733ac214882e24929d7f4819a99ea8e
    
    Inside miner: new coin mined: CEROCOIN_BEGIN COIN_ID=f91fcad7 COIN_MINER=8f315bb06cdd1c9b43e40d672f001a036fa9bf8ca
    0d88caa2cf6ec55b0ef682b MINER_PUB_KEY=CEROCOIN_PUBKEY,mod=bb03dee9147ecd6fcd65a6363628ae2420df42c01456b01a82d99eaf
    fdff029c1f76b30d1f410d028f948943e079e7690d7748cc236927d4df5b9e7c5222b8f9,e=10001 GENESIS_STRING=a11c3ac52b3c7a707e
    fad42b73b3e8fc68251ec4d2d2bbf42559363a672473244acc462b55f6442d9dd4873812a19ea4eda8399cd928232f2900556a18ad43ed NONCE
    =500f663ffb4e21000ddcc15e2e675db30523751b5b5d702cca10e14330cb6afb9d9fbc72bf324b75f4cdfe1fb47e78cff98896743fbf5843ad9
    f8df42a711d97 POW_DIFFICULTY=251 TIMESTAMP=1521659246.51 HASHVAL=021708d6931d7b78ba78638b7c075679f733ac214882e24929d
    7f4819a99ea8e CEROCOIN_END

@tag3
Client1 digitally signs the new coin:    
    
    DIGI_SIGN -- modulus:  979477660239518751196079239023400242129593686837226913277379224155811959573786658843789928
    5892764768773669595118563503158067765676545384871750925608466681
    
    DIGI_SIGN -- public exp:  65537
    
    DIGI_SIGN -- private exp:  623717002529499916744220438563919042751336395208477513035458857770335848587698736122630
    7777289646561155879429639119022107111582097030066568107748704560273
    
    DIGI_SIGN -- p:  102519358551241811495729724167444751109116912078693483765220449427883705379421
    
    DIGI_SIGN -- q:  95540751920521491674073950590733017660617481851057770307313856246375311882061
    
    DIGI_SIGN: hashval for coin as int:  86510437510980512407724286836130353097172028531149971985244332448617114765542
    
    DIGI_SIGN: coin signature as int:  3034287323255125514963426603882014706493101715032145041466955138696659312386417
    331192659711922521139809585876154377453866492931453312806246199515640150475
    
    DIGI_SIGN: coin hashval as int:    86510437510980512407724286836130353097172028531149971985244332448617114765542
    
    DIGI_SIGN: coin checkval as int:   86510437510980512407724286836130353097172028531149971985244332448617114765542
    
    The coin is authentic since its hashval is equal to its checkval
    
    
    Adding the digitally signed new coin (#1) to the 'currently owned and digitally signed' collection
    
    LOOKING FOR A CLIENT FOR MAKING A TRANSACTION
    
    New outgoing coin:   CEROCOIN_BEGIN COIN_ID=f91fcad7 COIN_MINER=8f315bb06cdd1c9b43e40d672f001a036fa9bf8ca0d88ca
    a2cf6ec55b0ef682b MINER_PUB_KEY=CEROCOIN_PUBKEY,mod=bb03dee9147ecd6fcd65a6363628ae2420df42c01456b01a82d99eaffdf
    f029c1f76b30d1f410d028f948943e079e7690d7748cc236927d4df5b9e7c5222b8f9,e=10001 GENESIS_STRING=a11c3ac52b3c7a707e
    fad42b73b3e8fc68251ec4d2d2bbf42559363a672473244acc462b55f6442d9dd4873812a19ea4eda8399cd928232f2900556a18ad43ed 
    NONCE=500f663ffb4e21000ddcc15e2e675db30523751b5b5d702cca10e14330cb6afb9d9fbc72bf324b75f4cdfe1fb47e78cff9889674
    3fbf5843ad9f8df42a711d97 POW_DIFFICULTY=251 TIMESTAMP=1521659246.51 HASHVAL=021708d6931d7b78ba78638b7c075679f73
    3ac214882e24929d7f4819a99ea8e MINER_SIGNATURE=39ef4998ee4892b2c93ac2dec26fd9fe5cd39a2b89130b2a44680eef67498a162
    330ec5b451019612ed251885565bd276fa0274a342610dfa6c465c4a672b9cb CEROCOIN_END

@tag3
Client1 scans the network for a client that wants to acquire the new coin:
    
    buyer pub key:  BUYER_PUB_KEY=CEROCOIN_PUBKEY,mod=bf6500d1437d9a6b5e8bc72cebc81f3ef4053f33de4c45efbb97ef32e34e
    9dd331d2239fff94c8e398e381fd4bd7606c723eb6416a98457fb8b4845a9175a319,e=10001
    
    TR: Transaction hashval as int:    26737969326165058000181407006099711277778763790219152843879665597323012105629
    
    TR: Transaction checkval as int:   26737969326165058000181407006099711277778763790219152843879665597323012105629
    
    Transaction is authenticated since its hashval is equal to its checkval
    
    Number of tranx in 'self.transactions_generated': 1
    
    sending to buyer: ----CEROCOIN_TRANSACTION_BEGIN TRANSACTION_ID=fec4d031 CEROCOIN_BEGIN COIN_ID=f91fcad7 
    COIN_MINER=8f315bb06cdd1c9b43e40d672f001a036fa9bf8ca0d88caa2cf6ec55b0ef682b MINER_PUB_KEY=CEROCOIN_PUBKEY,
    mod=bb03dee9147ecd6fcd65a6363628ae2420df42c01456b01a82d99eaffdff029c1f76b30d1f410d028f948943e079e7690d7748cc
    236927d4df5b9e7c5222b8f9,e=10001 GENESIS_STRING=a11c3ac52b3c7a707efad42b73b3e8fc68251ec4d2d2bbf42559363a6724
    73244acc462b55f6442d9dd4873812a19ea4eda8399cd928232f2900556a18ad43ed NONCE=500f663ffb4e21000ddcc15e2e675db30
    523751b5b5d702cca10e14330cb6afb9d9fbc72bf324b75f4cdfe1fb47e78cff98896743fbf5843ad9f8df42a711d97 POW_DIFFICULTY
    =251 TIMESTAMP=1521659246.51 HASHVAL=021708d6931d7b78ba78638b7c075679f733ac214882e24929d7f4819a99ea8e 
    MINER_SIGNATURE=39ef4998ee4892b2c93ac2dec26fd9fe5cd39a2b89130b2a44680eef67498a162330ec5b451019612ed251885565bd
    276fa0274a342610dfa6c465c4a672b9cb CEROCOIN_END SELLER=8f315bb06cdd1c9b43e40d672f001a036fa9bf8ca0d88caa2cf6ec
    55b0ef682b SELLER_PUB_KEY=CEROCOIN_PUBKEY,mod=bb03dee9147ecd6fcd65a6363628ae2420df42c01456b01a82d99eaffdff029c
    1f76b30d1f410d028f948943e079e7690d7748cc236927d4df5b9e7c5222b8f9,e=10001 BUYER_PUB_KEY=CEROCOIN_PUBKEY,mod=bb0
    3dee9147ecd6fcd65a6363628ae2420df42c01456b01a82d99eaffdff029c1f76b30d1f410d028f948943e079e7690d7748cc236927d4d
    f5b9e7c5222b8f9,e=10001 TIMESTAMP=1521659253.75 SELLER_TRANX_SIGNATURE=130f985d89c5d43dd2c971149775fd0d2277df4
    d118fa5a18809ac5207b46508f573c073ebdc84874f512cb2ea63d007ac18f5fe3590179efaa9808e9e8a413e0 
    CEROCOIN_TRANSACTION_END----

@tag3
Client1 is continuing the search for a new coin in its miner thread:
    
    Fresh mining with a RANDOM genesis message string
    
    Thread-3 -- Try 1 at mining a new coin -- hashval: f00ec92a22187f46884db4603965e3cfe35f7f73c87ab9b911e94df99f69473c
    Thread-3 -- Try 2 at mining a new coin -- hashval: 4d900ccf482a6c2809e2898f3892d299656c7426662e142e2de0dd5d5e294bc8
    Thread-3 -- Try 3 at mining a new coin -- hashval: c2a808ac8f79c4f1530105932c46586c44dc139cafdd966980815036ef37a900
    Thread-3 -- Try 4 at mining a new coin -- hashval: 68f8e33f0fe1c13d3a4ef56b5354382ecc2d0352e4369a6c2dc3a8d3b7328316
    Thread-3 -- Try 5 at mining a new coin -- hashval: 2ae8f6cf391f7b767b93cab65d86bb7ffc0623b6e9f9bd2783ac9f54408a8796
    Thread-3 -- Try 6 at mining a new coin -- hashval: 13e4478e12dc8d95213f554611d875e0994b0d41f156450900369201ac986862
                                                     ...
                                                     ...
                                                     ...
@tag3
Client1 discovers another coin:

    ***SUCCESS***  -- A coin mined successfully with hashval 02263d99f16f80da665663bb47e1cb664a980401a1d8efcd7dff46c09cce9367
    
    Inside miner: new coin mined: CEROCOIN_BEGIN COIN_ID=f4e1b5bf COIN_MINER=8f315bb06cdd1c9b43e40d672f001a036fa9bf8c
    a0d88caa2cf6ec55b0ef682b MINER_PUB_KEY=CEROCOIN_PUBKEY,mod=bb03dee9147ecd6fcd65a6363628ae2420df42c01456b01a82d99
    eaffdff029c1f76b30d1f410d028f948943e079e7690d7748cc236927d4df5b9e7c5222b8f9,e=10001 GENESIS_STRING=f5849857662e
    800df9600edecf84779ded0b91ad8877b99f7b3dd0da8fca9154c4c1c8ddbcb3395c133ef3c1ff31018d78f0f7a2053283403ffbbd1390
    3c85a1 NONCE=b2f4e377302b23271998bd6102a0b9802af7c57087018add00a4131e893e57b986775841c156ef6c388f2f39a07d081aff4
    d3083c184189e53043b039dccc942 POW_DIFFICULTY=251 TIMESTAMP=1521659272.15 HASHVAL=02263d99f16f80da665663bb47e1cb6
    64a980401a1d8efcd7dff46c09cce9367 CEROCOIN_END

@tag3
Client1 digitally signs the new coin:
    
    DIGI_SIGN -- modulus:  979477660239518751196079239023400242129593686837226913277379224
                               1558119595737866588437899285892764768773669595118563503158067765676545384871750925608466681
    
    DIGI_SIGN -- public exp:  65537
    
    DIGI_SIGN -- private exp:  62371700252949991674422043856391904275133639520847751303545
                           88577703358485876987361226307777289646561155879429639119022107111582097030066568107748704560273
    
    DIGI_SIGN -- p:  102519358551241811495729724167444751109116912078693483765220449427883705379421
    
    DIGI_SIGN -- q:  95540751920521491674073950590733017660617481851057770307313856246375311882061
    
    DIGI_SIGN: hashval for coin as int:  76514153981570775749716477771968396248887816319195349155147223699526208275377
    
    DIGI_SIGN: coin signature as int:  343603520296132174961536763080693984406914113835905398622829461208594254312782104
                                                 7247423984450190897882800780902696360164913108873934538812498079048126382
    
    DIGI_SIGN: coin hashval as int:    76514153981570775749716477771968396248887816319195349155147223699526208275377
    
    DIGI_SIGN: coin checkval as int:   76514153981570775749716477771968396248887816319195349155147223699526208275377
    
    The coin is authentic since its hashval is equal to its checkval
    
    
    Adding the digitally signed new coin (#1) to the 'currently owned and digitally signed' collection
    
    LOOKING FOR A CLIENT FOR MAKING A TRANSACTION
    
    New outgoing coin:   CEROCOIN_BEGIN COIN_ID=f4e1b5bf COIN_MINER=8f315bb06cdd1c9b43e40d672f001a036fa9bf8ca0d88caa
    2cf6ec55b0ef682b MINER_PUB_KEY=CEROCOIN_PUBKEY,mod=bb03dee9147ecd6fcd65a6363628ae2420df42c01456b01a82d99eaffdff0
    29c1f76b30d1f410d028f948943e079e7690d7748cc236927d4df5b9e7c5222b8f9,e=10001 GENESIS_STRING=f5849857662e800df9600
    edecf84779ded0b91ad8877b99f7b3dd0da8fca9154c4c1c8ddbcb3395c133ef3c1ff31018d78f0f7a2053283403ffbbd13903c85a1 
    NONCE=b2f4e377302b23271998bd6102a0b9802af7c57087018add00a4131e893e57b986775841c156ef6c388f2f39a07d081aff4d3083c
    184189e53043b039dccc942 POW_DIFFICULTY=251 TIMESTAMP=1521659272.15 HASHVAL=02263d99f16f80da665663bb47e1cb664a98
    0401a1d8efcd7dff46c09cce9367 MINER_SIGNATURE=419afd7f16a58cc0c3f62073ef6c2d5092dfd7650bfc75cbb323ce5790038dbbfbde
    04a8b3fd2c53494546b13929b4398b7395c3bbbd4cd7b62bfd8ce341cfae CEROCOIN_END

@tag3
Client1 scans the network for a client that wants to acquire the new coin:
    
    buyer pub key:  BUYER_PUB_KEY=CEROCOIN_PUBKEY,mod=bf6500d1437d9a6b5e8bc72cebc81f3ef4053f33de4c45efbb97ef32e34e9
    dd331d2239fff94c8e398e381fd4bd7606c723eb6416a98457fb8b4845a9175a319,e=10001
    
    TR: Transaction hashval as int:    95141149468134874583798512150534070228703333925502196698269811543349137467467
    
    TR: Transaction checkval as int:   95141149468134874583798512150534070228703333925502196698269811543349137467467
    
    Transaction is authenticated since its hashval is equal to its checkval
    
    Number of tranx in 'self.transactions_generated': 2
    
    sending to buyer: ----CEROCOIN_TRANSACTION_BEGIN TRANSACTION_ID=c8a81d3d CEROCOIN_BEGIN COIN_ID=f4e1b5bf 
    COIN_MINER=8f315bb06cdd1c9b43e40d672f001a036fa9bf8ca0d88caa2cf6ec55b0ef682b MINER_PUB_KEY=CEROCOIN_PUBKEY,
    mod=bb03dee9147ecd6fcd65a6363628ae2420df42c01456b01a82d99eaffdff029c1f76b30d1f410d028f948943e079e7690d7748cc2369
    27d4df5b9e7c5222b8f9,e=10001 GENESIS_STRING=f5849857662e800df9600edecf84779ded0b91ad8877b99f7b3dd0da8fca9154c4c1
    c8ddbcb3395c133ef3c1ff31018d78f0f7a2053283403ffbbd13903c85a1 NONCE=b2f4e377302b23271998bd6102a0b9802af7c57087018
    add00a4131e893e57b986775841c156ef6c388f2f39a07d081aff4d3083c184189e53043b039dccc942 POW_DIFFICULTY=251 TIMESTAMP
    =1521659272.15 HASHVAL=02263d99f16f80da665663bb47e1cb664a980401a1d8efcd7dff46c09cce9367 MINER_SIGNATURE=419afd7f
    16a58cc0c3f62073ef6c2d5092dfd7650bfc75cbb323ce5790038dbbfbde04a8b3fd2c53494546b13929b4398b7395c3bbbd4cd7b62bfd8
    ce341cfae CEROCOIN_END SELLER=8f315bb06cdd1c9b43e40d672f001a036fa9bf8ca0d88caa2cf6ec55b0ef682b SELLER_PUB_KEY=
    CEROCOIN_PUBKEY,mod=bb03dee9147ecd6fcd65a6363628ae2420df42c01456b01a82d99eaffdff029c1f76b30d1f410d028f948943e0
    79e7690d7748cc236927d4df5b9e7c5222b8f9,e=10001 BUYER_PUB_KEY=CEROCOIN_PUBKEY,mod=bb03dee9147ecd6fcd65a6363628ae
    2420df42c01456b01a82d99eaffdff029c1f76b30d1f410d028f948943e079e7690d7748cc236927d4df5b9e7c5222b8f9,e=10001 
    TIMESTAMP=1521659273.91 SELLER_TRANX_SIGNATURE=d27544dee4a7cc22b644f893622255414bee5d6b1631805620eb6c472cd13703
    8a8b69a7c328a2bfa91d23d1baf60589d0f92fa34782f74d27640fe0e795c014 CEROCOIN_TRANSACTION_END----

@tag3
Client1 packs the accumulated transactions into a block:
    
    PACKING THE ACCUMULATED TRANSACTIONS INTO A NEW BLOCK
    
    Block creator putting digital signature on the block
    
    TR: hashval for block as int:  112556547459111094707362991438730511176992142012846008255642465480248441399209
    
    TR: block signature as int:  72005989002111138203304445673053119862146986852048738369913245498645609861517688
    98275471642881695860822837550926993797388368855626970965727011952147632480
    
    TR: block hashval as int:    112556547459111094707362991438730511176992142012846008255642465480248441399209
    
    TR: block checkval as int:   112556547459111094707362991438730511176992142012846008255642465480248441399209
    
    
    WILL BROADCAST THIS SIGNED BLOCK: CEROCOIN_BLOCK_BEGIN BLOCK_ID=e19bec2f BLOCK_CREATOR=8f315bb06cdd1c9b43e40d672
    f001a036fa9bf8ca0d88caa2cf6ec55b0ef682b TRANSACTIONS=['----CEROCOIN_TRANSACTION_BEGIN:TRANSACTION_ID=fec4d031:CE
    ROCOIN_BEGIN:COIN_ID=f91fcad7:COIN_MINER=8f315bb06cdd1c9b43e40d672f001a036fa9bf8ca0d88caa2cf6ec55b0ef682b:MINER_
    PUB_KEY=CEROCOIN_PUBKEY,mod=bb03dee9147ecd6fcd65a6363628ae2420df42c01456b01a82d99eaffdff029c1f76b30d1f410d028f94
    8943e079e7690d7748cc236927d4df5b9e7c5222b8f9,e=10001:GENESIS_STRING=a11c3ac52b3c7a707efad42b73b3e8fc68251ec4d2d2
    bbf42559363a672473244acc462b55f6442d9dd4873812a19ea4eda8399cd928232f2900556a18ad43ed:NONCE=500f663ffb4e21000ddcc
    15e2e675db30523751b5b5d702cca10e14330cb6afb9d9fbc72bf324b75f4cdfe1fb47e78cff98896743fbf5843ad9f8df42a711d97:POW_
    DIFFICULTY=251:TIMESTAMP=1521659246.51:HASHVAL=021708d6931d7b78ba78638b7c075679f733ac214882e24929d7f4819a99ea8e:
    MINER_SIGNATURE=39ef4998ee4892b2c93ac2dec26fd9fe5cd39a2b89130b2a44680eef67498a162330ec5b451019612ed251885565bd27
    6fa0274a342610dfa6c465c4a672b9cb:CEROCOIN_END:SELLER=8f315bb06cdd1c9b43e40d672f001a036fa9bf8ca0d88caa2cf6ec55b0
    ef682b:SELLER_PUB_KEY=CEROCOIN_PUBKEY,mod=bb03dee9147ecd6fcd65a6363628ae2420df42c01456b01a82d99eaffdff029c1f76b3
    0d1f410d028f948943e079e7690d7748cc236927d4df5b9e7c5222b8f9,e=10001:BUYER_PUB_KEY=CEROCOIN_PUBKEY,mod=bb03dee9147
    ecd6fcd65a6363628ae2420df42c01456b01a82d99eaffdff029c1f76b30d1f410d028f948943e079e7690d7748cc236927d4df5b9e7c522
    2b8f9,e=10001:TIMESTAMP=1521659253.75:SELLER_TRANX_SIGNATURE=130f985d89c5d43dd2c971149775fd0d2277df4d118fa5a1880
    9ac5207b46508f573c073ebdc84874f512cb2ea63d007ac18f5fe3590179efaa9808e9e8a413e0:CEROCOIN_TRANSACTION_END----',:
    '----CEROCOIN_TRANSACTION_BEGIN:TRANSACTION_ID=c8a81d3d:CEROCOIN_BEGIN:COIN_ID=f4e1b5bf:COIN_MINER=8f315bb06cdd1
    c9b43e40d672f001a036fa9bf8ca0d88caa2cf6ec55b0ef682b:MINER_PUB_KEY=CEROCOIN_PUBKEY,mod=bb03dee9147ecd6fcd65a63636
    28ae2420df42c01456b01a82d99eaffdff029c1f76b30d1f410d028f948943e079e7690d7748cc236927d4df5b9e7c5222b8f9,e=10001:
    GENESIS_STRING=f5849857662e800df9600edecf84779ded0b91ad8877b99f7b3dd0da8fca9154c4c1c8ddbcb3395c133ef3c1ff31018d
    78f0f7a2053283403ffbbd13903c85a1:NONCE=b2f4e377302b23271998bd6102a0b9802af7c57087018add00a4131e893e57b986775841
    c156ef6c388f2f39a07d081aff4d3083c184189e53043b039dccc942:POW_DIFFICULTY=251:TIMESTAMP=1521659272.15:HASHVAL=022
    63d99f16f80da665663bb47e1cb664a980401a1d8efcd7dff46c09cce9367:MINER_SIGNATURE=419afd7f16a58cc0c3f62073ef6c2d509
    2dfd7650bfc75cbb323ce5790038dbbfbde04a8b3fd2c53494546b13929b4398b7395c3bbbd4cd7b62bfd8ce341cfae:CEROCOIN_END:SE
    LLER=8f315bb06cdd1c9b43e40d672f001a036fa9bf8ca0d88caa2cf6ec55b0ef682b:SELLER_PUB_KEY=CEROCOIN_PUBKEY,mod=bb03de
    e9147ecd6fcd65a6363628ae2420df42c01456b01a82d99eaffdff029c1f76b30d1f410d028f948943e079e7690d7748cc236927d4df5b9
    e7c5222b8f9,e=10001:BUYER_PUB_KEY=CEROCOIN_PUBKEY,mod=bb03dee9147ecd6fcd65a6363628ae2420df42c01456b01a82d99eaff
    dff029c1f76b30d1f410d028f948943e079e7690d7748cc236927d4df5b9e7c5222b8f9,e=10001:TIMESTAMP=1521659273.91:SELLER_
    TRANX_SIGNATURE=d27544dee4a7cc22b644f893622255414bee5d6b1631805620eb6c472cd137038a8b69a7c328a2bfa91d23d1baf60589
    d0f92fa34782f74d27640fe0e795c014:CEROCOIN_TRANSACTION_END----'] POW_DIFFICULTY=251 PREV_BLOCK_HASH=fb2c12bbdb4a7
    d2efdd789599f435b28f0bd1527a8705f3577d4bbdec8d8d70b BLOCKCHAIN_LENGTH=2 TIMESTAMP=1521659277.86 BLOCK_CREATOR_
    SIGNATURE=897bcb55543e0df20ed4bea6754dc4c7b92b400ca752ccbb8831691dcf944548cd1f8684ede8499c7e3630487fd5c7e14fd4ea
    b00875d6dcb707982ad36d1160 CEROCOIN_BLOCK_END

@tag3
Client1 is continuing with its new coin search:
    
    Fresh mining with a RANDOM genesis message string    

    Thread-3 -- Try 1 at mining a new coin -- hashval: 92b0c185b204efb89ea695d15d85ac8a3196eeef71a69309d0708d9ca0f67c78
    Thread-3 -- Try 2 at mining a new coin -- hashval: 7e33f604b9f64555aa75a10ac210aadbcdaf42f84f7bcf050d7de803e8691970
    Thread-3 -- Try 3 at mining a new coin -- hashval: a47a69c5c9ea2f119a93ca4a53e0902c7bb3c1e7b9791c8c2c40978c59b4e2e7
    Thread-3 -- Try 4 at mining a new coin -- hashval: 602a2dcbb19463939468a3ba85d297a7eaf62fa215084a0c74794154a8f2ce37
    Thread-3 -- Try 5 at mining a new coin -- hashval: 049ca556bf806ff1114562408be5d335d10ba1394b0f527df0e0dba13780a55e
                                      ...
                                      ...
                                      ...
    
@tag3
Client1 receives a block from Client2:
@tag4 
(This block is much larger because Client2 packs four transactions in each block)

    New block received: CEROCOIN_BLOCK_BEGIN BLOCK_ID=e80076c1 BLOCK_CREATOR=cffdf44c49fc95ef2e3c0b8e0c907b2502e95c141
    59036d611e0d831c5b541e2 TRANSACTIONS=['----CEROCOIN_TRANSACTION_BEGIN:TRANSACTION_ID=d4acdf97:CEROCOIN_BEGIN:COIN_ID
    =dab743b1:COIN_MINER=cffdf44c49fc95ef2e3c0b8e0c907b2502e95c14159036d611e0d831c5b541e2:MINER_PUB_KEY=CEROCOIN_PUBKEY,
    mod=bf6500d1437d9a6b5e8bc72cebc81f3ef4053f33de4c45efbb97ef32e34e9dd331d2239fff94c8e398e381fd4bd7606c723eb6416a98457
    fb8b4845a9175a319,e=10001:GENESIS_STRING=1ec4c97e06a6bbbf31631d3d1ef70c812467ed3777964e4fbd005da1fa110384:NONCE=
    4085310b3d70b30ba0575606b615b0fb5b215e076749b7b5f5ed6a1401ad06537cfc2af97452c2cf56466c053deaa92aa3823d692405e0a5f5
    25c84ad0820f21:POW_DIFFICULTY=251:TIMESTAMP=1521659352.59:HASHVAL=04053713fbb10530e805c2be11fbf3052e32251bfbc464d5
    eb7c76f5edd7e4db:MINER_SIGNATURE=12dd883410df1c21cc70db43c5ac389795c6f897174b23c07ebbbfe6048b9ef8a39ea0b455cbabdd04
    ccaa0854520628ce234687f5f78b09ec20df2cc01e1605a:CEROCOIN_END:SELLER=cffdf44c49fc95ef2e3c0b8e0c907b2502e95c14159036
    d611e0d831c5b541e2:SELLER_PUB_KEY=CEROCOIN_PUBKEY,mod=bf6500d1437d9a6b5e8bc72cebc81f3ef4053f33de4c45efbb97ef32e34e
    9dd331d2239fff94c8e398e381fd4bd7606c723eb6416a98457fb8b4845a9175a319,e=10001:BUYER_PUB_KEY=CEROCOIN_PUBKEY,mod=
    bf6500d1437d9a6b5e8bc72cebc81f3ef4053f33de4c45efbb97ef32e34e9dd331d2239fff94c8e398e381fd4bd7606c723eb6416a98457fb
    8b4845a9175a319,e=10001:TIMESTAMP=1521659369.47:SELLER_TRANX_SIGNATURE=bc80ec8846d7777615db8f54fa33114f01f089bb2
    cac9cd5224d1118e6a1769f8d73df30d6f58f55ed1f0a4a1420e76982ab196393fcfb12cf1aad23fcd4dad7:CEROCOIN_TRANSACTION_END----',
    :'----CEROCOIN_TRANSACTION_BEGIN:TRANSACTION_ID=e4fa0829:CEROCOIN_BEGIN:COIN_ID=d9714493:COIN_MINER=cffdf44c49fc95
    ef2e3c0b8e0c907b2502e95c14159036d611e0d831c5b541e2:MINER_PUB_KEY=CEROCOIN_PUBKEY,mod=bf6500d1437d9a6b5e8bc72cebc8
    1f3ef4053f33de4c45efbb97ef32e34e9dd331d2239fff94c8e398e381fd4bd7606c723eb6416a98457fb8b4845a9175a319,e=10001
    :GENESIS_STRING=59a74b5bdf1066393d608af03199feafe91628ad55aa53465390c0bfeb48a851:NONCE=81fb07af08dd89ebe1c90a1ae0f
    5acbd6ca8228b9bde9999dd906bd9a510cd74675e60a8f6bf74eb680ee8e908b099b963b473fbe01fc92947b1503b9666f06c:POW_DIFFICULTY
    =251:TIMESTAMP=1521659402.37:HASHVAL=00573b0d8cafce4d269cb35c31cba9bc8a5eec4bcb07eb8d62fb4aea9ae5a5e1:MINER_SIGNATURE
    =c3d3c19a14c1b3085136b3a4050c71d210b2cdb54ec98f15f02aa059dedc1152cafd491fe2922e7db573a4be2cc591cc41962f90f92d7855c6
    458122252f05a3:CEROCOIN_END:SELLER=cffdf44c49fc95ef2e3c0b8e0c907b2502e95c14159036d611e0d831c5b541e2:SELLER_PUB_KEY
    =CEROCOIN_PUBKEY,mod=bf6500d1437d9a6b5e8bc72cebc81f3ef4053f33de4c45efbb97ef32e34e9dd331d2239fff94c8e398e381fd4bd7
    606c723eb6416a98457fb8b4845a9175a319,e=10001:BUYER_PUB_KEY=CEROCOIN_PUBKEY,mod=bf6500d1437d9a6b5e8bc72cebc81f3ef
    4053f33de4c45efbb97ef32e34e9dd331d2239fff94c8e398e381fd4bd7606c723eb6416a98457fb8b4845a9175a319,e=10001:TIMESTAMP
    =1521659405.88:SELLER_TRANX_SIGNATURE=39459a484b9ec5d1b58d3fe65186d42c99b3c8d36a4ccc0902deccb1a9556bf62c6fcb95834
    aed7d3066bb0d27c205cad67d36021512753fecfebd6c70090711:CEROCOIN_TRANSACTION_END----',:'----CEROCOIN_TRANSACTION_BEGIN
    :TRANSACTION_ID=fdb5b1b3:CEROCOIN_BEGIN:COIN_ID=dba393f5:COIN_MINER=cffdf44c49fc95ef2e3c0b8e0c907b2502e95c14159036d
    611e0d831c5b541e2:MINER_PUB_KEY=CEROCOIN_PUBKEY,mod=bf6500d1437d9a6b5e8bc72cebc81f3ef4053f33de4c45efbb97ef32e34e9d
    d331d2239fff94c8e398e381fd4bd7606c723eb6416a98457fb8b4845a9175a319,e=10001:GENESIS_STRING=59a74b5bdf1066393d608af03
    199feafe91628ad55aa53465390c0bfeb48a851:NONCE=f8708170929fcc11a920b578c791266cda2ccb22a301f73f1b7dd115adc343c15ba
    fc42391ea37a79d835f831bfef1bc18691b47cfbfdd5c67a7d5d1e0161aec:POW_DIFFICULTY=251:TIMESTAMP=1521659442.01:HASHVAL=
    0649a35f8e1b33137882c530b1433a35a7176a82be6dade129b320d269ddb15e:MINER_SIGNATURE=12d598a3bf463b6afa5971b1e00be628
    9190c6bc78b0261c1c9855a116663e8f4754a3de887000ffd5cb62f300bd5cf7c719979e85207d8d4163d036de2841bd1:CEROCOIN_END
    :SELLER=cffdf44c49fc95ef2e3c0b8e0c907b2502e95c14159036d611e0d831c5b541e2:SELLER_PUB_KEY=CEROCOIN_PUBKEY,mod=bf6500
    d1437d9a6b5e8bc72cebc81f3ef4053f33de4c45efbb97ef32e34e9dd331d2239fff94c8e398e381fd4bd7606c723eb6416a98457fb8b4845a
    9175a319,e=10001:BUYER_PUB_KEY=CEROCOIN_PUBKEY,mod=bf6500d1437d9a6b5e8bc72cebc81f3ef4053f33de4c45efbb97ef32e34e9dd
    331d2239fff94c8e398e381fd4bd7606c723eb6416a98457fb8b4845a9175a319,e=10001:TIMESTAMP=1521659446.4:SELLER_TRANX_
    SIGNATURE=f93e2bbae95d2789c3e1d7063203921d60c72e95eb99e20c0f863ddd5261751faca48b57f4f8024971ef8f88c156982d5675cf55
    78274a60b4872cd08eae5855:CEROCOIN_TRANSACTION_END----',:'----CEROCOIN_TRANSACTION_BEGIN:TRANSACTION_ID=c2ec70c7:
    CEROCOIN_BEGIN:COIN_ID=c211147f:COIN_MINER=cffdf44c49fc95ef2e3c0b8e0c907b2502e95c14159036d611e0d831c5b541e2:MINER_
    PUB_KEY=CEROCOIN_PUBKEY,mod=bf6500d1437d9a6b5e8bc72cebc81f3ef4053f33de4c45efbb97ef32e34e9dd331d2239fff94c8e398e38
    1fd4bd7606c723eb6416a98457fb8b4845a9175a319,e=10001:GENESIS_STRING=9f0eb4cd38c01a2ca6176ae51068b0b7b2c2801bd4a977
    0930d42aac89191a71:NONCE=5ce8a1d8cff0e0c9f2341996cfac85ffa0f99851b4942d98c81068da595e4c2c407c68642edfb6d1b195dcec
    36062d2925cf4571c39b96494ec2bb58b842770d:POW_DIFFICULTY=251:TIMESTAMP=1521659676.3:HASHVAL=07dc521a04b7fbf85ff1f7
    249c3e5f06c8f210c0d7802112949da7a722ea3243:MINER_SIGNATURE=106620245b3c023c36a3ac0d16ea8889e857dc0149c5af88d54e54
    cf9531efe859be2c7c9c155cbcb11a5cbacd82e37931f68e3d072ede327cf4427e36de1a370:CEROCOIN_END:SELLER=cffdf44c49fc95ef2
    e3c0b8e0c907b2502e95c14159036d611e0d831c5b541e2:SELLER_PUB_KEY=CEROCOIN_PUBKEY,mod=bf6500d1437d9a6b5e8bc72cebc81f
    3ef4053f33de4c45efbb97ef32e34e9dd331d2239fff94c8e398e381fd4bd7606c723eb6416a98457fb8b4845a9175a319,e=10001:BUYER_
    PUB_KEY=CEROCOIN_PUBKEY,mod=bf6500d1437d9a6b5e8bc72cebc81f3ef4053f33de4c45efbb97ef32e34e9dd331d2239fff94c8e398e38
    1fd4bd7606c723eb6416a98457fb8b4845a9175a319,e=10001:TIMESTAMP=1521659680.55:SELLER_TRANX_SIGNATURE=12d3ced3a0862b
    01c5b22346fcb0fc17d0900836a1242b80d61c5467c99045217f6581350766ab074eea42bcf695f1742d9afecbce315f4d8e058413b2f6089
    75:CEROCOIN_TRANSACTION_END----'] POW_DIFFICULTY=251 PREV_BLOCK_HASH=9f0eb4cd38c01a2ca6176ae51068b0b7b2c2801bd4a9
    770930d42aac89191a71 BLOCKCHAIN_LENGTH=12 TIMESTAMP=1521659727.59 BLOCK_CREATOR_SIGNATURE=d7a40e834e5b9657f761f725
    2d604edb901f71e9a4d6693cd2e80bbb3e8938add291737874d3d11c1b3b30025a5b46dd692975d2d2c2e0ee270c0839ca45dbcd CEROCOIN
    _BLOCK_END
    
    received block validated
    
    ========> received blockchain length:     12
    
    ========> self.blockchain_length:  10
    
    ========> received_block_pow_difficulty:  251
    
    ========> self.pow_difficulty:  251
    
    ========> WILL ASK THE CURRENT MINER THREAD TO STOP
    
    >>>>>>>>> CURRENT MINER THREAD TERMINATED SUCCESSFULLY <<<<<<<<<<<<
    
    ========> STARTING A NEW COIN MINER THREAD WITH POW DIFFICULTY OF 251 AND BLOCKCHAIN LENGTH OF 12

    
    server in interactive mode with client
    
@tag3
Client1 starts new coin search in a newly created miner thread with different search parameters:
    
    Using the new block for forming the genesis string
    
    Thread-7 -- Try 1 at mining a new coin -- hashval: 779672b69174950065a35056f4988ca04e6c7bf98a2147003375f9d4a45bee0e
    Thread-7 -- Try 2 at mining a new coin -- hashval: cca7bfb5613eda1630477bb045048ce1ede393682bf477c987ec9264497ea60a
    Thread-7 -- Try 3 at mining a new coin -- hashval: 87cf7a04e66d1a09f7ad32b6a8155dad3f9d8229154ce81e2cc0f5047333f663
    Thread-7 -- Try 4 at mining a new coin -- hashval: 8e4b01d6b47895d62ffde1a10d78e53da089b6d9684df7f76f4d1c541dcf773e
    Thread-7 -- Try 5 at mining a new coin -- hashval: 69aac946e5f1b9aa8d69518d65e4cc6f489e97b944cef374d6f3008663f60228
    Thread-7 -- Try 6 at mining a new coin -- hashval: a02346fee3f495ad36cf06fa25babee2e74d58ab0b073fed6f011ac4c4975f74
    
                                  ...
                                  ...
                                  ...

@endcode    

    Note again that what is shown above is just for Client1.  You will see a
    similar output on the terminal screen of Client2.  Since Client2 was asked
    to pack four transactions in each block, the formation of the blocks would
    occur less frequently in Client2's terminal screen.


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
        like 512 for the modulus since that keeps the size of the keys small
        enough so that you can conveniently display the transactions in the
        demo.  Recall that a transaction must contain the public key of the
        buyer of the coin and the size of the public key is only larger than the
        size of the modulus.  Obviously, using a small value like 512 for the
        modulus gives you no security at all in this day and age.  But that's
        okay for for just the demos.

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

    and/or

@begincode
            sudo python3 setup.py install
@endcode

    On Linux distributions, this will install the module file at a location that
    for Python2 looks like

@begincode
             /usr/local/lib/python2.7/dist-packages/
@endcode

    and for Python3 at a location like

             /usr/local/lib/python3.5/dist-packages/

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

    Future plans include creating a rudimentary wallet to go with CeroCoin.
    Additionally, I am also planning to replace the inter-thread coordination
    logic with one based on events.


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
import functools

def interrupt_sig_handler( signum, frame ):                  
    print("=======> terminating all threads with kill")
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
        '''
        Only used for testing
        '''
        print("\n\nInitializing the node and running only the miner")
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
        print("\nlocal IPv4 address: %s" % local_addr)
        soc.close()
        while True:
            ans = None
            if sys.version_info[0] == 3:
                ans = input("\nIs %s for your local IPv4 address correct? Enter 'y' for 'yes' and 'n' for 'no': " % local_addr)
            else:
                ans = raw_input("\nIs %s for your local IPv4 address correct? Enter 'y' for 'yes' and 'n' for 'no': " % local_addr)
            ans = ans.strip()
            if ans == 'y' or ans == 'yes':
                return local_addr
            elif ans == 'n' or ans == 'no':
                while True:
                    ans = None
                    if sys.version_info[0] == 3:
                        ans = input("\nEnter your local IPv4 address:  ")
                    else:
                        ans = raw_input("\nEnter your local IPv4 address:  ")
                    try:
                        socket.inet_pton(socket.AF_INET, ans)
                        local_addr = ans                
                        break
                    except:
                        print("The IPv4 address you entered does not look right.  Try again.")
                return local_addr
            else:
                print("\nYour answer can only be 'y' or 'n'.  Try again!")


    def miner_supervisor(self):
        '''
        Only used in testing
        '''
        print("\n\n=======STARTING A MINER SUPERVISOR THREAD======\n\n")
        while self.t_miner is None: time.sleep(2)
        while True:
            if  self.miner_iteration_index % 20 > 10:
                print("\n\nMiner supervisor terminating the miner thread\n")
                self.terminate_thread( self.t_miner )
                time.sleep(2)
                print("\n\n=======STARTING A NEW MINER THREAD======\n\n")
                self.miner_iteration_index += 10
                self.t_miner = ThreadedMiner( self )
                self.t_miner.start()
                time.sleep(2)   

    def run_hasher(self, num_iterations):
        '''
        Only used for testing
        '''
        genesis_string = binascii.b2a_hex(os.urandom(64))
        if sys.version_info[0] == 3:
            # It is easier to use Python's encode() and decode() to go back and forth between the
            # bytes type and str type, but the statement that follows is more fun to look at:
            genesis_string = functools.reduce(lambda x,y: x+y, list(map(lambda x: chr(x), genesis_string)))
        for iter_index in range(num_iterations):
            nonce = binascii.b2a_hex(os.urandom(64))
            if sys.version_info[0] == 3:
                nonce = functools.reduce(lambda x,y: x+y, list(map(lambda x: chr(x), nonce)))
            string_to_be_hashed = genesis_string + nonce
            hasher = SHA256.SHA256(message_in_ascii = string_to_be_hashed)
            hashval = hasher.sha256()  
            print("for try %d, hashval: %s" % (iter_index, hashval))
            if iter_index == 0:
                return string_to_be_hashed,hashval

    def scan_the_network_for_cerocoin_nodes(self):
        ip_block_to_scan = self.cerocoin_network[:]
        try:
            del ip_block_to_scan[ip_block_to_scan.index(self.local_ip_address)]
        except:
            print("\nYour local IP address is not included in the list of network addresses supplied in your constructor call. !!!ABORTING!!!\n")
            os.kill( os.getpid(), signal.SIGKILL )                           
        print("\n Will scan the IP addresses: %s" % str(ip_block_to_scan))
        remote_server_port = self.server_port
        max_num_of_tries_for_establishing_network = 3
        while True:
            if max_num_of_tries_for_establishing_network == 0:
                print("\n\nUnable to establish a network for CeroCoin demonstrations.  !!!ABORTING!!!\n\n")
                os.kill( os.getpid(), signal.SIGKILL )                                           
            for host in ip_block_to_scan:
                try:
                    print("\nTrying to connect with host %s\n" % host)
                    sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )   
                    sock.settimeout(3)    
                    sock.connect( (host, remote_server_port) )                                 
                    sock.settimeout(None)      
                    print("\nDiscovering CeroCoinClient Nodes: -- Made connection with host: %s\n" % host)
                    self.outgoing_client_sockets.append(sock)
                except:
                    print("        no connection possible with %s" % host)
            if len(self.outgoing_client_sockets) == 1:
                print("\n\nWARNING: Only one other CeroCoin node found -- only the simplest of blockchain demos possible\n\n")
                break
            elif len(self.outgoing_client_sockets) == 0:
                max_num_of_tries_for_establishing_network -= 1
                print("\n\n\nNo CeroCoin clients found.  Will sleep for 5 sec and try again. (Max num of tries: 3)")
                time.sleep(5)
            else: 
                break
    #server
    def set_up_server(self):
        mdebug = True
        port = self.server_port
        try:
            if mdebug:
                print("\n\nWill set up a server on port %d\n\n" % port)
            server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_sock.bind( ('', port) )        
            server_sock.listen(5)                 
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket = server_sock
            print("\n\nSUCCESSFULLY CREATED A SERVER SOCKET ON PORT %d\n\n" % port)
        except (socket.error, (value, message)) as error:       
            if server_sock:                         
                server_sock.close()                 
                print("\nCould not establish server socket: " + message)  
                os.killpg(0, signal.SIGKILL)
        while True:       
            (client_sock, address) = server_sock.accept()                   
            print("\nConnection request from address: %s" % str(address))
            t_connection = ThreadedClientConnection(self, client_sock, address)
            t_connection.daemon = True
            t_connection.start()

    #clientcon
    def client_connection(self, client_socket, ip_address):
        mdebug = False
        while True:                                               
            print("\nserver in interactive mode with client\n")
            client_line = ''                                   
            while 1:                                           
                client_byte = client_socket.recv(1) 
                if sys.version_info[0] == 3:
                    client_byte = client_byte.decode()
                if client_byte == '\n' or client_byte == '\r': 
                    break                                      
                else:                                          
                    client_line += client_byte                 
            if mdebug:
                print("\n::::::::::::::line received from remote: %s\n" % client_line)
            if client_line == "Send pub key for a new transaction":
                if self.pub_key_string is None:
                    sys.exit("buyer ID not yet created")
                if sys.version_info[0] == 3:
                    tobesent = "BUYER_PUB_KEY=" + ",".join(self.pub_key_string.split()) + "\n" 
                    client_socket.send( tobesent.encode() )
                else:
                    client_socket.send( "BUYER_PUB_KEY=" + ",".join(self.pub_key_string.split()) + "\n" )
            elif client_line.startswith("----CEROCOIN_TRANSACTION_BEGIN"):    
                print("\nTransaction received: %s\n" % client_line)
                transaction_received = client_line
                print("\nValidating transaction\n")
                lock.acquire()
                if self.is_transaction_valid( transaction_received ):
                    self.prev_transaction = self.transaction
                    print("\n\nAdding new transaction to the list in 'self.transactions_received'\n")
                    self.transactions_received.append( transaction_received )
                    print("\n\nNumber of transactions in 'self.transactions_received': %d\n" % len(self.transactions_received))
                lock.release()
            elif client_line == "Sending new block":    
                if sys.version_info[0] == 3:
                    client_socket.send("OK to new block\n".encode())
                else:
                    client_socket.send("OK to new block\n")
            elif client_line.startswith("CEROCOIN_BLOCK_BEGIN"):
                self.blockvalidator_flag = True
                print("\n\nNew block received: %s\n" % client_line)
                block_received = client_line
                if self.is_block_valid( block_received ):
                    print("\nreceived block validated\n")
                    lock.acquire()
                    (received_blockchain_len, received_block_pow_difficulty) = self.get_block_prop(block_received,
                                                                ('BLOCKCHAIN_LENGTH', 'POW_DIFFICULTY'))
                    received_blockchain_len = int(received_blockchain_len)
                    received_block_pow_difficulty = int(received_block_pow_difficulty)
                    print("\n========> received blockchain length:   %d" % received_blockchain_len)
                    print("\n========> self.blockchain_length:       %d" % self.blockchain_length)
                    print("\n========> received_block_pow_difficulty:  %d" % received_block_pow_difficulty)
                    print("\n========> self.pow_difficulty:            %d" % self.pow_difficulty)
                    if self.block is None:
                        self.block = block_received
                        self.blockchain_length = received_blockchain_len
                        print("\n========> WILL ASK THE CURRENT MINER THREAD TO STOP\n")
                        self.terminate_thread( self.t_miner )
                        self.t_miner = None
                        time.sleep(2)
                        self.block = block_received
                        self.blockchain_length = received_blockchain_len                            
                        self.pow_difficulty = received_block_pow_difficulty
                        print("\n========> STARTING A NEW COIN MINER THREAD WITH POW DIFFICULTY OF %d AND BLOCKCHAIN LENGTH OF %d\n\n" % (self.pow_difficulty, self.blockchain_length))
                        self.t_miner = ThreadedMiner( self )
                        self.t_miner.daemon = True
                        self.t_miner.start()
                        time.sleep(5)
                        self.t_miner_changed = False
                    elif (received_blockchain_len > self.blockchain_length) and \
                                         (received_block_pow_difficulty <= self.pow_difficulty):
                        print("\n========> WILL ASK THE CURRENT MINER THREAD TO STOP\n")
                        self.terminate_thread( self.t_miner )
                        self.t_miner = None
                        time.sleep(2)
                        self.block = block_received
                        self.blockchain_length = received_blockchain_len                            
                        self.pow_difficuly = received_block_pow_difficulty
                        print("\n========> STARTING A NEW COIN MINER THREAD WITH POW DIFFICULTY OF %d AND BLOCKCHAIN LENGTH OF %d\n\n" % (self.pow_difficulty, self.blockchain_length))
                        self.t_miner = ThreadedMiner( self )
                        self.t_miner.daemon = True
                        self.t_miner.start()
                        time.sleep(5)
                        self.t_miner_changed = False
                    else:
                        print("\nNo reason to abandon the current miner thread\n") 
                    lock.release()
                else:
                    print("\n\nNOTICE: An illegal block received --- Ignoring the received block\n")
                self.blockvalidator_flag = False
            else:
                print("buyer:  We should not be here")

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
            print("\n\nPrepareTranx::Buyer pub key:  %s\n" % buyer_pub_key)
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
                print("\n\nadditional sleep of 10 secs for the miner for the next round\n\n")
                time.sleep(10)
            time.sleep(2)
            hashval_int = 1 << 260
            iteration_control = 0
            genesis_string = string_to_be_hashed = None
            if self.block is None:
                print("\n\nFresh mining with a RANDOM genesis message string\n\n") 
                genesis_string = binascii.b2a_hex(os.urandom(64))
                if sys.version_info[0] == 3:
                    # It is easier to use Python's encode() and decode() to go back and forth between the
                    # bytes type and str type, but the statement that follows is more fun to look at:
                    genesis_string = functools.reduce(lambda x,y: x+y, list(map(lambda x: chr(x), genesis_string)))
            else:
                print("\n\nUsing the new block for forming the genesis string\n\n")
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
                if sys.version_info[0] == 3:
                    nonce = functools.reduce(lambda x,y: x+y, list(map(lambda x: chr(x), nonce)))
                string_to_be_hashed = genesis_string + nonce                
                hasher = SHA256.SHA256(message_in_ascii = string_to_be_hashed)
                hashval = hasher.sha256()  
                if len(hashval) < 64:
                    hashval = [0] * (64 - len(hashval)) + hashval
                print("%s -- Try %d at mining a new coin -- hashval: %s" % (threadname, iteration_control, hashval))
                hashval_int = int(hashval, 16)
            print("\n\n***SUCCESS***  -- A coin mined successfully with hashval %s\n" % hashval)
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
            print("\n\nInside miner: new coin mined: %s\n\n" % str(newcoin))
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
            print(">>>>>>>>> CURRENT MINER THREAD TERMINATED SUCCESSFULLY <<<<<<<<<<<<") 

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
            print("\n\nLOOKING FOR A CLIENT FOR MAKING A TRANSACTION\n\n")
            coin = self.coins_currently_owned_digitally_signed.pop()
            if coin is not None: 
                print("\nNew outgoing coin:  %s" % coin)
            buyer_sock = None
            new_transaction = None
            random.shuffle(self.outgoing_client_sockets)
            sock = self.outgoing_client_sockets[0]
            if sys.version_info[0] == 3:
                sock.send(b"Send pub key for a new transaction\n")
            else:
                sock.send("Send pub key for a new transaction\n")
            try:
                while True: 
                    while self.blockmaker_flag or self.blockvalidator_flag: time.sleep(2)
                    message_line_from_remote = ""
                    while True:
                        byte_from_remote = sock.recv(1)               
                        if sys.version_info[0] == 3:
                            byte_from_remote = byte_from_remote.decode()
                        if byte_from_remote == '\n' or byte_from_remote == '\r':   
                            break                                        
                        else:                                            
                            message_line_from_remote += byte_from_remote
                    if mdebug:
                        print("\n:::::::::::::message received from remote: %s\n" % message_line_from_remote)
                    if message_line_from_remote == "Do you have a coin to sell?":
                        if sys.version_info[0] == 3:
                            sock.send( b"I do. If you want one, send public key.\n" )
                        else:
                            sock.send( "I do. If you want one, send public key.\n" )
                    elif message_line_from_remote.startswith("BUYER_PUB_KEY="):
                        while self.blockmaker_flag or self.blockvalidator_flag: time.sleep(2)
                        buyer_pub_key = message_line_from_remote
                        print("\nbuyer pub key: %s" % buyer_pub_key)
                        new_transaction = self.prepare_new_transaction(coin, buyer_pub_key)
                        self.old_transaction = self.transaction
                        self.transaction = new_transaction
                        self.transactions_generated.append(new_transaction)
                        print("\n\nNumber of tranx in 'self.transactions_generated': %d\n" % len(self.transactions_generated))
                        print("\n\nsending to buyer: %s\n"  % new_transaction)
                        if sys.version_info[0] == 3:
                            tobesent = str(new_transaction) + "\n"
                            sock.send( tobesent.encode() )
                        else:
                            sock.send( str(new_transaction) + "\n" )
                        self.num_transactions_sent += 1
                        break
                    else:
                        print("seller side: we should not be here")
            except:
               print("\n\n>>>Seller to buyer: Could not maintain socket link with remote for %s\n" % str(socket))
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
            print("\n\n\nPACKING THE ACCUMULATED TRANSACTIONS INTO A NEW BLOCK\n\n")
            current_block_hash = min_pow_difficulty = None
            if self.block is None:
                current_block_hash = self.gen_rand_bits_with_set_bits(256)
                min_pow_difficulty = self.pow_difficulty              
                self.blockchain_length = len(self.transactions_generated)
            else:
                current_block_hash = self.get_hash_of_block(self.block)       
                min_pow_difficulty = 0
                for tranx in self.transactions_generated:
                    tranx_pow = int(self.get_tranx_prop(self.block, 'POW_DIFFICULTY'))
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
            print("\n\n\nWILL BROADCAST THIS SIGNED BLOCK: %s\n\n\n" % new_block_with_signature)
            self.block = new_block_with_signature
            for sock in self.outgoing_client_sockets:   
                if sys.version_info[0] == 3:
                    sock.send("Sending new block\n".encode())
                else:
                    sock.send("Sending new block\n")
                try:
                    while True: 
                        message_line_from_remote = ""
                        while True:
                            byte_from_remote = sock.recv(1)               
                            if sys.version_info[0] == 3:
                                byte_from_remote = byte_from_remote.decode()
                            if byte_from_remote == '\n' or byte_from_remote == '\r':   
                                break                                        
                            else:                                            
                                message_line_from_remote += byte_from_remote
                        if mdebug:
                            print("\n::::::::::BLK: message received from remote: %s\n" % message_line_from_remote)
                        if message_line_from_remote == "OK to new block":
                            if sys.version_info[0] == 3:
                                tobesent = self.block + "\n"
                                sock.send( tobesent.encode() )
                            else:
                                sock.send( self.block + "\n" )
                            break
                        else:
                            print("sender side for block upload: we should not be here")
                except:
                    print("Block upload: Could not maintain socket link with remote for %s\n" % str(sockx))
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
            print("\nVerifier: modulus: %d    public exponent: %d" % (mod, e))
        coin_without_signature, coin_signature_string = " ".join(coin_splits[1:-2]), coin_splits[-2]
        hasher = SHA256.SHA256(message = str(coin_without_signature))
        hashval = hasher.sha256()  
        hashval_int = int(hashval, 16)
        print("\nVerifier: coin hashval as int: %d" % hashval_int)
        coin_signature = int( coin_signature_string[ coin_signature_string.index('=')+1 : ], 16 )
        coin_checkval_int = modular_exp( coin_signature, e, mod )        
        print("\nVerifier: coin checkval as int: %d" % coin_checkval_int)
        if hashval_int == coin_checkval_int: 
            print("\nVerifier: Since the coin hashval is equal to the coin checkval, the coin is authentic\n")
            return True
        else: 
            return False

    def add_to_coins_owned_digitally_signed(self, signed_coin):
        how_many_currently_owned = len(self.coins_currently_owned_digitally_signed)
        print("\n\nAdding the digitally signed new coin (#%d) to the 'currently owned and digitally signed' collection\n" % (how_many_currently_owned + 1))
        self.coins_currently_owned_digitally_signed.append(signed_coin)

    def add_to_coins_acquired_from_others(self, newcoin):
        how_many_previously_bought = len(self.coins_acquired_from_others)
        print("\nChecking authenticity of the coin")
        check = self.verify_coin(newcoin)
        if check is True:
            print("\nCoin is authentic")
        print("\nAdding the received coin (#%d) to the 'previously bought' collection\n" % (how_many_previously_bought + 1))
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
            print("\nDIGI_SIGN -- modulus: %d" % modulus)
            print("\nDIGI_SIGN -- public exp: %d" % e)
            print("\nDIGI_SIGN -- private exp: %d" % d)
            print("\nDIGI_SIGN -- p: %d" % p)
            print("\nDIGI_SIGN -- q: %d" % q)
        splits = str(coin).split()
        coin_without_ends = " ".join(str(coin).split()[1:-1])
        hasher = SHA256.SHA256(message = str(coin_without_ends))
        hashval = hasher.sha256()  
        if mdebug:
            print("\nDIGI_SIGN: hashval for coin as int: %d" % int(hashval, 16))
        hashval_int = int(hashval, 16)
        Vp = modular_exp(hashval_int, d, p)
        Vq = modular_exp(hashval_int, d, q)
        coin_signature = (Vp * Xp) % modulus + (Vq * Xq) % modulus
        if mdebug:
            print("\nDIGI_SIGN: coin signature as int: %d" % coin_signature)
        coin_signature_in_hex = "%x" % coin_signature
        coin_with_signature = self.insert_miner_signature_in_coin(str(coin), coin_signature_in_hex)
        checkval_int = modular_exp(coin_signature, e, modulus)
        if mdebug:
            print("\nDIGI_SIGN: coin hashval as int:  %d" % hashval_int)
            print("\nDIGI_SIGN: coin checkval as int: %d" % checkval_int)
        assert hashval_int == checkval_int, "coin hashval does not agree with coin checkval"
        if mdebug:
            print("\nThe coin is authentic since its hashval is equal to its checkval")
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
            print("\nTR: transaction hashval as int: %d" % int(hashval, 16))
        hashval_int = int(hashval, 16)
        Vp = modular_exp(hashval_int, d, p)
        Vq = modular_exp(hashval_int, d, q)
        tranx_signature = (Vp * Xp) % modulus + (Vq * Xq) % modulus
        if mdebug:
            print("\nTR: transaction signature as int: %d" % tranx_signature)
        tranx_signature_in_hex = "%x" % tranx_signature
        tranx_with_signature = '----CEROCOIN_TRANSACTION_BEGIN ' + tranx_without_ends + " SELLER_TRANX_SIGNATURE=" + tranx_signature_in_hex + ' CEROCOIN_TRANSACTION_END----'
        checkval_int = modular_exp(tranx_signature, e, modulus)
        print("\nTR: Transaction hashval as int:   %d" % hashval_int)
        print("\nTR: Transaction checkval as int:  %d" % checkval_int)
        assert hashval_int == checkval_int, "tranx hashval does not agree with tranx checkval"
        print("\nTransaction is authenticated since its hashval is equal to its checkval")
        return tranx_with_signature

    #digisignblock
    def digitally_sign_block(self, block):
        '''
        Even though the method 'get_hash_of_block()' only hashes the transactions, prev_block hash,
        and the timestamp, we use the entire block, sans its two end delimiters, for the block 
        creator's digital signature.
        '''
        print("\n\nBlock creator putting digital signature on the block\n\n")
        mdebug = True
        modulus,e,d,p,q,Xp,Xq = self.modulus,self.pub_exponent,self.priv_exponent,self.p,self.q,self.Xp,self.Xq
        block_without_ends = " ".join(block.split()[1:-1])
        hasher = SHA256.SHA256(message = block_without_ends)
        hashval = hasher.sha256()  
        if mdebug:
            print("\nTR: hashval for block as int: %d" % int(hashval, 16))
        hashval_int = int(hashval, 16)
        Vp = modular_exp(hashval_int, d, p)
        Vq = modular_exp(hashval_int, d, q)
        block_signature = (Vp * Xp) % modulus + (Vq * Xq) % modulus
        if mdebug:
            print("\nTR: block signature as int: %d" % block_signature)
        block_signature_in_hex = "%x" % block_signature
        block_with_signature = 'CEROCOIN_BLOCK_BEGIN ' + block_without_ends + " BLOCK_CREATOR_SIGNATURE=" + block_signature_in_hex + ' CEROCOIN_BLOCK_END'
        checkval_int = modular_exp(block_signature, e, modulus)
        if mdebug:
            print("\nTR: block hashval as int:   %d" % hashval_int)
            print("\nTR: block checkval as int:  %d" % checkval_int)
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
#            print("\nitem in validating block: %s" % item)
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
        self.network_node.miner_supervisor()

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

