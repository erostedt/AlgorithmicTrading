import pandas as pd
import numpy as np
import keras
class Bot:
    def __init__(self):
        self.name = "Jonte_bot"
        self.scale = 184.83719635009766
        self.shift = 76.8767318725586
        self.df_main = pd.DataFrame(columns=['Main'])
        self.df_tickers = [[],[],[],[],[],[],[]]
        self.df_close = [0,0,0,0,0,0,0]
        self.df = pd.DataFrame()
        self.i = 0
        self.tickers = {}
        self.tickers_name = []
        self.actions = []
        self.time = 0
        self.main_ticker = ''
        self.start = True
        self.vae = keras.models.load_model('file_system/trading_algorithms/Jonte_bot/vae_ez_enc')
        self.lstm = keras.models.load_model('file_system/trading_algorithms/Jonte_bot/ez2')
        self.prediction = []
        self.position = "short"


    def handle_event(self, event):
        timestamp, ticker, new_close = event

        if self.start:
            self.start = False
            self.main_ticker = ticker
        if self.time < 100 and ticker == self.main_ticker:
            self.df_main = self.df_main.append({'Main': new_close}, ignore_index=True)
            self.time += 1
        if self.time <= 100 and ticker is not self.main_ticker:
            index = self.tickers_to_index(ticker)
            self.df_tickers[index].append(new_close)
        if self.time >= 100:
            self.data_proc(ticker,new_close)
            self.time += 1
            self.algorithm(event)

    def algorithm(self,event):
        timestamp, ticker, new_close = event
        if ticker == self.main_ticker and len(self.prediction) >7:
            change = self.prediction[-7]-self.prediction[-1]
            if change < 0 and not self.position == "short":
                self.position = "short"
                self.actions.append([event, "short"])

            if change > 0 and not self.position == "long":
                self.position = "long"
                self.actions.append([event, "long"])

    def data_proc(self,ticker, price):
        if sum(self.df_close) == 7:
            self.df_main = self.df_main.append({'Main': price}, ignore_index=True)
            ma7 = self.df_main.rolling(window=7).mean()['Main'].tolist()
            ma21 = self.df_main.rolling(window=21).mean()['Main'].tolist()
            ema26 = self.df_main.ewm(span=26).mean()['Main'].tolist()
            ema12 = self.df_main.ewm(span=12).mean()['Main'].tolist()
            MACD = [x - y for x, y in zip(ema12, ema26)]
            std20 = self.df_main.rolling(20).std()['Main'].tolist()

            upper_band = [x + 2*y for x, y in zip(ma21, std20)]
            lower_band = [x - 2 * y for x, y in zip(ma21, std20)]
            ema = self.df_main.ewm(com=0.5).mean()['Main'].tolist()
            momentum = self.df_main.pct_change()['Main'].tolist()

            close_fft = np.fft.fft(np.asarray(self.df_main.to_numpy()))
            fft_list = np.copy(close_fft)
            fft_list[3:-3] = 0
            fft3 = abs(np.fft.ifft(fft_list)).tolist()
            fft_list = np.copy(close_fft)
            fft_list[6:-6] = 0
            fft6 = abs(np.fft.ifft(fft_list)).tolist()
            fft_list = np.copy(close_fft)
            fft_list[9:-9] = 0
            fft9 = abs(np.fft.ifft(fft_list)).tolist()


            test2 = [self.df_main['Main'].tolist(), self.df_tickers[0],self.df_tickers[1],self.df_tickers[2],self.df_tickers[3],self.df_tickers[4],self.df_tickers[5],self.df_tickers[6],ma7, ma21 ,ema26, ema12, MACD, std20, upper_band, lower_band, ema, momentum, fft3, fft6,fft9]
            temp = [None for i in range(21)]

            for i,tttet in enumerate(test2):
                if i>17:
                    tttet = [x[0] for x in tttet]
                temp[i] = [(x-self.shift)/self.scale for x in tttet]

            testtt3 = pd.DataFrame(temp)
            testtt3 = testtt3.transpose()
            testtt3.fillna(method='bfill', inplace=True)
            testtt3.fillna(method='ffill', inplace=True)

            vae_feat = self.vae.predict(testtt3.to_numpy())

            testtt3.columns = ['Main', '1', '2' ,'3' ,'4' ,'5' ,'6' ,'7', 'ma7', 'ma21', 'ema26', 'ema12', 'MACD', 'std20', 'upper_band', 'lower_band', 'ema', 'momentum', 'fft3', 'fft6','fft9']

            testtt3['VAE_0'] = vae_feat[:,0]
            testtt3['VAE_1'] = vae_feat[:, 1]
            testtt3['VAE_2'] = vae_feat[:, 2]
            testtt3['VAE_3'] = vae_feat[:, 3]
            self.df = testtt3
            self.df_close = [0,0,0,0,0,0,0]

            x_multi = self.multi_data_x(self.df.iloc[-22:].to_numpy(), 7, 21, False)
            f = self.lstm.predict(x_multi)
            self.prediction.append(f[0][0]*self.scale+self.shift)

            if ticker is not self.main_ticker:
                index = self.tickers_to_index(ticker)
                self.df_close[index] = 1
                self.df_tickers[index].append(price)
        else:
            if ticker is not self.main_ticker:
                index = self.tickers_to_index(ticker)
                self.df_close[index] = 1
                self.df_tickers[index].append(price)
            else:
                self.df_main.append({'Main': price}, ignore_index=True)


    def tickers_to_index(self,ticker):
        if ticker not in self.tickers.keys():
            self.tickers[ticker] = self.i
            self.i += 1
            return self.i-1
        else:
            return self.tickers[ticker]


    def multi_data_x(self,data, days, memory, is_array=False):
        if not is_array:
            return np.array([data[index - memory:index, :] for index in range(memory, np.shape(data)[0])])
        else:
            return np.array([data[index + days] for index in range(memory, np.shape(data)[0] - days)])