import CeroCoinClient
import unittest
import hashlib

class TestCeroCoinHashing(unittest.TestCase):

    def setUp(self):
        print("Testing CeroCoin hashing")
        self.cc = CeroCoinClient.CeroCoinClient(
                               run_miner_only             =  True,
                               starting_pow_difficulty    =  252,
                               modulus_size               =  512,
                  )  

    def test_cero_coin_hashing(self):
        msg_string, hashval = self.cc.run_hasher(1)
        print "hash value:  ", hashval
        checkval =  hashlib.sha256(msg_string.encode('utf-8')).hexdigest()
        print "check value: ", checkval
        self.assertEqual(hashval, checkval)

def getTestSuites(type):
    return unittest.TestSuite([
            unittest.makeSuite(TestCeroCoinHashing, type)
                             ])                    
if __name__ == '__main__':
    unittest.main()

