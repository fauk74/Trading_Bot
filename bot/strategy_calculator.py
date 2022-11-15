

def strategy_units(trade_settings, strategy_state):
    units=trade_settings.size
    ot=strategy_state['current_ot']
    dim_lot=trade_settings['dim_lot'][ot]
    units=units*dim_lot
    return units
