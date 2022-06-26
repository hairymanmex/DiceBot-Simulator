import hmac
import hashlib
import math


class bitsler:
    def __init__(self):
        self.luckynumber = 0

    def generator(self, nonce, clientseed, serverseed):

        snonce = str(nonce)
        bnonce = bytes(snonce, 'UTF-8')
        serverseed = bytes(serverseed, 'UTF-8')
        clientseed = bytes(clientseed, 'UTF-8')
        # nonce = bytes(nonce, 'UTF-8')
        key = bytes(',', 'UTF-8')

        seed = hmac.new(serverseed, clientseed + key + bnonce, hashlib.sha512).hexdigest()

        offset=0
        fiveset=5

        number = seed[offset:fiveset]
        number = int(number, 16)

        while number > 999999:
            number = seed[offset:fiveset]
            number = int(number, 16)
            offset+=5
            fiveset+=5
        self.luckyNumber = (number % 10000) / 100
        return self.luckyNumber
