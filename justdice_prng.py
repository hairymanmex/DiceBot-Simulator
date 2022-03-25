import hmac
import hashlib


class justdice:
    def __init__(self):
        self.luckynumber = 0

    def generator(self, nonce, clientseed, serverseed):

        hash = hmac.new(self.str2bin(serverseed), self.str2bin(clientseed + ":" + str(nonce)), hashlib.sha512).hexdigest()
        i = 0
        while True:
            if i == 25:
                self.luckynumber = int(hash[-3:], 16) / 10000
                break
            else:
                f5p = int(hash[5 * i: 5 + 5 * i], 16)
                if f5p < 1000000:
                    self.luckynumber = f5p / 10000
                    break
                i += 1

        return self.luckynumber

    def str2bin(self, string):
        return bytes(string, 'UTF-8')