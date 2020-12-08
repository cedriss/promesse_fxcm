from strategy.strategy import Strategy

import queue

import numpy as np
import pandas as pd

from datetime import datetime
from talib import RSI, EMA, BBANDS, ATR
from custom_indicators import STOCHRSI
from helpers import load_config

from telegram import TelegramBot


class Momentum(Strategy):
    def __init__(self, events, data_handler):
        self.events = events
        self.config = load_config()

        self.data_handler = data_handler
        self.symbol_list = self.data_handler.symbol_list

        self.counter = 0

        self.bars_window = 200
        self.rsi_window = 14

        self.telegram = TelegramBot(
            bot_token=self.config['telegram']['bot_token'],
            channel_id=self.config['telegram']['channel_id'])

    def calculate_signals(self):
        for symbol in self.symbol_list:
            print('Searching for {1} signals ...'.format(symbol))

            last_price = self.data_handler.current_price(symbol)[0]

            h1_highs = self.data_handler.get_latest_bars_values(
                symbol, 'high', timeframe='H1', N=self.bars_window)

            h1_lows = self.data_handler.get_latest_bars_values(
                symbol, 'low', timeframe='H1', N=self.bars_window)

            h1_closes = self.data_handler.get_latest_bars_values(
                symbol, 'close', timeframe='H1', N=self.bars_window)

            h1_hlc3 = (h1_highs + h1_lows + h1_closes) / 3

            h1_ema_50 = EMA(h1_hlc3, timeperiod=50)
            h1_ema_100 = EMA(h1_hlc3, timeperiod=100)
            h1_ema_200 = EMA(h1_hlc3, timeperiod=200)

            m15_highs = self.data_handler.get_latest_bars_values(
                symbol, 'high', timeframe='m15', N=self.bars_window)

            m15_lows = self.data_handler.get_latest_bars_values(
                symbol, 'low', timeframe='m15', N=self.bars_window)

            m15_closes = self.data_handler.get_latest_bars_values(
                symbol, 'close', timeframe='m15', N=self.bars_window)

            m15_hlc3 = (m15_highs + m15_lows + m15_closes) / 3

            m15_ema_50 = EMA(m15_hlc3, timeperiod=50)
            m15_ema_100 = EMA(m15_hlc3, timeperiod=100)
            m15_ema_200 = EMA(m15_hlc3, timeperiod=200)

            m15_price_bb_up, m15_price_bb_mid, m15_price_bb_low = BBANDS(
                m15_hlc3, timeperiod=20, nbdevup=2, nbdevdn=2)

            m15_price_bb_low_dist = (m15_price_bb_mid + m15_price_bb_low) / 2
            m15_price_bb_up_dist = (m15_price_bb_up + m15_price_bb_mid) / 2

            m15_rsi = RSI(m15_closes, timeperiod=14)
            m15_rsi_bb_up, m15_rsi_bb_mid, m15_rsi_bb_low = BBANDS(
                m15_rsi, timeperiod=20, nbdevup=2, nbdevdn=2)

            m15_stochrsi = STOCHRSI(
                pd.Series(m15_closes), timeperiod=14)

            m15_atr = ATR(m15_highs, m15_lows, m15_closes, timeperiod=14)

            datetime = self.data_handler.get_latest_bar_datetime(symbol)[0]

            direction = None
            status = None
            position = 'Not yet'

            print(datetime)

            if last_price > h1_ema_50[-1] and last_price > h1_ema_100[-1] and last_price > h1_ema_200[-1]:
                print('Uprend detected')

                if last_price > m15_ema_50[-1] and last_price > m15_ema_100[-1] and last_price > m15_ema_200[-1]:
                    print('Uprend confirmed')
                    direction = 'LONG'

                    if m15_rsi[-1] < m15_rsi_bb_low[-1]:
                        print('Reversal Detected')
                        status = 'Reversal detected'

                        if last_price < m15_price_bb_low_dist[-1]:
                            print('Reversal confirmed')
                            status = 'Reversal confirmed'

                            if m15_stochrsi[-1] < 25:
                                print('Go LONG')
                                position = 'Go ahead'

            elif last_price < h1_ema_50[-1] and last_price < h1_ema_100[-1] and last_price < h1_ema_200[-1]:
                print('Downrend detected')

                if last_price < m15_ema_50[-1] and last_price < m15_ema_100[-1] and last_price < m15_ema_200[-1]:
                    print('Downrend confirmed')
                    direction = 'SHORT'

                    if m15_rsi[-1] > m15_rsi_bb_up[-1]:
                        print('Reversal Detected')
                        status = 'Reversal detected'

                        if last_price > m15_price_bb_up_dist[-1]:
                            print('Reversal confirmed')
                            status = 'Reversal confirmed'

                            if m15_stochrsi[-1] > 75:
                                print('Go SHORT')
                                position = 'Go ahead'

            else:
                pass

            print(symbol, direction, status, position, datetime)

            if status is not None:
                self.telegram.send_text({
                    'symbol': symbol,
                    'direction': direction,
                    'status': status,
                    'position': position,
                    'atr': np.around(m15_atr[-1], decimals=5),
                    'datetime': datetime
                })
