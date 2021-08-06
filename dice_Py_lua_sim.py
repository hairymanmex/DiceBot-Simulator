import matplotlib.pyplot as p
import numpy as np
import hmac
import string
import hashlib
import stake_prng
import bitsler_prng
import wolfbet_prng
import math
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



stake_server =('d8782071e497e4bc7a4e39c0b6c0e507f03c721070d6e12dfd57513c9f68b559','9a7bbd71f048649154c7e1baa7bfe880558cd648d1f93e832d3cc9cdf9957c98')
stake_client =('e8159d21c1','151563870')

class Dice:

    def __init__(self,casino):
        self.chance = 57
        self.bethigh = True
        self.nextbet = 1
        self.previousbet = 1
        self.amount = 1
        self.win = False
        self.nonce_start = 1
        self.number_of_rolls = 1000
        self.roll = 1       # this will be the current number generated "lastBet.roll"
        self.basebet = 0
        self.nonce = self.nonce_start  # lastBet.nonce
        self.balance = 100000
        self.start_balance = self.balance
        self.currentstreak = 0  # keep track of win and los streak in + and - negative
        self.multiplier = 0
        self.edge = 1
        self.payout = (100-self.edge) / self.chance
        self.casino = casino
        self.currentprofit = 0


        #self.luckeynumber = 0
        self.serverseed = ""
        self.clientseed = ""
        self.lastbet = 1
        self.profit = 0
        self.id = 'none'
        self.amount = 0
        self.previousbalance = 0
        self.plot = False




    def gen(self):

        self.previousbalance = self.balance
        self.roll = self.casino.generator(self.nonce, self.clientseed, self.serverseed)
        self.winloss()
        self.bal()
        self.nonce += 1

        if self.plot == True:
            '''Temporary measures to add a plot. although this only produces a batch plot 
            its slow and takes a lot of memory'''
            luckyarray, nonceset = luckyset(self.previousbalance,self.balance,self.nonce)
            plotbet(nonceset, luckyarray, self.win)

    def bal(self):
        if self.win:

            self.balance = self.payout * self.nextbet + self.balance - self.nextbet

        else:
            self.balance = self.balance - self.nextbet

        self.profit = self.balance - self.start_balance

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

    def seeds(self,serverseed,clientseed):
        self.serverseed = serverseed
        self.clientseed = clientseed

    def attribute_update(self):         # need to update object attributes from inside lua
        self.chance = g.chance
        self.nextbet = g.nextbet
        self.bethigh = g.bethigh
        self.payout = 99 / self.chance

    def previous(self):
        self.amount = self.previousbet
        self.previousbet = g.nextbet

    def resetstats(self):
        pass

    def resetbuiltin(self):
        pass

    def resetseed(self):
        pass

lua_func = lua.eval('''
        function(bot,file) -- pass python object into lua space with this function
        
        bot.previousbet = bot.nextbet
        balance = bot.balance  
        win = bot.win 
        lastbet = bot.lastbet 
        bethigh = bot.bethigh
        chance = bot.chance
        previousbet = bot.previousbet
        
        
            
        dofile(file) 
        
        bot.nextbet = nextbet
       
      
        
        
        --[[ I found the only way to keep object atributes syncronized between lua 
             and python was to make call within lua out to python. Maybe there is 
             a better way, but I could not figure it out]]--
        
        if initialize then
            initialize()
        end 
        
        python.eval('bot1.attribute_update()')
        while bot.number_of_rolls > bot.nonce do
            python.eval("bot1.gen()")
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
            
            print(string.format('stake: %2.8f %s balance: %8.8f roll: %2.2f %s',bot.nextbet,win2,bot.balance,bot.roll,high2))
            balance = bot.balance  
            
            lastbet = bot.lastbet 
            nextbet = bot.nextbet
            bethigh = bot.bethigh
            previousbet = bot.previousbet
            lastBet = bot
            
            
            
            dobet()
            python.eval('bot1.previous()')
            python.eval('bot1.attribute_update()')
            
            if bot.nextbet > bot.balance then
                break
            end 
                      
        end            
    end
    ''')

def plotbet(nonceset,figure,winloss):

    if winloss:
        winloss = 'green'
    else:
        winloss = 'red'

    p.plot(nonceset, figure, label="Line 2", color=winloss, linestyle="solid", linewidth=0.5, marker="o",
       markerfacecolor="gray", markersize=0.5)

    return

def plotshow():
    # Giving Label to x-axis
    p.xlabel("Roll Number")

    # Giving Label to y-axis
    p.ylabel("Balance")

    # Giving Title To Plotted Graph
    p.title("Random Number Analysis")

    p.grid()
    # DISPLAY the plot
    p.show()
    return

def luckyset(previousluck, luckynumber, nonce):        # this can be used for sets of numbers or wins and losses
    nonceset = []
    luckeyset = []
    luckeynumberarray = []
    luckeytally = []

    nonceset.append(nonce-1)
    nonceset.append(nonce)

    luckeyset.append(previousluck)
    luckeyset.append(luckynumber)           # store only the last two numbers

    luckeynumberarray.append(luckynumber)   # store all generated numbers

    return luckeyset, nonceset

def main():
    script = 'yan_text.lua'
    casino = stake_prng.stake_casino()
    #casino = bitsler_prng.bitsler()
    #casino = wolfbet_prng.wolfbet()
    bot1 = Dice(casino)

    bot1.plot = True
    bot1.edge = 0
    bot1.balance = 1.0
    bot1.number_of_rolls = 10000
    bot1.seeds(stake_server[1],stake_client[1])
    lua_func(bot1,script)
    plotshow()

if __name__ == '__main__':
    main()