
# Trade manager is the module where , according to the strategy, the placed orders and the state of the strategy ,
# an order is placed
# place_trade is called

from api.oanda_api import OandaApi
from bot.trade_risk_calculator import get_trade_units
from models.trade_decision import TradeDecision
from bot.strategy_calculator import strategy_units , strategy_sl_tp
from bot.telegram import send_message

def trade_is_open(pair, api: OandaApi):

    open_trades = api.get_open_trades()

    if open_trades != None:
        for ot in open_trades:
            if ot.instrument == pair:
                print(ot)
                return ot

    return None


def place_trade(trade_decision: TradeDecision, api: OandaApi, log_message, log_error, trade_risk, trade_settings, strategy_state):

    send_message("Placing a trade")
    ot = trade_is_open(trade_decision.pair, api)

    # it is possbile that the system exit from tradings anywhen . If there are no trades open, strategy state is to be reset
    if ot == None:
        strategy_state.reset()

    # if we have a simple strategy we cannot trade if there is one trade open.
    if ot is not None and trade_settings.strategy == 'B':
        log_message(f"Failed to place trade {trade_decision}, already open: {ot}", trade_decision.pair)
        return None

    # if we have more open trades AND we have a multi strategy (from trade_settings), the SL and TP are calculated in detail

    if trade_settings.strategy == 'B' :
        trade_units = get_trade_units(api, trade_decision.pair, trade_decision.signal,
                                      trade_decision.loss, trade_risk, log_message)
        trade_id = api.place_trade(
            trade_decision.pair,
            trade_units,
            trade_decision.signal,
            trade_decision.sl,
            trade_decision.tp
        )

    if trade_settings.strategy == 'M':

        trade_units = strategy_units(trade_settings, strategy_state)
        # SL and TP must be according to strategy
        SL, TP = strategy_sl_tp(trade_decision, trade_settings, strategy_state)

        trade_id = api.place_trade(
            trade_decision.pair,
            trade_units,
            trade_decision.signal,
            SL,
            TP
        )

    if trade_id is not None :
        print (f"\n Trade id : {trade_id}")
        # we need , now that we placed a trade, to update the strategy_state
        strategy_state.update(trade_decision.mid_c, trade_decision.signal, trade_units )
        log_message(
            f"placed trade_id:{trade_id} for {trade_decision} , strategy {trade_settings.strategy}, traded units {trade_units} , strategy_state {strategy_state}",
            trade_decision.pair)
        send_message(f"placed trade_id:{trade_id} for {trade_decision} , strategy {trade_settings.strategy}, traded units {trade_units} , strategy_state {strategy_state}")



    if trade_id is None:

        send_message(f"ERROR placing trade_id:{trade_id} for {trade_decision} , strategy {trade_settings.strategy}, traded units {trade_units} , strategy_state {strategy_state}")
        log_error(f"ERROR placing {trade_decision}, {trade_decision.pair} , trade_units {trade_units}")
        log_message(f"ERROR placing {trade_decision} for trade_units {trade_units}", trade_decision.pair)




