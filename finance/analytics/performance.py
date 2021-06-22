import pandas as pd
import numpy as np

from andromeda.finance.analytics.portfolio import roll, equal_weight


def daily_returns(prices):
    """
    Calculates daily returns from daiy prices
    :param prices: prices, indexed by date
    :return: daily returns, indexed by date
    """

    res = (prices / prices.shift(1) - 1.0)
    res.iloc[0] = 0

    return res


def cumulative_returns(returns):
    """
    Calculates cumulative returns from daily returns
    :param returns: daily returns, indexed by date
    :return: cumulative returns, indexed by date
    """

    res = (returns + 1.0).cumprod()

    return res


def sharpe(returns, returns_ref=0, period=252, ddof=1):
    """
    Calculates Sharpe Ratio given periodic returns
    :param returns: periodic returns, indexed by date
    :param returns_ref: reference average return rate
    :param period: period to annual, 252 if returns are daily, 12 if monthly
    :param ddof: degrees of freedom for volatility estimation
    :return: Sharpe Ratio
    """

    mean_returns = returns.squeeze().sub(returns_ref, axis='rows').mean(axis='rows')
    volatility = returns.std(axis='rows', ddof=ddof)

    return mean_returns * np.sqrt(period) / volatility


def max_drawdown(cum_returns):

    max_returns = np.fmax.accumulate(cum_returns)
    res = cum_returns / max_returns - 1

    res.columns = ['max drawdown']

    return res


def brownian_prices(start, end):

    bdates = pd.bdate_range(start, end)
    size = len(bdates)

    np.random.seed(1)
    wt = np.random.standard_normal(size)

    mu = 0.0001
    sigma = 0.01
    s0 = 10.0
    st = s0 * np.cumprod(np.exp(mu - (sigma * sigma / 2.0) + sigma * wt))

    return pd.DataFrame(data={'date': bdates, 'price': st}).set_index('date')


def factor_strategy(factor,
                    roll_days=None,
                    leverage=1,
                    groups=None,
                    neutral=False):

    factor = factor.copy()
    factor = roll(factor, roll_days)

    group_weights = None
    if groups is not None:
        groups = groups.copy()
        grp_col = groups.columns[0]
        res = groups.reindex(factor.columns).set_index(grp_col, append=True)
        res = res.reorder_levels([grp_col, 'ticker']).index
        factor.columns = res
        if neutral:
            factor_sn = factor.div(factor.groupby(grp_col, axis='columns').sum(), axis='rows')
        else:
            factor_sn = factor

        group_weights = factor_sn.groupby(grp_col, axis='columns').sum()

        factor_sn.columns = factor_sn.columns.droplevel(0)
        factor = factor_sn

    factor_count = factor.sum(axis=1)
    factor_strategy = factor.div(factor_count, axis='rows')
    return factor_strategy.mul(leverage), group_weights


def calc_returns(factor_strategy, returns, trade_cost=None):
    strategy_sod = factor_strategy.copy()
    strategy_sod.index = strategy_sod.index.shift(1, 'B')

    returns = returns.reindex(strategy_sod.index)
    returns = returns[strategy_sod.columns]

    daily_returns = strategy_sod.mul(returns).sum(axis='columns')

    if trade_cost is not None:
        trades = strategy_sod.sub(strategy_sod.shift(1))
        daily_returns = daily_returns.sub(trades.abs().mul(trade_cost).sum(axis='columns'))

    cum_returns = cumulative_returns(daily_returns)

    return cum_returns, daily_returns


def performance_data(factor,
                     returns,
                     roll=None,
                     title=None,
                     leverage=1,
                     groups=None,
                     trade_cost=None,
                     neutral=False):
    strat, gweights = factor_strategy(factor,
                                      roll,
                                      leverage,
                                      groups=groups,
                                      neutral=neutral)
    ret, daily_ret = calc_returns(strat,
                                  returns,
                                  trade_cost=trade_cost)

    if title is None:
        title = f'roll-{roll}'
    ret.name = title
    daily_ret.name = title
    gweights.name = title

    return ret, daily_ret, gweights


def performance_data_list(factor,
                          returns,
                          rolls=[],
                          groups=None,
                          trade_cost=None,
                          neutral=False):
    rets = []
    drets = []
    gwgts = {}

    ret, dret, gw = performance_data(equal_weight(factor.index, factor.columns),
                                     returns,
                                     title='equal weight',
                                     groups=groups,
                                     trade_cost=trade_cost,
                                     neutral=neutral)
    rets.append(ret)
    drets.append(dret)
    gwgts[ret.name] = gw

    #ret, dret, gw = performance_data(equal_weight(factor.index, factor.columns),
    #                                 returns,
    #                                 title='equal weight 1.5',
    #                                 leverage=1.5,
    #                                 groups=groups,
    #                                 trade_cost=trade_cost,
    #                                 neutral=neutral)
    #rets.append(ret)
    #drets.append(dret)
    #gwgts[ret.name] = gw

    ret, dret, gw = performance_data(factor,
                                     returns,
                                     groups=groups,
                                     trade_cost=trade_cost,
                                     neutral=neutral)
    rets.append(ret)
    drets.append(dret)
    gwgts[ret.name] = gw

    for roll in rolls:
        ret, dret, gw = performance_data(factor,
                                         returns,
                                         roll,
                                         groups=groups,
                                         trade_cost=trade_cost,
                                         neutral=neutral)
        rets.append(ret)
        drets.append(dret)
        gwgts[ret.name] = gw

    rets = pd.concat(rets, axis=1)
    drets = pd.concat(drets, axis=1)
    return rets, drets, gwgts


def calc_performance(drets, ref):
    sp = sharpe(drets, returns_ref=ref).sort_values()
    sp.name = "Sharpe"

    vol = drets.std(axis='rows') * np.sqrt(252)
    vol.name = "Volatility"

    res = pd.concat([sp, vol], axis=1)

    return res


def analyze_factor(factor_name,
                   data,
                   returns,
                   sp500_gics,
                   trade_cost=0,
                   rolls=[2, 5, 8, 10, 13, 15, 100]):

    print(f"ANALYZING: {factor_name}")
    r1 = data[[factor_name]]
    r1 = r1.dropna()
    factor = r1[factor_name].unstack()

    factor = factor.reindex(pd.bdate_range(factor.index.min(),
                                           factor.index.max()))
    returns.columns.name = 'ticker'
    factor = factor.reindex(returns.columns, axis=1)
    #print(factor)

    rets, drets, gwgts = performance_data_list(factor,
                                               returns,
                                               rolls=rolls,
                                               trade_cost=trade_cost,
                                               groups=sp500_gics)
    rets.plot(figsize=(10, 5), title=f"{factor_name} Without Neutralization")
    print(calc_performance(drets, drets['equal weight']))
    # print(drets_n.corr())
    gwgts['roll-None'].tail(300).plot.area(figsize=(10, 5), title=f"{factor_name} Without Neutralization")

    rets_n, drets_n, gwgts_n = performance_data_list(factor,
                                                     returns,
                                                     rolls=rolls,
                                                     trade_cost=trade_cost,
                                                     groups=sp500_gics,
                                                     neutral=True)
    rets_n.plot(figsize=(10, 5), title=f"{factor_name} Neutralized")
    print("sector neutral:")
    print(calc_performance(drets_n, drets_n['equal weight']))
    #print(drets_n.corr())
    gwgts_n['roll-None'].tail(300).plot.area(figsize=(10, 5), title=f"{factor_name} Neutralized")