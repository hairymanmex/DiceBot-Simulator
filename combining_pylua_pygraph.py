from PyQt5.QtGui import *
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pyqtgraph as pg
import random
import time
import traceback, sys
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

''' threading code from https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/'''

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(object,object,bool)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()


        # Add the callback to our kwargs
        self.kwargs['progress'] = self.signals.progress


    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)

        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done



class MainWindow(QMainWindow):


    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)



        #layout = QVBoxLayout()
        self.mainbox = QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QVBoxLayout())

        self.main_graph = pg.GraphicsLayoutWidget()
        self.mainbox.layout().addWidget(self.main_graph)

        self.label = QLabel()
        self.mainbox.layout().addWidget(self.label)



        b = QPushButton("Start Simulation")
        b.pressed.connect(self.Simulation)



        self.mainbox.layout().addWidget(b)

        self.s_nonce = QLineEdit('Starting Nonce')
        self.s_nonce.setGeometry(20, 20, 50, 20)
        #self.s_nonce.selectAll()
        self.mainbox.layout().addWidget(self.s_nonce)
        self.s_nonce.returnPressed.connect(lambda: do_action())

        self.f_nonce = QLineEdit('Finishing Nonce')
        self.f_nonce.selectAll()
        self.mainbox.layout().addWidget(self.f_nonce)
        self.f_nonce.returnPressed.connect(lambda: do_action())


        self.s_seed = QLineEdit('Server Seed')
        self.s_seed.selectAll()
        self.mainbox.layout().addWidget(self.s_seed)
        self.s_seed.returnPressed.connect(lambda: do_action())

        self.c_seed = QLineEdit('Client Seed')
        self.c_seed.selectAll()
        self.mainbox.layout().addWidget(self.c_seed)
        self.c_seed.returnPressed.connect(lambda: do_action())  # need to send seeds to apropriate variables




        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())


        #  line plot
        self.otherplot = self.main_graph.addPlot()


        self.h2 = self.otherplot.plot(pen='r')
        self.h3 = self.otherplot.plot(pen='g')

        #### Set Data  #####################
        self.o = 0
        self.datacount = 0
        self.a1 = [00,25]
        self.a2 = [00]
        self.a3 = [00]
        self.a4 = [100,150]
        self.x1 = [00,200]



        self.x = np.linspace(0, 50., num=100)
        self.X, self.Y = np.meshgrid(self.x, self.x)

        self.counter = 0
        self.fps = 0.
        self.lastupdate = time.time()

        #### Start  #####################
        self.show()



    def progress_fn(self, nonceset, luckyarray, win):

        if win:
            self.otherplot.plot(nonceset,luckyarray,pen='g')
        else:
            self.otherplot.plot(nonceset,luckyarray, pen='r')

    def print_output(self, s):
        print(s)



    def thread_complete(self):
        print("THREAD COMPLETE!")

    def Simulation(self):
        # Pass the function to execute
        prg = Dice()
        worker = Worker(prg.execute_this_fn) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.print_output)  #prints return of for loop
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.threadpool.start(worker)






stake_server =('d8782071e497e4bc7a4e39c0b6c0e507f03c721070d6e12dfd57513c9f68b559',
                '9a7bbd71f048649154c7e1baa7bfe880558cd648d1f93e832d3cc9cdf9957c98')
stake_client = ('e8159d21c1', '151563870')


class Dice:

    def __init__(self,*args, **kwargs):
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
        self.balance = 100000
        self.start_balance = self.balance
        self.currentbalance = self.balance
        self.currentprofit = 0
        self.currentstreak = 0  # keep track of win and los streak in + and - negative
        self.multiplier = 0
        self.edge = 1
        self.payout = (100 - self.edge) / self.chance
        self.casino = 'casino'

        # self.luckeynumber = 0
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
            luckyarray, nonceset = luckyset(self.previousbalance, self.balance, self.nonce)


            self.progress.emit(nonceset, luckyarray, self.win)

    def bal(self):
        if self.win:

            self.balance = self.payout * self.nextbet + self.balance - self.nextbet

        else:
            self.balance = self.balance - self.nextbet

        self.profit = self.balance - self.start_balance
        self.currentprofit = self.currentbalance - self.start_balance

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

    def seeds(self, serverseed, clientseed):
        self.serverseed = serverseed
        self.clientseed = clientseed

    def attribute_update(self):  # need to update object attributes from inside lua
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

    def execute_this_fn(self,progress):
        self.progress = progress
        script = 'yan_text.lua'
        casino = stake_prng.stake_casino()
        # casino = bitsler_prng.bitsler()
        # casino = wolfbet_prng.wolfbet()
        self.casino = casino

        self.plot = True
        self.edge = 0
        self.balance = 1.0
        self.number_of_rolls = 10000
        self.seeds(stake_server[1], stake_client[1])
        lua_func(self, script)

        #progress.emit(n * 100 / 4)  # ?????



        return "Done."



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

        python.eval('self.attribute_update()')
        while bot.number_of_rolls > bot.nonce do
            python.eval("self.gen()")
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
            python.eval('self.previous()')
            python.eval('self.attribute_update()')

            if bot.nextbet > bot.balance then
                break
            end 

        end            
    end
    ''')




def luckyset(previousluck, luckynumber, nonce):  # this can be used for sets of numbers or wins and losses
    nonceset = []
    luckeyset = []
    luckeynumberarray = []
    luckeytally = []

    nonceset.append(nonce - 1)
    nonceset.append(nonce)

    luckeyset.append(previousluck)
    luckeyset.append(luckynumber)  # store only the last two numbers

    #luckeynumberarray.append(luckynumber)  # store all generated numbers  -- this hogs memory

    return luckeyset, nonceset


class progress:

    def __init__(self):
        self.bob = 0






def script():
    script = 'yan_text.lua'
    casino = stake_prng.stake_casino()
    # casino = bitsler_prng.bitsler()
    # casino = wolfbet_prng.wolfbet()
    bot1 = Dice(casino)

    bot1.plot = True
    bot1.edge = 0
    bot1.balance = 1.0
    bot1.number_of_rolls = 10000
    bot1.seeds(stake_server[1], stake_client[1])
    lua_func(bot1, script)

def main():

    app = QApplication([])
    window = MainWindow()
    app.exec_()





if __name__ == '__main__':
    main()