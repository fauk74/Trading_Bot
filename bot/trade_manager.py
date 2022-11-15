
from api.oanda_api import OandaApi
from bot.trade_risk_calculator import get_trade_units
from models.trade_decision import TradeDecision
from bot.strategy_calculator import strategy_units

def trade_is_open(pair, api: OandaApi):

    open_trades = api.get_open_trades()

    for ot in open_trades:
        if ot.instrument == pair:
            return ot

    return None


def place_trade(trade_decision: TradeDecision, api: OandaApi, log_message, log_error, trade_risk, trade_settings, strategy_state):

    ot = trade_is_open(trade_decision.pair, api)

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

        trade_id = api.place_trade(
            trade_decision.pair,
            trade_units,
            trade_decision.signal,
            trade_decision.sl,
            trade_decision.tp
        )

    if trade_id is not None :
        print (f"\n Trade id : {trade_id}")
        # we need , now that we placed a trade, to update the strategy_state


    if trade_id is None:
        log_error(f"ERROR placing {trade_decision}")
        log_message(f"ERROR placing {trade_decision}", trade_decision.pair)
    else:
        log_message(f"placed trade_id:{trade_id} for {trade_decision} , strategy {trade_settings.strategy}", trade_decision.pair)


