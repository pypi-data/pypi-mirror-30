from collections import UserDict, UserList

import pandas as pd

from OnePy.constants import ActionType
from OnePy.environment import Environment


class SeriesBase(UserDict):
    env = Environment

    def __init__(self):
        super().__init__()
        name = None

        for ticker in self.env.feeds:
            self.data[f'{ticker}_long'] = [
                dict(date=self.env.fromdate, value=0)]
            self.data[f'{ticker}_short'] = [
                dict(date=self.env.fromdate, value=0)]

    def latest(self, ticker, long_or_short, index=-1):
        return self.data[f'{ticker}_{long_or_short}'][index]['value']

    def total_value(self):
        total = 0

        for data_list in self.data.values():
            per_dict = data_list[-1]
            total += per_dict['value']

        return total

    def direction(self, order):
        if order.action_type in [ActionType.Buy, ActionType.Short_sell]:
            return 1

        elif order.action_type in [ActionType.Sell, ActionType.Short_cover]:
            return -1

    def earn_short(self, long_or_short):
        return 1 if long_or_short == 'long' else -1

    def _append_value(self, ticker, trading_date, value, long_or_short):
        self.data[f'{ticker}_{long_or_short}'].append(
            {'date': trading_date, 'value': value})

    def dataframe(self):
        dataframe_list = []

        for ticker in self.env.tickers:
            long_df = pd.DataFrame(self.data[f'{ticker}_long'])
            short_df = pd.DataFrame(self.data[f'{ticker}_short'])
            long_df.rename(columns=dict(
                value=f'{self.name}_{ticker}_long'), inplace=True)
            short_df.rename(columns=dict(
                value=f'{self.name}_{ticker}_short'), inplace=True)

            dataframe_list.append(long_df)
            dataframe_list.append(short_df)

        dataframe = long_df

        for df in dataframe_list:
            dataframe = dataframe.merge(df, how='outer')

        dataframe.set_index('date', inplace=True)
        dataframe.fillna(method='ffill', inplace=True)

        return dataframe

    def plot(self, ticker):
        long_df = pd.DataFrame(self.data[f'{ticker}_long'])
        short_df = pd.DataFrame(self.data[f'{ticker}_short'])
        long_df.rename(columns=dict(value=f'{self.name}_long'), inplace=True)
        short_df.rename(columns=dict(value=f'{self.name}_short'), inplace=True)

        total_df = long_df.merge(short_df, how='outer')
        total_df.fillna(method='ffill', inplace=True)
        total_df.set_index('date', inplace=True)
        total_df.plot()

    def get_barly_cur_price(self, ticker, order_executed):
        if order_executed:
            return self.env.feeds[ticker].execute_price
        else:
            return self.env.feeds[ticker].open


class CashSeries(UserList):
    env = Environment

    def __init__(self, name, initial_value):
        super().__init__()
        self.name = name
        self.data = [dict(date=self.env.fromdate, value=initial_value)]

    def latest(self):
        return self.data[-1]['value']

    def dataframe(self):
        dataframe = pd.DataFrame(self.data)
        dataframe.rename(columns=dict(value=self.name), inplace=True)
        dataframe.set_index('date', inplace=True)

        return dataframe

    def plot(self):
        self.dataframe().plot()


class BarSeries(UserDict):
    env = Environment

    def __init__(self):
        super().__init__()

    def __missing__(self, key):
        self.data[key] = []

        return self.data[key]

    def dataframe(self, ticker):
        dataframe = pd.DataFrame(self.data[ticker])
        dataframe.set_index('date', inplace=True)

        return dataframe
