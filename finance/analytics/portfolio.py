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
    if roll is not None:
        factor = factor.rolling(roll, min_periods=1).sum()

    return factor