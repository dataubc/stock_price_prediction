import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, MACD

class AlphaRealtimeStock():
    def __init__(self, symbol, crumbs, interval='5m'):
        self.symbol = symbol
        self.interval = interval
        self.df = None
        self.crumbs = crumbs

    def fetch_webdata(self):
        symbol = self.symbol
        current = datetime.now()
        period2 = int(datetime.timestamp(current))
        period1 = int(datetime.timestamp(current - timedelta(days=5)))
        includePrePost = 'true'
        url ='https://query1.finance.yahoo.com/v8/finance/chart/{}?symbol={}&period1={}&period2={}&interval={}' \
              '&includePrePost={}&events=div%7Csplit%7Cearn&lang=en-US&region=US&crumb={}&corsDomain=finance.yahoo.com'\
              ''.format(symbol, symbol, period1, period2, self.interval, includePrePost, self.crumbs)
        response = requests.get(url=url)
        if response.status_code == 200:
            response = json.loads(response.content)
            web_data = response['chart']['result'][0]['indicators']['quote'][0]
            df = pd.DataFrame()
            df['Datetime'] = response['chart']['result'][0]['timestamp']
            df['Datetime'] = df['Datetime'].apply(lambda x: datetime.fromtimestamp(x))
            ohlcv = ['Open','High','Low','Close','Volume']
            for item in ohlcv:
                df[item] = web_data[item.lower()]
            self.df = df
            return df
        else:
            print(response.status_code)

    def get_Stoch_RSI_Indicator(self, period=14, smooth=[3, 3], col='Close', fillna=False):
        """
        get Stoch RSI Indicator
        """
        rsi = RSIIndicator(close=self.df[col], n=period, fillna=fillna).rsi()
        stochrsi = (rsi - rsi.rolling(period).min()) / (rsi.rolling(period).max() - rsi.rolling(period).min())
        stochrsi_K = stochrsi.rolling(smooth[0]).mean()
        stochrsi_D = stochrsi_K.rolling(smooth[1]).mean()
        self.df['Stoch_RSI'] = stochrsi * 100
        self.df['Stoch_RSI_K'] = stochrsi_K * 100
        self.df['Stoch_RSI_D'] = stochrsi_D * 100
        return self.df

    def get_MACD_Indicator(self, col='Close', fillna=False):
        """
        get MACD Indicator
        """
        stock_MACD = MACD(self.df[col], fillna=fillna)
        self.df['MACD'] = stock_MACD.macd()
        self.df['MACD_signal'] = stock_MACD.macd_signal()
        self.df['MACD_diff'] = stock_MACD.macd_diff()
    
    def get_market_data(self):
        # return market data
        return self.df[self.df['Volume'] != 0]