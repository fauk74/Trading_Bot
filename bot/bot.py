import json
import time
from bot.candle_manager import CandleManager
from bot.technicals_manager import get_trade_decision
from bot.trade_manager import place_trade, trade_is_open

from infrastructure.log_wrapper import LogWrapper
from models.trade_settings import TradeSettings
from models.strategies import StrategyStates
from api.oanda_api import OandaApi
import constants.defs as defs
from bot.telegram import send_message


class Bot:

    ERROR_LOG = "error"
    MAIN_LOG = "main"
    GRANULARITY = "M1"
    SLEEP = 10

    def __init__(self):
        self.load_settings() # loads trade_settings into self.trade_setting, that will be passed to CandleManager
        self.setup_logs()
        self.api = OandaApi()
        self.candle_manager = CandleManager(self.api, self.trade_settings, self.log_message, Bot.GRANULARITY)
        self.log_to_main("Bot started")
        self.log_to_error("Bot started")
        self.strategy_states=dict({k: StrategyStates(v, k, self.api) for k,v in self.pairs.items() })
        print(f"\nStrategy_states :{self.strategy_states}")

    def load_settings(self):
        # upload settings.json info into data ; trade_settings is set
        with open("./bot/settings.json", "r") as f:
            data = json.loads(f.read())
            self.pairs=data['pairs']
            self.trade_settings = { k: TradeSettings(v, k) for k, v in self.pairs.items() }
            self.trade_risk = data['trade_risk']  # this number is set equal to 10 in settings.json
            print(f"\nTrade settings: {self.trade_settings}")



    def setup_logs(self):
        self.logs = {}
        for k in self.trade_settings.keys():
            self.logs[k] = LogWrapper(k)
            self.log_message(f"{self.trade_settings[k]}", k)
        self.logs[Bot.ERROR_LOG] = LogWrapper(Bot.ERROR_LOG)
        self.logs[Bot.MAIN_LOG] = LogWrapper(Bot.MAIN_LOG)
        self.log_to_main(f"Bot started with {TradeSettings.settings_to_str(self.trade_settings)} ")

    def log_message(self, msg, key):
        self.logs[key].logger.debug(msg)

    def log_to_main(self, msg):
        self.log_message(msg, Bot.MAIN_LOG)

    def log_to_error(self, msg):
        self.log_message(msg, Bot.ERROR_LOG)

    def process_candles(self, triggered):
        # be aware that there is another function called process_candles in technical manager
        if len(triggered) > 0:
            self.log_message(f"process_candles triggered:{triggered}", Bot.MAIN_LOG)
            
            for p in triggered:
                # p is a pair, so when it is triggered , we get last time, settings and other data
                # then a trade decision is got and place trade is activated
                # it is necessary to check if , in the meanwhile, the system closed automatically some trades, to
                # reset the strategy states
                # this should be further checked, in case there are partial closing

                ot=trade_is_open(p, self.api)
                if ot==0:
                    self.strategy_states[p].reset()

                last_time = self.candle_manager.timings[p].last_time
                # in technical manager there is the function get_trade_decision:
                trade_decision = get_trade_decision(last_time, p, Bot.GRANULARITY, self.api, 
                                 self.trade_settings[p],  self.log_message, self.strategy_states[p])

                if trade_decision is not None and trade_decision.signal != defs.NONE:
                    self.log_message(f"Place Trade: {trade_decision}", p)
                    self.log_to_main(f"Place Trade: {trade_decision}")
                    # place trade is in trade_manager
                    # the strategy_states have to be passed because a purchase
                    # can change them
                    send_message(trade_decision)
                    place_trade(trade_decision, self.api, self.log_message, self.log_to_error, self.trade_risk, self.trade_settings[p], self.strategy_states[p])

                

    # bot.process_candles -> for p in triggered -> get_trade_decision (from technicals_manager) -> place_trade

    # trade_decision comes from get_trade_decision (technicals_manager) which fetch_candles and then process_candles and then return TradeDecision
    # the class trade_decision is in models and the most important item is the signal: trade_decision.signal

    # steps to implement a new strategy:
    # add details to settings
    # signal to trigger is in technicals_manager (through process_candles and apply_signal)
    # get_trade_decision then passes the trade_decision
    # the place_trade has to be implemented as well



    def run(self):
        while True:
            time.sleep(Bot.SLEEP)
            #update_timings is a function of candle_manager: it returns all triggered candles
            self.process_candles(self.candle_manager.update_timings())

  #          try:
  #              self.process_candles(self.candle_manager.update_timings())
  #          except Exception as error:
  #              self.log_to_error(f"CRASH: {error}")
  #              break
    

