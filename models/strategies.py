from bot.trade_manager import trade_is_open
import numpy as np

class StrategyStates:

#in the object Strategy are defined the parameters that can vary during the exectution of the bot
# that are not fixed like TradeSettings 
    def __init__(self, ob, pair , api):
        self.price_trades=[]
        self.unit_trades=[]
        ot = trade_is_open(pair, api)
        self.signals=[]
        if ot == None:
            a=0
        else:
            trades=ot['trades']

            a=len(trades)
            c=[]
            for b in trades:
                d=b['currentUnits']
                c.append(d / np.abs( d) )
            self.signals = c
            # da scrivere una funzione che calcola BENE  len(ot)
            # ricordarsi che per ogni open trade ci deve essere una corrispondenza in signals
        self.current_n_ot=a

        self.sl=0
        self.tp=0


    def update(self, price, signal, units):
        self.price_trades.append(price)
        self.unit_trades.append(units)
        self.current_n_ot += 1
        self.signals.append(signal)

    def reset(self):
        self.price_trades = []
        self.unit_trades = []
        self.current_n_ot = 0
        self.signals = []
        self.sl = 0
        self.tp = 0

    def __repr__(self):
        return str(vars(self))

    @classmethod
    def strategy_to_str(cls, strategy):
        ret_str = "Strategy:\n"
        for _, v in strategy.items():
            ret_str += f"{v}\n"

        return ret_str