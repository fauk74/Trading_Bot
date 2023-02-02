from bot.trade_manager import trade_is_open, trade_are_open
import numpy as np
from constants.defs import BUY, SELL, NONE
class StrategyStates:

#in the object StrategyStates are defined the parameters that can vary during the exectution of the bot
# that are not fixed like TradeSettings
# those parameters are saved in lists. See function reset

    def __init__(self, ob, pair , api):
        self.price_trades=[]
        self.unit_trades=[]
        self.signals=[]
        self.current_n_ot=0
        self.open_trades=[]
        self.sl=0
        self.tp=0
        # through the parameters escalations we will manage the rise of the order-based strategy
        self.escalationbuy=0
        self.escalationsell=0
        self.reset(pair, api)

    def update(self, price, signal, units):
        self.price_trades.append(price)
        self.unit_trades.append(units)
        self.current_n_ot += 1
        self.signals.append(signal)

    def reset(self, pair, api):
        self.price_trades = []
        self.unit_trades = []
        self.current_n_ot = 0
        self.signals = []
        self.sl = 0
        self.tp = 0
        self.open_trades= []
        self.escalationbuy = 0
        self.escalationsell = 0
        self.check_open_trades(pair, api)

    def check_status(self, pair, api):
        # please note that this function updates the open trades but does not reset the escalationbuy/sell
        self.price_trades = []
        self.unit_trades = []
        self.current_n_ot = 0
        self.signals = []
        self.check_open_trades(pair, api)

    def check_open_trades(self, pair, api):
        list_open_trades = trade_are_open(pair, api)
        a = len(list_open_trades)
        if a > 0:
            for ot in list_open_trades:
                # a=len(trades)
                c = []
                # for b in trades:
                d = ot.currentUnits
            self.price_trades.append(ot.price)
            self.unit_trades.append(d)
            if d < 0:
                f = SELL
            else:
                f = BUY
            c.append(f)
            self.signals = c

    def __repr__(self):
        return str(vars(self))

    @classmethod
    def strategy_to_str(cls, strategy):
        ret_str = "Strategy:\n"
        for _, v in strategy.items():
            ret_str += f"{v}\n"

        return ret_str