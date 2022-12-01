

def strategy_units(trade_settings, strategy_state):

    units=trade_settings.size
    ot=strategy_state['current_n_ot']
    dim_lot=trade_settings['dim_lot'][ot]
    units=units*dim_lot
    return units

def strategy_sl_tp(trade_decision, trade_settings, strategy_state):
    price = trade_decision.mid_c
    if strategy_state.current_n_ot == 0:
        #if it is the first trade the SL and TP are recorded on strategy_states
        SL = price - trade_decision.signal * trade_settings.sl
        TP = price + trade_decision.signal * trade_settings.tp
        strategy_state.sl=SL
        strategy_state.tp=TP
    else:
        SL = strategy_state.sl
        TP = strategy_state.tp

    return SL, TP

