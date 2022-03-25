import hmac
import hashlib

class primedice:
    def __init__(self):
        self.luckynumber = 0

    def str2bin(self, string):
        return bytes(string, 'UTF-8')

    def generator(self, nonce, clientseed, serverseed):
        hash = hmac.new(self.str2bin(serverseed), self.str2bin(clientseed + "-" + str(nonce)),
                        hashlib.sha512).hexdigest()

        index = 0
        self.luckynumber = int(hash[index:5], 16)


        while (self.luckynumber >= 1e6):
            index += 1
            self.luckynumber = int(hash[index*5:index*5+5],16)

            # we have reached the end of the hash and they all must have been ffffff
            if index * 5 + 5 > 129:
              self.luckynumber = 9999;
              return self.luckeynumber
              break

        return (self.luckynumber % 1e4) * 1e-2

