import pandas as pd
import yfinance as yf


def get_prices(tickers):

    history = []
    for ticker in tickers:
        print(f'processing {ticker}')

        yt = yf.Ticker(ticker)

        res = yt.history(period='max')['Close']
        res.name = ticker
        res = pd.DataFrame(data=res)

        history.append(res)

    prices = pd.concat(history, axis=1)

    return prices
