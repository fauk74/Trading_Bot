class TradeSettings:

    def __init__(self, ob, pair):
        self.n_ma = ob['n_ma']
        self.n_std = ob['n_std']
        self.maxspread = ob['maxspread']
        self.mingain = ob['mingain']
        self.riskreward = ob['riskreward']
        self.strategy=ob['strategy']
        self.dim_lot=ob['dim_lot']
        self.max_open_trades=len(self.dim_lot)
        self.sl=ob['sl']
        self.tp=ob['tp']
        self.delta_sl_tp=self.sl-self.tp
        self.size=ob['size']
    def __repr__(self):
        return str(vars(self))

    @classmethod
    def settings_to_str(cls, settings):
        ret_str = "Trade Settings:\n"
        for _, v in settings.items():
            ret_str += f"{v}\n"

        return ret_str