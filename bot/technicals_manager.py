import pandas as pd
from models.trade_decision import TradeDecision

from technicals.indicators import BollingerBands

pd.set_option('display.max_columns', None)
pd.set_option('expand_frame_repr', False)
# comment1


from api.oanda_api import OandaApi

# inside trade_settings there are useful information like strategy : trade_setting.strategy
from models.trade_settings import TradeSettings
import constants.defs as defs

ADDROWS = 20

def apply_signal(row, trade_settings: TradeSettings,  strategy_state):

    strategy_state.check_status(trade_settings.pair, OandaApi)
    if trade_settings.strategy == "MD":
        if strategy_state.current_n_ot == 0:
            return defs.BUY2
        if strategy_state.current_n_ot == 2:
            return defs.NONE
        if strategy_state.current_n_ot == 1:
            if strategy_state.signals[0] == defs.BUY:
                return defs.SELL
            if strategy_state.signal[0] == defs.SELL:
                return defs.BUY

    # for the first purchase the approach is the usual: trigger Bollinger
    if strategy_state.current_n_ot == 0:


        if row.SPREAD <= trade_settings.maxspread and row.GAIN >= trade_settings.mingain:
            if row.mid_c > row.BB_UP and row.mid_o < row.BB_UP:
                return defs.SELL
            elif row.mid_c < row.BB_LW and row.mid_o > row.BB_LW:
                return defs.BUY
        else: return defs.NONE
    
    if strategy_states.current_n_ot %2 == 1:

        if strategy_states.signals[0] == defs.BUY:
            # in case the mid_c is lower than delta_sl_tp of price of first trade
            # and there are uneven trades and the first was a BUY order
            if row.mid_c < strategy_states.price_trades[0]-trade_settings.delta_sl_tp:
                return defs.SELL # we have to specify, after, units and tp/sl
        if strategy_states.signals[0]==defs.SELL:
            if row.mid_c > strategy_states.price_trades[0]+trade_settings.delta_sl_tp:
                return defs.BUY # the opposite of previous one
    elif strategy_states.current_n_ot > 1 and strategy_states.current_n_ot%2==0 : # so, there is a sell/buy or a buy/sell trades, in even number
        if strategy_states.signals[0]==defs.BUY:
            if row.mid_c > strategy_states.prices[0]:
                return defs.BUY

        if strategy_states.signals[0]==defs.SELL:
            if row.mid_c < strategy_states.price_trades[0]:
                return defs.SELL

    return defs.NONE     


def apply_SL(row, trade_settings: TradeSettings):
    # riskreward is set in settings.json and GAIN is in process_candles , below in technicals_manager, as  abs(df.mid_c
    # - df.BB_MA)
    # therefore, gain depends on Bollinger calculation
    if row.SIGNAL == defs.BUY:
        return row.mid_c - (row.GAIN / trade_settings.riskreward)
    elif row.SIGNAL == defs.SELL:
        return row.mid_c + (row.GAIN / trade_settings.riskreward)
    return 0.0

def apply_TP(row):
    # TakeProfit is set as mid_c + GAIN, where GAIN depends on abs(mid_c - BB_MA)
    if row.SIGNAL == defs.BUY:
        return row.mid_c + row.GAIN
    elif row.SIGNAL == defs.SELL:
        return row.mid_c - row.GAIN
    return 0.0


def process_candles(df: pd.DataFrame, pair, trade_settings: TradeSettings, log_message, strategy_states):

    df.reset_index(drop=True, inplace=True)
    df['PAIR'] = pair
    df['SPREAD'] = df.ask_c - df.bid_c

    df = BollingerBands(df, trade_settings.n_ma, trade_settings.n_std)
    df['GAIN'] = abs(df.mid_c - df.BB_MA)
    df['SIGNAL'] = df.apply(apply_signal, axis=1, trade_settings=trade_settings, strategy_states=strategy_states)
    df['TP'] = df.apply(apply_TP, axis=1)
    df['SL'] = df.apply(apply_SL, axis=1, trade_settings=trade_settings)
    df['LOSS'] = abs(df.mid_c - df.SL)

    log_cols = ['PAIR', 'time', 'mid_c', 'mid_o', 'SL', 'TP', 'SPREAD', 'GAIN', 'LOSS', 'SIGNAL', 'BB_UP', 'BB_LW',
                'BB_MA']
    log_message(f"process_candles:\n{df[log_cols].tail()}", pair)

    return df[log_cols].iloc[-1]


def fetch_candles(pair, row_count, candle_time, granularity,
                    api: OandaApi, log_message):

    df = api.get_candles_df(pair, count=row_count, granularity=granularity)

    if df is None or df.shape[0] == 0:
        log_message("tech_manager fetch_candles failed to get candles", pair)
        return None
    
    if df.iloc[-1].time != candle_time:
        log_message(f"tech_manager fetch_candles {df.iloc[-1].time} not correct", pair)
        return None
    return df

def get_trade_decision(candle_time, pair, granularity, api: OandaApi, 
         trade_settings: TradeSettings, log_message, strategy_states):

    max_rows = trade_settings.n_ma + ADDROWS

    log_message(f"tech_manager: max_rows:{max_rows} candle_time:{candle_time} granularity:{granularity}", pair)

    df = fetch_candles(pair, max_rows, candle_time,  granularity, api, log_message)

    if df is not None:
        last_row = process_candles(df, pair, trade_settings, log_message, strategy_states)
        return TradeDecision(last_row)

    return None


