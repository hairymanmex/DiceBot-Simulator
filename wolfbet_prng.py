import hmac
import hashlib


class wolfbet:
    def __init__(self):
        self.luckynumber = 0

    def generator(self, nonce, clientseed, serverseed,):

        bserver_seed = serverseed.encode('utf-8')  # key
        bclient_seed = bytes(clientseed, 'UTF-8')
        nonce = nonce
        snonce = str(nonce)
        bnonce = bytes(snonce, 'UTF-8')
        delimiter = bytes('_', 'UTF-8')

        message = bclient_seed + delimiter + bnonce
        hash = hmac.new(message, bserver_seed,hashlib.sha256).hexdigest()

        index = 0
        fiveset = 5
        number = hash[index:5]

        self.luckynumber = int(number,16)

        while (self.luckynumber >= 1000000):
            number = hash[index:fiveset]
            self.luckynumber = int(number,16)
            index += 5
            fiveset += 5
        return float(format(self.luckynumber % 10000 /100, ".2f"))


