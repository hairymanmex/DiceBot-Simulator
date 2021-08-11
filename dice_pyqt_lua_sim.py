import matplotlib.pyplot as p
import numpy as np
import hmac
import string
import hashlib
import stake_prng
import bitsler_prng
import wolfbet_prng
import math
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

import lupa
from lupa import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)

'''Need to call the lua objects and variables into python space into 
    object g in order to comunicate back and forth between lua and python'''
g = lua.globals()

# first will have to call the dobet() function to fill the variables and loop
'''resetstats()
   resetbuiltin()  need to pass on these I have certainly missed other methods 
   resetseed()     and variables. Sugestions, request and recomendations are welcome'''

stake_server = ('d8782071e497e4bc7a4e39c0b6c0e507f03c721070d6e12dfd57513c9f68b559',
                '9a7bbd71f048649154c7e1baa7bfe880558cd648d1f93e832d3cc9cdf9957c98')
stake_client = ('e8159d21c1', '151563870')


class Dice:

    def __init__(self, casino):
        self.chance = 57
        self.bethigh = True
        self.nextbet = 1
        self.previousbet = 1
        self.amount = 1
        self.win = False
        self.nonce_start = 1
        self.number_of_rolls = 1000
        self.roll = 1  # this will be the current number generated "lastBet.roll"
        self.basebet = 0
        self.nonce = self.nonce_start  # lastBet.nonce
        self.balance = 0
        self.start_balance = self.balance
        self.currentstreak = 0  # keep track of win and los streak in + and - negative
        self.multiplier = 0
        self.edge = 1
        self.payout = (100 - self.edge) / self.chance
        self.casino = casino
        self.currentprofit = 0

        # self.luckeynumber = 0
        self.serverseed = ""
        self.clientseed = ""
        self.lastbet = 1
        self.profit = 0
        self.id = 'none'
        self.amount = 0
        self.previousbalance = 0
        self.qtplot = False
        self.wins = 0
        self.losses = 0
        self.wager = 0
        self.count = 0
        self.balance_set = np.array([])
        self.balance_set1 = []
        self.bal_count = 0
        self.currency = 'Butcher_Coins!'

    def gen(self):
        self.count += 1
        self.bal_count = 0
        self.previousbalance = self.balance
        self.roll = float(self.casino.generator(self.nonce, self.clientseed, self.serverseed))
        self.winloss()
        self.bal()
        self.nonce += 1



        if self.qtplot == True:
            '''Temporary measures to add a plot. although this only produces a batch plot '''
            self.bal_count += 1
            if self.bal_count > 500000 or g.finish == True:
                self.balance_set = np.append(self.balance_set, self.balance_set1)
                self.balance_set1 = []
                self.bal_count = 0

            else:
                self.balance_set1.append(self.balance)


    def bal(self):
        self.lastbalance = self.balance
        self.wager += self.nextbet
        if self.win:

            self.balance = self.payout * self.nextbet + self.balance - self.nextbet

        else:
            self.balance = self.balance - self.nextbet

        self.profit = self.balance - self.start_balance
        self.currentprofit = self.balance - self.lastbalance

    def winloss(self):

        if self.bethigh == False:
            if self.roll <= self.chance:
                self.win = True
            else:
                self.win = False
        else:
            if self.roll >= (99.99 - self.chance):
                self.win = True
            else:
                self.win = False

        if self.win:
            self.wins += 1
            if self.currentstreak < 0:
                self.currentstreak = 1
            else:
                self.currentstreak += 1
        else:
            self.losses += 1
            if self.currentstreak > 0:
                self.currentstreak = -1
            else:
                self.currentstreak -= 1

    def seeds(self, serverseed, clientseed):
        self.serverseed = serverseed
        self.clientseed = clientseed

    def attribute_update(self):  # need to update object attributes from inside lua
        self.chance = g.chance
        self.nextbet = g.nextbet

        self.bethigh = g.bethigh
        self.payout = (100 - self.edge) / self.chance

    def nonce_update(self):
        self.start_balance = self.balance
        self.nonce = int(self.nonce_start)
        self.nonce_start = int(self.nonce_start)
        self.number_of_rolls = int(self.number_of_rolls)
        self.number_of_rolls = self.number_of_rolls + self.nonce

    def previous(self):
        self.amount = self.previousbet
        self.previousbet = g.nextbet

    def resetstats(self):
        pass

    def resetbuiltin(self):
        pass

    def resetseed(self):
        pass

    def ching(self):
        pass

    def alarm(self):
        pass


lua_func = lua.eval('''
        function(bot,file) -- pass python object into lua space with this function

        finish = false
        function stop()
            number_of_rolls = 0
        end

        bets = 0
        bot.previousbet = bot.nextbet
        balance = bot.balance  
        win = bot.win 
        lastbet = bot.lastbet 
        bethigh = bot.bethigh
        chance = bot.chance
        python.eval('bot1.nonce_update()')
        number_of_rolls = bot.number_of_rolls
        profit = bot.profit
        currentprofit = bot.currentprofit
        currentstreak = bot.currentstreak
        
        resetstats = bot.resetstats
        resetseed = bot.resetseed
        ching = bot.ching
        alarm = bot.alarm
        wager = bot.wager
        currency = bot.currency



        dofile(file) 


        bot.nextbet = nextbet
        bot.previousbet = bot.nextbet
        previousbet = nextbet
        print(previousbet)



        --[[ I found the only way to keep object atributes syncronized between lua 
             and python was to make call within lua out to python. Maybe there is 
             a better way, but I could not figure it out]]--

        if initialize then
            initialize()
        end 
        python.eval('bot1.previous()')
        python.eval('bot1.attribute_update()')
        print(number_of_rolls,bot.nonce)
        while number_of_rolls > bot.nonce do
            python.eval("bot1.gen()")

            bets = bets + 1           
            win = bot.win 
            if win then
                win2 = ' win '
            else
                win2 = ' loss'
            end

            if bot.bethigh then
                high2 = 'high'
            else
                high2 = 'low'
            end

            print(string.format('stake: %2.8f %s balance: %8.8f wager: %8.8f roll: %2.2f nonce: %d bets: %d %s',bot.nextbet,win2,bot.balance,bot.wager,bot.roll,bot.nonce,bets,high2))
            balance = bot.balance  

            lastbet = bot.lastbet 
            nextbet = bot.nextbet
            bethigh = bot.bethigh
            previousbet = bot.previousbet
            lastBet = bot
            profit = bot.profit
            currentprofit = bot.currentprofit
            currentstreak = bot.currentstreak

            wins = bot.wins
            losses = bot.losses
            wagered = bot.wager



            dobet()
            python.eval('bot1.previous()')
            python.eval('bot1.attribute_update()')

            if bot.nextbet > bot.balance then
                break
            end 
        
        end
        finish = true            
    end
    ''')


def pyqtplot(bot1):  #temporary qt window and plot

    y = bot1.balance_set
    plt = pg.plot()
    plt.showGrid(x=True, y=True)
    plt.setLabel('left', 'Balance', units='y')
    plt.setWindowTitle('Random Number Analysis')
    line1 = plt.plot(y, pen='g')

    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


def main():


    script = input("Enter lua script file name: ") or 'rolling_regression.lua'
    server_seed = input(
        "Enter server seed or hit enter for Default: ") or 'b28abbe1828e9aca7563e1bf82e8d28908d80998285d4e145c7a5fe8b7a33bf5'
    client_seed = input("Enter client seed or hit enter for Default: ") or '58c325924f611c2eee6771db70ed9572'
    # nonce = '1143448'

    print('select Casino\n #1 Stake.Com \n #2 Bitsler \n #3 Wolf.bet')
    responce = input(' : ') or 3
    int(responce)
    if responce == 1:
        casino = stake_prng.stake_casino()
    elif responce == 2:
        casino = bitsler_prng.bitsler()
    else:
        casino = wolfbet_prng.wolfbet()

    bot1 = Dice(casino)

    bot1.edge = input('Enter House Edge : ') or 1
    bot1.edge = float(bot1.edge)
    bot1.balance = input('Enter Balance :') or 600.0
    bot1.balance = int(bot1.balance)
    bot1.nonce_start = input('Enter Starting Nonce :') or 1143200
    bot1.number_of_rolls = input('Enter Number of Rolls : ') or 350
    bot1.number_of_rolls = int(bot1.number_of_rolls)
    bot1.seeds(server_seed, client_seed)
    pltrsp = input('Would you like to plot results? Y/N :') or True
    if pltrsp == 'yes' or pltrsp == 'y' or pltrsp == 'Y' or pltrsp == 'Yes' or pltrsp == 'YES':
        bot1.qtplot = True
    else:
        bot1.qtplot = False

    lua_func(bot1, script)


    bot1.gen()

    if bot1.qtplot:
        pyqtplot(bot1)


if __name__ == '__main__':
    main()