from bot.trade_manager import trade_is_open

class StrategyStates:

#in the object Strategy are defined the parameters that can vary during the exectution of the bot
# that are not fixed like TradeSettings 
    def __init__(self, ob, pair , api):
        self.price_trades=[]
        self.unit_trades=[]
        ot = trade_is_open(pair, api)
        if ot == None:
            a=0
        else:
            a=len(ot)
        self.current_n_ot=a
        self.signals=[]


    def __repr__(self):
        return str(vars(self))

    @classmethod
    def strategy_to_str(cls, strategy):
        ret_str = "Strategy:\n"
        for _, v in strategy.items():
            ret_str += f"{v}\n"

        return ret_str