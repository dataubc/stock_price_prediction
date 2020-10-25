import yfinance as yf  # for data
import pandas_datareader.data as web
from pandas_datareader.nasdaq_trader import get_nasdaq_symbols
from pandas_datareader._utils import RemoteDataError
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pickle
import warnings
warnings.filterwarnings('ignore')

class stock():

    def __init__(self,stock = 'NIO',price = 'Close'):
        self.stock = stock
        self.price = price
    
        price = self.price
        df = yf.download(tickers = self.stock,period = "7d",interval = "5m",group_by = 'ticker',auto_adjust = True,prepost = False,threads = True,proxy = None)
        df['close_before'] = df[price].shift(1) 
        df['relative_price'] = df[price] - df['close_before']
        df["Color"] = np.where(df["relative_price"]<0, 'red', 'green')

        df = df.iloc[::-1]
        df = df.reset_index()
        df = df.fillna(0)
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
        df = df.iloc[::-1]
        #Calculate the MACD and Signal Line indicators
        #Calculate the Short Term Exponential Moving Average
        ShortEMA = df['Close'].ewm(span=12, adjust=False).mean() #AKA Fast moving average
        #Calculate the Long Term Exponential Moving Average
        LongEMA = df['Close'].ewm(span=26, adjust=False).mean() #AKA Slow moving average

        #ShortEMA = df['Adj Close'].rolling(window = 12).mean() #AKA Fast moving average
        #Calculate the Long Term Exponential Moving Average
        #LongEMA = df['Adj Close'].rolling(window = 26).mean() #AKA Slow moving average
        #Calculate the Moving Average Convergence/Divergence (MACD)
        MACD = ShortEMA - LongEMA
        #Calcualte the signal line
        signal = MACD.ewm(span=9, adjust=False).mean()
        #signal = MACD.rolling(window = 9).mean()

        df['macd'] = MACD
        df['signal'] = signal
        df['macd_above'] = np.where(df['macd'] > df['signal'],'green','red')
        
        
        
        #### ballinger band
        df['Middle Band'] =df['Close'].rolling(window=20).mean()
        df['Upper Band'] = df['Middle Band'] + 1.96*df['Close'].rolling(window=20).std()
        df['Lower Band'] = df['Middle Band'] - 1.96*df['Close'].rolling(window=20).std()
        df['status_lower'] = np.where(df['Close'] < df['Lower Band'],'below_ballinger','normal')
        df['status_upper'] = np.where(df['Close'] > df['Upper Band'],'above_ballinger','normal')
            
        self.df2 = df[::-1]

        return self.df2
    
    def moving_avg(self,time_frame = 50):
        
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
        df = df.iloc[::-1]
        #Calculate the MACD and Signal Line indicators
        #Calculate the Short Term Exponential Moving Average
        df['moving_avg'] =df['Close'].rolling(window=time_frame).mean()
    
        df['status_moving_avg'] = np.where(df['Close'] > df['moving_avg'],'green','red')
            
        self.df2 = df[::-1]

        return self.df2
        
    def is_this_a_winner_moving_avg(self,colors = ['green','green','green','red']):
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
        result = np.where(df['status_moving_avg'][0]== colors[0] and df['status_moving_avg'][1]==colors[1] and df['status_moving_avg'][2]==colors[2]and df['status_moving_avg'][3]==colors[3],True,False)
        #result = np.where(df['Color'][0]=='green' and df['Color'][1]=='red' and df['Color'][2]=='red' and df['Color'][3]=='red' ,True,False)
        return result[()]
    
    
    
    def is_this_a_winner_volume(self,colors = ['green','green','red','red']):
        '''
        volume trading, given a condition by the user this function will return wether a stock matches that condition or not        
        inputs: 
        ------
        colors : list of colors for today and the previous 3 days, green indicates a positive volume and red indicates a negative volume
        
        returns:
        ------
        result : Boolean, True if the conditions in the colors list are met
        
        '''
        
        df = self.df
        result = np.where(df['Color'][0]== colors[0] and df['Color'][1]==colors[1] and df['Color'][2]==colors[2] and df['Color'][3]==colors[3],True,False)
        #result = np.where(df['Color'][0]=='green' and df['Color'][1]=='red' and df['Color'][2]=='red' and df['Color'][3]=='red' ,True,False)
        return result[()]
        
    def is_this_a_winner_macd(self,colors = ['green','green','red']):
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
        result = np.where(df['macd_above'][0]== colors[0] and df['macd_above'][1]==colors[1] and df['macd_above'][2]==colors[2],True,False)
        #result = np.where(df['Color'][0]=='green' and df['Color'][1]=='red' and df['Color'][2]=='red' and df['Color'][3]=='red' ,True,False)
        return result[()]
    def is_this_a_winner_ballinger(self,status_lower = ['normal','below_ballinger','below_ballinger']):
        '''
        ballinger trading, given a condition by the user this function will return wether a stock matches that condition or not        
        inputs: 
        ------
        status_lower : list of status for today and the previous 3 days, where the price is below or above ballinger ['normal','below_balinger','above_balinger']
        
        returns:
        ------
        result : Boolean, True if the conditions in the status list are met
        
        '''
        
        df = self.df2
        result = np.where(df['status_lower'][0]== status_lower[0] and df['status_lower'][1]==status_lower[1] and df['status_lower'][2]==status_lower[2],True,False)
        #result = np.where(df['Color'][0]=='green' and df['Color'][1]=='red' and df['Color'][2]=='red' and df['Color'][3]=='red' ,True,False)
        return result[()]
    
    
    def plot_df_bar(self):
        '''
        volume trading : displays a bar plot for the volume over time,green bar for positivie volume and red bar for negative volume         
        inputs: 
        '''   
        df = self.df

        df1 = df[df['relative_price']<0]
        df2 = df[df['relative_price']>=0]
        plt.bar(df1['Datetime'], df1['Volume'], color='r')
        plt.bar(df2['Datetime'], df2['Volume'], color='g')
        plt.show()
        return 
     
    def plot_df_macd(self):
        '''
        volume trading : displays a bar plot for the volume over time,green bar for positivie volume and red bar for negative volume         
        inputs: 
        '''   
        df = self.df2.iloc[1:5,:]
        plt.plot(df['Datetime'],df['signal'])
        plt.plot(df['Datetime'],df['macd']);

        return    
     
    def plot_df_ballinger(self):
        '''
        displays a bar plot for the volume over time,green bar for positivie volume and red bar for negative volume         
        inputs: 
        '''   
        df = self.df2.iloc[1:5,:]

        plt.plot(df['Datetime'], df['Close'], color='g')
        plt.plot(df['Datetime'], df['Lower Band'], color='r')
        plt.plot(df['Datetime'], df['Upper Band'], color='b')
        plt.show()
        return 
       
    
    