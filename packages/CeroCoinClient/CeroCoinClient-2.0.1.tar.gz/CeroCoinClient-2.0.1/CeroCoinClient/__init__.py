#!/usr/bin/env python

import sys

if sys.version_info[0] == 3:

    from CeroCoinClient.CeroCoinClient import __version__
    from CeroCoinClient.CeroCoinClient import __author__
    from CeroCoinClient.CeroCoinClient import __date__
    from CeroCoinClient.CeroCoinClient import __url__
    from CeroCoinClient.CeroCoinClient import __copyright__
    
    from CeroCoinClient.CeroCoinClient import CeroCoin
    from CeroCoinClient.CeroCoinClient import CeroCoinClient
    from CeroCoinClient.CeroCoinClient import ThreadedServer
    from CeroCoinClient.CeroCoinClient import ThreadedScanner
    from CeroCoinClient.CeroCoinClient import ThreadedMiner
    from CeroCoinClient.CeroCoinClient import ThreadedTransactor
    from CeroCoinClient.CeroCoinClient import ThreadedBlockMaker
    from CeroCoinClient.CeroCoinClient import ThreadedClientConnection
    from CeroCoinClient.CeroCoinClient import ThreadedMinerSupervisor
    
else:

    from CeroCoinClient import __version__
    from CeroCoinClient import __author__
    from CeroCoinClient import __date__
    from CeroCoinClient import __url__
    from CeroCoinClient import __copyright__
    
    from CeroCoinClient import CeroCoin
    from CeroCoinClient import CeroCoinClient
    from CeroCoinClient import ThreadedServer
    from CeroCoinClient import ThreadedScanner
    from CeroCoinClient import ThreadedMiner
    from CeroCoinClient import ThreadedTransactor
    from CeroCoinClient import ThreadedBlockMaker
    from CeroCoinClient import ThreadedClientConnection
    from CeroCoinClient import ThreadedMinerSupervisor
    
