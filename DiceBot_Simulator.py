import numpy as np
import re
import hmac
import random
import hashlib
import justdice_prng, primedice_prng, stake_prng, bitsler_prng, wolfbet_prng
import math
from PyQt5.QtWidgets import *
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets

import lupa
from lupa import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)

'''Need to call the lua objects and variables into python space into 
    object g in order to comunicate back and forth between lua and python'''
g = lua.globals()


class Dice:
    profit_set = np.array([])
    profit_set1 = []

    def __init__(self, casino_prng, casino_name):
        self.Name = 'Butcher_Simulation!'
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
        self.vault_balance = 0
        self.start_balance = self.balance
        self.currentstreak = 0  # keep track of win and los streak in + and - negative
        self.longest_loss_streak = 0
        self.multiplier = 0
        self.Edge = 1
        self.payout = (100 - self.Edge) / self.chance
        self.casino = casino_prng
        self.casino_name = casino_name
        self.currentprofit = 0
        self.Profit = 0
        self.partialprofit = 0

        # self.luckeynumber = 0
        self.serverseed = ""
        self.clientseed = ""
        self.lastbet = 0
        self.profit = 0
        self.id = 'Forks_and_Knives'
        self.previousbalance = 0
        self.qtplot = False
        self.wins = 0
        self.losses = 0
        self.wager = 0
        self.counter = 0

        self.bal_count = -1
        self.currency = 'Butcher Coins!'
        self.roll_average = []
        self.roll_average_chart = []
        self.wincount = 0
        self.losscount = 0
        self.wincount1 = 0
        self.losscount1 = 0
        self.cluster = []
        self.loss_streaks = []
        self.roll_number = 0

        self.CanVault = False

    def gen(self):

        self.previousbalance = self.balance
        self.roll = (self.casino.generator(self.nonce, self.clientseed, self.serverseed))
        self.winloss()
        self.bal()
        self.nonce += 1

        if self.qtplot == True:
            '''Temporary measures to add a plot. although this only produces a batch plot '''
            div = 1200
            num = 1
            # self.bal_count += 1
            Dice.profit_set1.append(self.profit)
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
        # self.balance = 1
        self.counter += 1
        self.lastbalance = self.balance
        self.wager += self.nextbet
        if self.win:
            self.currentprofit = 0
            self.balance = self.payout * self.nextbet + self.balance - self.nextbet
            self.currentprofit = self.payout * self.nextbet - self.nextbet
        else:
            self.currentprofit = 0
            self.balance = self.balance - self.nextbet
            self.currentprofit = self.currentprofit - self.nextbet

        self.profit += self.currentprofit
        self.Profit += self.currentprofit
        self.partialprofit += self.currentprofit

    def winloss(self):
        if self.casino_name == "stake":
            stake = (math.floor((((100 - self.chance) * 100)) + 0.000000001)) / 100
        elif self.casino_name == "justdice":
            stake = (math.floor((((100 - self.chance - 0.0001) * 10000)) + 0.000000001)) / 10000
        else:
            stake = (math.floor((((100 - self.chance - 0.01) * 100)) + 0.000000001)) / 100

        if self.bethigh == False:
            if self.roll < self.chance:
                self.win = True
            else:
                self.win = False
        else:
            if self.roll > stake:
                self.win = True
            else:
                self.win = False

        if self.win:
            self.wins += 1
            if self.currentstreak < 0:
                self.loss_streaks.append(-self.currentstreak)
                self.currentstreak = 1
            else:
                self.currentstreak += 1
        else:
            self.losses += 1
            if self.currentstreak > 0:
                self.currentstreak = -1
            else:
                self.currentstreak -= 1

        if self.currentstreak < self.longest_loss_streak:
            self.longest_loss_streak = self.currentstreak

    def seeds(self, serverseed, clientseed):
        self.serverseed = serverseed
        self.clientseed = clientseed

    def attribute_update(self):  # need to update object attributes from inside lua
        self.chance = math.floor(g.chance * 100) / 100

        if self.chance > 99.99:
            self.chance = 99.99
        elif self.chance < 0.01:
            self.chance = 0.01
        self.nextbet = g.nextbet
        self.bethigh = g.bethigh
        self.payout = (100 - self.Edge) / self.chance

    def nonce_update(self):
        self.start_balance = self.balance
        self.nonce = int(self.nonce_start)
        self.nonce_start = int(self.nonce_start)
        self.roll_number = self.number_of_rolls
        self.number_of_rolls = int(self.number_of_rolls)
        # self.balance_set = np.zeros(self.number_of_rolls+1)
        self.number_of_rolls = self.number_of_rolls + self.nonce

    def stop_bot(self):
        self.number_of_rolls = int(0)

    def previous(self):
        self.amount = self.previousbet
        self.previousbet = g.nextbet

    def resetstats(self):
        self.profit = 0
        self.wins = 0
        self.bets = 0
        self.losses = 0

    def resetbuiltin(self):
        pass

    def resetpartialprofit(self):
        print('reseting!!!!')
        self.partialprofit = 0
        g.partialprofit = 0

    def resetseed(self):

        key = math.floor(random.random() * 1e16)
        key1 = math.floor(random.random() * 1e16)
        key = str(key)
        key1 = str(key)
        key = key + key1

        key = bytes(key, 'UTF-8')
        message = math.floor(random.random() * 1e16)
        message = str(message)
        message = bytes(message, 'UTF-8')

        seed = hmac.new(key, message, hashlib.sha512).hexdigest()

        if self.casino_name == "stake":
            self.serverseed = seed[0:54]
            self.clientseed = seed[110:120]
        elif self.casino_name == "bitsler":
            self.serverseed = seed[0:64]
            self.clientseed = seed[110:126]
        elif self.casino_name == "wolf":
            self.serverseed = seed[0:64]
            self.clientseed = seed[105:125]
        elif self.casino_name == "prime":
            self.serverseed = seed[0:54]
            self.clientseed = seed[110:120]
        elif self.casino_name == "justdice":
            self.serverseed = seed[0:54]
            self.clientseed = seed[100:124]

        self.nonce = 1

    def ching(self):
        print('ching')

    def alarm(self):
        pass

    def vault(self, value):
        self.vault_balance += value
        self.balance -= value


lua_start = lua.eval('''
        function(bot) -- pass python object into lua space with this function
        win3 = 0
        finish = false      
        lastBet = bot
        site = bot
        bets = 1

        bot.previousbet = bot.nextbet
        balance = bot.balance  
        win = bot.win 
        lastbet = bot       

        python.eval('bot1.nonce_update()')
        number_of_rolls = bot.number_of_rolls
        profit = bot.profit
        currentprofit = bot.currentprofit
        currentstreak = bot.currentstreak


        resetpartialprofit = bot.resetpartialprofit
        vault = bot.vault
        resetstats = bot.resetstats
        resetseed = bot.resetseed
        ching = bot.ching
        alarm = bot.alarm
        wager = bot.wager
        currency = bot.currency
        function stop()
            stopbreak = true        
        end
        function wait(a) 
            local sec = tonumber(os.clock() + a); 
            while (os.clock() < sec) do 
            end 
        end

        --[[function wait(seconds)
            local start = os.time()
            repeat until os.time() > start + seconds
        end--]]

        --dofile(file) 


        bot.nextbet = nextbet
        bot.previousbet = bot.nextbet
        previousbet = nextbet
        lastchance = chance


        --[[ I found the only way to keep object atributes syncronized between lua 
             and python was to make call within lua out to python. Maybe there is 
             a better way, but I could not figure it out--]]

        if initialize then
            initialize()
        end 

        end
        ''')

lua_func = lua.eval('''
        function(bot) -- pass python object into lua space with this function



        number_of_rolls = bot.number_of_rolls
        profit = bot.profit
        currentprofit = bot.currentprofit
        currentstreak = bot.currentstreak


        resetpartialprofit = bot.resetpartialprofit
        resetstats = bot.resetstats
        resetseed = bot.resetseed
        ching = bot.ching
        alarm = bot.alarm
        wager = bot.wager
        currency = bot.currency
        function stop()
            stopbreak = true        
        end
        function wait(a) 
            local sec = tonumber(os.clock() + a); 
            while (os.clock() < sec) do 
            end 
        end

        --[[function wait(seconds)
            local start = os.time()
            repeat until os.time() > start + seconds
        end--]]

        --dofile(file) 


        bot.nextbet = nextbet
        bot.previousbet = bot.nextbet
        previousbet = nextbet
        lastchance = chance


        --[[ I found the only way to keep object atributes syncronized between lua 
             and python was to make call within lua out to python. Maybe there is 
             a better way, but I could not figure it out--]]

        if initialize then
            initialize()
        end 
        python.eval('bot1.previous()')
        python.eval('bot1.attribute_update()')

        if nextbet < 0 then
            print('Error! Bet is below minimum!')


        elseif nextbet > bot.balance then
            print(nextbet)
            print('bet exceeds balance')             

        elseif nextbet < 1e-8 then
            print('Bet below minbet')            

        else
            for i = 1, bot.roll_number do
                python.eval("bot1.gen()")

                --bets = bets + 1           
                win = bot.win 
                if win then
                    win2 = 'win'
                    win3 = win3 + 1
                else
                    win2 = 'loss'
                end

                if bot.bethigh then
                    high2 = 'high'
                else
                    high2 = 'low'
                end

                python.eval('bot1.previous()')

                bets = bot.counter
                balance = bot.balance
                vault_balance = bot.vault_balance          
                lastbet = bot.lastbet 
                nextbet = bot.nextbet
                bethigh = bot.bethigh
                previousbet = bot.previousbet
                lastBet = bot
                site = bot
                profit = bot.profit
                currentprofit = bot.currentprofit
                currentstreak = bot.currentstreak
                partialprofit = bot.partialprofit


                wins = bot.wins
                losses = bot.losses
                wagered = bot.wager



                dobet()
                --wait(0.2)
                if nextbet < 0 then
                    print('Error! Bet is below minimum!')
                    break
                end
                if nextbet > bot.balance then
                    print(nextbet)
                    print('bet exceeds balance')
                    break   
                end
                if nextbet == 0 then
                elseif nextbet < 1e-8 then
                    print('Bet below minbet')
                    break
                end
                python.eval('bot1.attribute_update()')
                print(string.format('stake: %2.8f balance: %8.8f vaulted: %8.8f wager: %8.8f roll: %2.4f nonce: %d bets: %d chance: %2.2f This round:%s',previousbet,bot.balance,bot.vault_balance,bot.wager,bot.roll,(bot.nonce-1),bets,lastchance,win2))
                lastchance = chance
                if bot.nextbet > bot.balance then
                    print(bot.nextbet)
                    print('bet exceeds balance')
                    break   
                end
                if bot.nextbet == 0 then
                elseif bot.nextbet < 1e-8 then
                    print('Bet below minbet')
                    break
                end

                if stopbreak then
                    print('ching')
                    break
                end
                --wait(0.01)            
            end
        end
        finish = true            
    end
    ''')


def pyqtplot(bot1):  # temporary qt window and plot -depricated versin of qt window

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
        QtWidgets.QApplication(sys.argv).instance().exec_()
        # QtGui.QApplication.instance().exec_()


class MainWindow(QMainWindow):  # going to build out this aplication anyway

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.mainbox = QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QVBoxLayout())

        self.butcher_graph = pg.GraphicsLayoutWidget()
        self.butcher_graph.setBackground((40, 40, 40))
        self.mainbox.layout().addWidget(self.butcher_graph)

        self.butcher_plot = self.butcher_graph.addPlot()
        self.butcher_plot.showGrid(x=True, y=True)
        self.butcher_plot.setLabel('left', 'Profit')
        self.butcher_plot.plot(Dice.profit_set, pen='g')
        self.show()


def operations(script):
    new = re.sub("!=", "~=", script)
    new = re.sub("!", "not ", new)
    new = re.sub("([a-zA-Z0-9]*\s*)\+\=(\s*.*)", r'\1 = \1 + (\2)', new)
    new = re.sub("([a-zA-Z0-9]*\s*)\-\=(\s*.*)", r'\1 = \1 - (\2)', new)
    new = re.sub("([a-zA-Z0-9]*\s*)\*\=(\s*.*)", r'\1 = \1 * (\2)', new)
    new = re.sub("([a-zA-Z0-9]*\s*)\/\=(\s*.*)", r'\1 = \1 / (\2)', new)
    return new


def main():
    avgsize = 25

    print('Shall we play a Game?')
    script = input("Enter lua script file name: ")

    print('select Casino\n #1 Stake.Com \n #2 Primedice.com \n #3 Bitsler \n #4 Wolf.bet \n #5 Just-dice')
    responce = input(' : ') or "5"

    if responce == "1":
        print('Stake.com selected')
        casino_prng = stake_prng.stake_casino()
        casino_name = "stake"
    elif responce == "2":
        print('Primedice.com selected')
        casino_prng = primdice_prng.primedice()
        casino_name = "prime"
    elif responce == "3":
        print('Bitsler.com selected')
        casino_prng = bitsler_prng.bitsler()
        casino_name = "bitsler"
    elif responce == "4":
        print('Wolf.bet Selected')
        casino_prng = wolfbet_prng.wolfbet()
        casino_name = "wolf"
    elif responce == "5":
        print('Just-dice.com selected')
        casino_prng = justdice_prng.justdice()
        casino_name = "justdice"

    server_seed = input(
        "Enter server seed or hit enter for Default: ") or '9e34592a544e4ac3b2a534d7d56b73fe0d42fc4e6ed297c65d9302632fd7988a'
    client_seed = input("Enter client seed or hit enter for Default: ") or 'Meowcatmeow'

    bot1 = Dice(casino_prng, casino_name)

    bot1.edge = input('Enter House Edge : ') or 1
    bot1.edge = float(bot1.edge)
    print("edge is", bot1.edge)
    bot1.balance = input('Enter Balance :') or 600.0
    bot1.balance = float(bot1.balance)
    bot1.nonce_start = input('Enter Starting Nonce :') or 1
    bot1.number_of_rolls = input('Enter Number of Rolls : ') or 350
    bot1.number_of_rolls = int(bot1.number_of_rolls)
    bot1.seeds(server_seed, client_seed)
    pltrsp = input('Would you like to plot results? Y/N :') or 'Y'
    if pltrsp == 'yes' or pltrsp == 'y' or pltrsp == 'Y' or pltrsp == 'Yes' or pltrsp == 'YES':
        bot1.qtplot = True
    else:
        bot1.qtplot = False

    text_file = open(script, "r")
    data = text_file.read()
    text_file.close()
    data2 = operations(data)
    g.script = data2
    lua.execute('load(script)()')

    lua_func(bot1)

    print('How about a nice game of chess?')

    if bot1.qtplot:
        Dice.profit_set = np.append(Dice.profit_set, Dice.profit_set1)
        app = QApplication([])
        app.setStyleSheet("""
                                QWidget {
                                    background-color: rgb(40,40,40);
                                    color: rgb(200,200,200);
                                }

                            """)
        window = MainWindow()
        app.exec_()
        # pyqtplot(bot1)


if __name__ == '__main__':
    main()