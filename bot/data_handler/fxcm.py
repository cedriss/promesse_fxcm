from data_handler.data_handler import DataHandler

import numpy as np
import pandas as pd

from datetime import datetime
import time

import fxcmpy
import socketio

from event import MarketEvent

import queue

from helpers import load_config


class FXCMDataHandler(DataHandler):
    def __init__(self, events, symbol_list, timeframe):
        self.events = events
        self.config = load_config()

        self.exchange_token = self.config['exchange']['fxcm']['token']
        self.exchange = self._create_exchange()

        self.timeframe_map = {
            '15m': 'm15',
            '30m': 'm30',
            '1h':  'H1',
            '1d': 'D1'
        }
        self.timeframe = ['m15', 'H1']

        self.symbol_list = symbol_list
        self.latest_symbol_data = {
            "EUR/USD": {
                'm15': None,
                'H1': None
            },
            "USD/JPY": {
                'm15': None,
                'H1': None
            },
            "GBP/USD": {
                'm15': None,
                'H1': None
            },
            "USD/CHF": {
                'm15': None,
                'H1': None
            },
            "AUD/USD": {
                'm15': None,
                'H1': None
            },
            "USD/CAD": {
                'm15': None,
                'H1': None
            },
            "NZD/USD": {
                'm15': None,
                'H1': None
            },
            "EUR/GBP": {
                'm15': None,
                'H1': None
            },
            "EUR/JPY": {
                'm15': None,
                'H1': None
            },
            "EUR/CHF": {
                'm15': None,
                'H1': None
            },
            "EUR/CAD": {
                'm15': None,
                'H1': None
            }
        }

        self.continue_backtest = True

        self._load_symbol_data()

    def __repr__(self):
        return f'<FXCMDataHandler>'

    def __str__(self):
        return f'FXCMDataHandler from {self.exchange_id} with {self.timeframe} timeframe'

    def _create_exchange(self):
        fxcm = fxcmpy.fxcmpy(
            access_token=self.exchange_token, log_level='error', server='real')

        return fxcm

    def _load_symbol_data(self):
        for symbol in self.symbol_list:
            for timeframe in self.timeframe:
                bars = self.exchange.get_candles(
                    symbol, period=timeframe, number=200)
                bars.reset_index(inplace=True)
                self.latest_symbol_data[symbol][timeframe] = bars
                time.sleep(1)

    def update_bars(self):
        self._load_symbol_data()
        self.events.put(MarketEvent())

    def get_latest_bars(self, symbol, timeframe, N=1):
        try:
            bars = self.latest_symbol_data[symbol][timeframe].iloc[-N:]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars

    def get_latest_bar(self, symbol, timeframe):
        return self.get_latest_bars(symbol, timeframe, N=1)

    def get_latest_bars_values(self, symbol, value_type, timeframe, N=1):
        try:
            bars = self.latest_symbol_data[symbol][timeframe].iloc[-N:]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            if value_type == 'datetime':
                return np.array(bars['date'])

            if value_type == 'volume':
                return np.array(bars['tickqty'])

            return np.array(bars[f'bid{value_type}'])

    def get_latest_bar_value(self, symbol, value_type, timeframe):
        return self.get_latest_bars_values(symbol, value_type, timeframe, N=1)

    def get_latest_bar_datetime(self, symbol, timeframe='m15'):
        return self.get_latest_bar_value(symbol, 'datetime', timeframe)

    def current_price(self, symbol, timeframe='m15'):
        return self.get_latest_bar_value(symbol, 'close', timeframe)
