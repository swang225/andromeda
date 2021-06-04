import pandas as pd


def equal_weight(index, columns):
    """
    creates a dataframe of 1's given an index and columns
    :param index:
    :param columns:
    :return:
    """
    eq_factor = pd.DataFrame(1,
                             index=index,
                             columns=columns)
    return eq_factor


def roll(factor,
         roll_days=None):
    """
    roll dataframe foward for specified number of days
    :param factor: dataframe, datetime indexed
    :param roll_days: int, number of dates to roll
    :return: dataframe, original dataframe rolled foward
    """

    factor = factor.copy()
    if roll_days is not None:
        factor = factor.rolling(roll_days, min_periods=1).sum()

    return factor


def factors_from_cluster(data):
    data = data[~data['factor'].isnull()][['ticker', 'factor']]
    data['count'] = data['ticker'].apply(lambda x: len(x))

    data1 = data[data['count'] <= 1][['ticker', 'factor']]
    data1['ticker'] = data1['ticker'].apply(lambda x: x[0])
    data1.index.name = 'date'

    data_list = []
    data2 = data[data['count'] > 1][['ticker', 'factor']]
    for idx, row in data2.iterrows():
        tickers = row['ticker']
        factor = row['factor']
        for ticker in tickers:
            data_list.append(pd.DataFrame(data={'date': [idx],
                                                'ticker': [ticker],
                                                'factor': [factor]}))
    data2 = pd.concat(data_list, axis=0)
    data2 = data2.set_index('date')

    data = pd.concat([data1, data2], axis=0)
    data.index = pd.to_datetime(data.index.map(lambda x: x.date()))
    data = data.sort_index()
    data['value'] = 1
    data = data.set_index(['ticker', 'factor'], append=True)
    data = data.groupby(['date', 'ticker', 'factor']).sum()
    data = data.squeeze()
    data = data.unstack()

    return data
