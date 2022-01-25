import threading
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

import lupa1
from lupa1 import LuaRuntime

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
    balance_set = np.array([])
    balance_set1 = []

    def __init__(self, casino):
        self.chance = 1
        self.bethigh = True
        self.nextbet = 0
        self.previousbet = 0
        self.amount = 0
        self.win = False
        self.nonce_start = 0
        self.number_of_rolls = 0
        self.roll = 1  # this will be the current number generated "lastBet.roll"
        self.Roll = self.roll
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
        self.Profit = self.currentprofit

        # self.luckeynumber = 0
        self.serverseed = ""
        self.clientseed = ""
        self.lastbet = 0
        self.profit = 0
        self.id = 'none'
        self.amount = 0
        self.previousbalance = 0
        self.qtplot = False
        self.wins = 0
        self.losses = 0
        self.wager = 0
        self.count = 0

        self.bal_count = -1
        self.currency = 'Butcher Coins!'
        self.roll_average = []
        self.roll_average_chart = []
        self.wincount = 0
        self.losscount = 0
        self.wincount1 = 0
        self.losscount1 = 0
        self.cluster = []
        self.name = casino
        self.roll_number = 0

    def gen(self):
        self.count += 1

        self.previousbalance = self.balance
        self.roll = (self.casino.generator(self.nonce, self.clientseed, self.serverseed))
        print(self.nonce)
        print(self.clientseed)
        print(self.serverseed)
        self.winloss()
        self.bal()
        self.nonce += 1

        if self.qtplot == True:
            '''Temporary measures to add a plot. although this only produces a batch plot '''
            div = 1200
            num = 1
            # self.bal_count += 1
            Dice.balance_set1.append(self.balance)
            '''if self.win:
                self.roll_average.append(1)
                self.roll_average.pop(0)
                self.wincount1 += 1
                if self.losscount1 % 3 == 0:
                    self.cluster.append((((self.losscount1)/div)*-1)+num)
                elif self.losscount1 % 4 == 0:
                    self.cluster.append((((self.losscount1)/div)*-1)+num)
                elif self.losscount1 % 5 == 0:
                    self.cluster.append((((self.losscount1)/div)*-1)+num)
                else:
                    self.cluster.append(num)
                self.losscount1 = 0
            else:
                self.losscount1 += 1
                self.roll_average.append(0)
                self.roll_average.pop(0)
                if self.wincount1 % 3 == 0:
                    self.cluster.append(((self.wincount1)/div)+num)
                elif self.wincount1 % 4 == 0:
                    self.cluster.append(((self.wincount1)/div)+num)
                elif self.wincount1 % 5 == 0:
                    self.cluster.append(((self.wincount1)/div)+num)
                else:
                    self.cluster.append(num)
                self.wincount1 = 0


            self.wincount = 0
            self.losscount = 0
            for i in self.roll_average:
                if i == 1:
                    self.wincount += 1
                else:
                    self.losscount += 1

            average =((self.wincount / (self.wincount+self.losscount))/40)+1
            self.roll_average_chart.append(average)'''

    def bal(self):

        self.lastbalance = self.balance
        self.wager += self.nextbet
        if self.win:

            self.balance = self.payout * self.nextbet + self.balance - self.nextbet

        else:
            self.balance = self.balance - self.nextbet

        self.profit = self.balance - self.start_balance
        self.currentprofit = self.balance - self.lastbalance
        self.Profit = self.balance - self.lastbalance

    def winloss(self):

        if self.bethigh == False:
            if self.roll < self.chance:
                self.win = True
            else:
                self.win = False
        else:
            if self.roll > (math.floor((((99.99 - self.chance) * 100)) + 0.000000000001)) / 100:
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
        self.roll_number = self.number_of_rolls + 1
        self.number_of_rolls = int(self.number_of_rolls + 1)
        # self.balance_set = np.zeros(self.number_of_rolls+1)
        self.number_of_rolls = self.number_of_rolls + self.nonce

    def stop_bot(self):
        self.number_of_rolls = int(0)

    def previous(self):
        self.amount = self.previousbet
        self.previousbet = g.nextbet

    def resetstats(self):
        pass

    def resetbuiltin(self):
        pass

    def resetseed(self):
        self.number_of_rolls += 10000000
        self.nonce += 10000000

    def ching(self):
        pass

    def alarm(self):
        pass


lua_func = lua.eval('''
        function(bot,file) -- pass python object into lua space with this function
        win3 = 0
        finish = false

        lastBet = bot
        site = bot
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
        function stop()
            stopbreak = true        
        end



        dofile(file) 


        bot.nextbet = nextbet
        bot.previousbet = bot.nextbet
        previousbet = nextbet




        --[[ I found the only way to keep object atributes syncronized between lua 
             and python was to make call within lua out to python. Maybe there is 
             a better way, but I could not figure it out]]--

        if initialize then
            initialize()
        end 
        python.eval('bot1.previous()')
        python.eval('bot1.attribute_update()')

        for i = 1, bot.roll_number do
            python.eval("bot1.gen()")

            bets = bets + 1           
            win = bot.win 
            if win then
                win2 = ' win '
                win3 = win3 + 1
            else
                win2 = ' loss'
            end

            if bot.bethigh then
                high2 = 'high'
            else
                high2 = 'low'
            end

            python.eval('bot1.previous()')

            balance = bot.balance  

            lastbet = bot.lastbet 
            nextbet = bot.nextbet
            bethigh = bot.bethigh
            previousbet = bot.previousbet
            lastBet = bot
            site = bot
            profit = bot.profit
            currentprofit = bot.currentprofit
            currentstreak = bot.currentstreak

            wins = bot.wins
            losses = bot.losses
            wagered = bot.wager



            dobet()

            if nextbet < 1e-8 then
                print('Error! Bet is below minimum!')
                break
            end
            python.eval('bot1.attribute_update()')
            print(string.format('stake: %2.8f %s balance: %8.8f wager: %8.8f roll: %2.2f nonce: %d bets: %d chance %2.2f total wins: %d ',previousbet,win2,bot.balance,bot.wager,bot.roll,(bot.nonce-1),bets,chance, win3))

            if bot.nextbet > bot.balance then
                break   
            end 
            if stopbreak then
                print('ching')
                break
            end

        end
        finish = true            
    end
    ''')


def pyqtplot(bot1):  # temporary qt window and plot

    y = Dice.balance_set
    avg = bot1.roll_average_chart
    cluster = bot1.cluster
    plt = pg.plot()
    plt.showGrid(x=True, y=True)
    plt.setLabel('left', 'Balance')
    plt.setWindowTitle('Random Number Analysis')
    line1 = plt.plot(y, pen='g')
    # ,symbol='o', symbolSize=2, symbolBrush=('g'))
    # line2 = plt.plot(avg, pen='b')
    # line3 = plt.plot(cluster, pen='r')

    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


def main():
    avgsize = 25

    print('Shall we play a Game?')
    script = input("Enter lua script file name: ")
    server_seed = input("Enter server seed or hit enter for Default: ") or '9e34592a544e4ac3b2a534d7d56b73fe0d42fc4e6ed297c65d9302632fd7988a'
    client_seed = input("Enter client seed or hit enter for Default: ") or 'Meowcatmeow'

    print('select Casino\n #1 Stake.Com \n #2 Bitsler \n #3 Wolf.bet')
    responce = input(' : ') or 3
    int(responce)
    if responce == "1":
        casino = stake_prng.stake_casino()
    elif responce == "2":
        casino = bitsler_prng.bitsler()
    else:
        casino = wolfbet_prng.wolfbet()

    bot1 = Dice(casino)

    bot1.edge = input('Enter House Edge : ') or 1
    bot1.edge = float(bot1.edge)
    print("edge is", bot1.edge)
    bot1.balance = input('Enter Balance :') or 600.0
    bot1.balance = float(bot1.balance)
    bot1.nonce_start = input('Enter Starting Nonce :') or 1
    bot1.number_of_rolls = input('Enter Number of Rolls : ') or 350
    bot1.number_of_rolls = int(bot1.number_of_rolls)
    bot1.seeds(server_seed, client_seed)
    pltrsp = input('Would you like to plot results? Y/N :') or True
    if pltrsp == 'yes' or pltrsp == 'y' or pltrsp == 'Y' or pltrsp == 'Yes' or pltrsp == 'YES':
        bot1.qtplot = True
    else:
        bot1.qtplot = False

    lua_func(bot1, script)

    print('How about a nice game of chess?')

    if bot1.qtplot:
        Dice.balance_set = np.append(Dice.balance_set, Dice.balance_set1)
        pyqtplot(bot1)


if __name__ == '__main__':
    main()