import hmac
import hashlib
import math

class stake_casino:
    def __init__(self):
        self.luckynumber = 0

    def generator(self,nonce, clientseed, serverseed, round='0'):
        count = 0
        bserver_seed = serverseed.encode('utf-8')  # key
        # serverSeed = bytes(secret, 'UTF-8')  #Key
        bclient_seed = bytes(clientseed, 'UTF-8')
        nonce = nonce
        snonce = str(nonce)
        bnonce = bytes(snonce, 'UTF-8')
        delimiter = bytes(':', 'UTF-8')
        bround = bytes(round, 'UTF-8')

        message = bclient_seed + delimiter + bnonce + delimiter + bround

        hmac_result = hmac.new(bserver_seed, message, hashlib.sha256).hexdigest()


        offset = 0
        twoset = 2
        luck = 0

        while offset < 8:
            count += 1
            number = hmac_result[offset:twoset]
            number = int(number, 16)
            offset += 2
            twoset += 2
            luck = luck + number / (256 ** count)
        self.luckynumber = luck * 10001
        self.luckynumber = math.floor(self.luckynumber)
        self.luckynumber = self.luckynumber / 100
        return self.luckynumber