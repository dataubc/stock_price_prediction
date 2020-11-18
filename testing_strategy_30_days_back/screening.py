import pandas_datareader.data as web
from pandas_datareader.nasdaq_trader import get_nasdaq_symbols
from pandas_datareader._utils import RemoteDataError
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pickle

plt.rcParams['figure.figsize'] = [10, 6]
import warnings

warnings.filterwarnings('ignore')
from pandas_datareader import data as pdr
import yfinance as yf  # for data

yf.pdr_override()
import os
from dotenv import load_dotenv
from email.message import EmailMessage
import smtplib

import time
while True:


    load_dotenv(".env")

    SENDER = os.environ.get("GMAIL_USER")
    PASSWORD = os.environ.get("GMAIL_PASSWORD")

    series_tickers = pickle.load(open("series_tickers.p", "rb"))


    class stock:
        def __init__(self, stock='NIO', price='Adj Close'):
            self.stock = stock
            self.price = price

        def get_df(self):
            '''
            volume trading create a data frame for the stocks and manipulate it, a new column reflecting postive or negative is created, green for postive
            and red for negative

            inputs:
            ------
            None

            returns:
            ------
            df : a dataframe which will be used with the subsequent  functions
            '''
            price = self.price
            df = pdr.get_data_yahoo(self.stock, period="60d",

                                    # fetch data by interval (including intraday if period < 60 days)
                                    # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                                    # (optional, default is '1d')
                                    interval="5m")

            self.df = df
            return self.df

        def macd(self):
            '''
            macd trading, create a data frame for the stocks and manipulate it, a new column reflecting postive or negative is created, green for when macd is above the signal line
            and red for when when the macd is below singal line

            inputs:
            ------
            None

            returns:
            ------
            df : a dataframe which will be used with the subsequent  functions
            '''

            df = self.df
            # df = df.iloc[::-1]
            # Calculate the MACD and Signal Line indicators
            # Calculate the Short Term Exponential Moving Average
            ShortEMA = df['Adj Close'].ewm(span=26, adjust=False).mean()  # AKA Fast moving average
            # Calculate the Long Term Exponential Moving Average
            LongEMA = df['Adj Close'].ewm(span=50, adjust=False).mean()  # AKA Slow moving average

            # ShortEMA = df['Adj Close'].rolling(window = 12).mean() #AKA Fast moving average
            # Calculate the Long Term Exponential Moving Average
            # LongEMA = df['Adj Close'].rolling(window = 26).mean() #AKA Slow moving average
            # Calculate the Moving Average Convergence/Divergence (MACD)
            MACD = ShortEMA - LongEMA
            # Calcualte the signal line
            signal = MACD.ewm(span=9, adjust=False).mean()
            # signal = MACD.rolling(window = 9).mean()

            df['macd'] = MACD
            df['signal'] = signal

            df['macd_above'] = np.where(ShortEMA > LongEMA, 'green', 'red')

            self.df2 = df[::-1]

            return self.df2.head(25)

        def is_this_a_winner_macd(self, colors=['green', 'green', 'red']):
            '''
            macd trading, given a condition by the user this function will return wether a stock matches that condition or not
            inputs:
            ------
            colors : list of colors for today and the previous 3 days, green indicates a positive volume and red indicates a negative volume

            returns:
            ------
            result : Boolean, True if the conditions in the colors list are met

            '''

            df = self.df2
            result = np.where(
                df['macd_above'][0] == colors[0] and df['macd_above'][1] == colors[1] and df['macd_above'][2] == colors[2],
                True, False)
            # result = np.where(df['Color'][0]=='green' and df['Color'][1]=='red' and df['Color'][2]=='red' and df['Color'][3]=='red' ,True,False)
            return result[()]

        ### Example: volume trading :


    #
    # tsla = stock('FOLD')
    # tsla.get_df()
    # tsla.macd()

    conditions = ['green', 'red', 'red', 'red']

    winners_moving_avg = []  # a list that we will append with stocks that meet out conditions
    #
    # # i = 0

    star1_list = pd.read_csv("stra1_best.csv").iloc[:, 1].tolist()
    star2_list = pd.read_csv("stra2_best.csv").iloc[:, 1].tolist()
    star3_list = pd.read_csv("stra3_best.csv").iloc[:, 1].tolist()
    star4_list = pd.read_csv("stra4_best.csv").iloc[:, 1].tolist()

    all_lists = star1_list + star2_list + star2_list + star2_list + ['BYND','TSLA','ZM','AAPL','ROKU']

    for ticker in all_lists:
        # i = i +1
        try:
            my_stock = stock(ticker)
            my_stock.get_df()
            my_stock.macd()
            if my_stock.is_this_a_winner_macd():
                print(ticker, 'is a winner')
                # my_stock.plot_df_ballinger()
                # my_stock.plot_df_macd()
                winners_moving_avg.append(ticker)
            else:
                print(ticker, 'is not a winner')
        except:
            continue
        # if i ==1:
        # break


    def send_email(recipient, subject, body):
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = SENDER
        msg["To"] = recipient
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(SENDER, PASSWORD)
        server.send_message(msg)
        server.quit()

    # only if there is at least one winner then send email
    if winners_moving_avg:
        winners_string = ' '.join(winners_moving_avg)

        send_email("mmohamme@ualberta.ca", subject="List of winner", body=winners_string)
        send_email("must.usri@gmail.com", subject="List of winners", body=winners_string)
        print('Emails sent')
    print('No email sent')

    time.sleep(60)  # Delay for 1 minute (60 seconds).
    print('Starting next round')
