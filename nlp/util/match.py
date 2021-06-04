import pandas as pd
from fuzzywuzzy import fuzz


def get_matches_fuzzy(ticker, tickers):

    match = []
    for test in tickers:

        score = fuzz.partial_ratio(test[0], ticker)

        if score > 80:
            match.append(test[1])

    return match


def create_ticker_map(subjects, tickers):

    ticker_map = {}
    total = len(subjects)
    count = 0
    success = 0
    failure = 0
    for subject in subjects:
        count = count + 1
        print(f"processing {count} out of {total}")
        ticker_map[subject] = get_matches_fuzzy(subject, tickers)

        if len(ticker_map[subject]) > 0:
            success = success + 1
        else:
            failure = failure + 1
        print(f"subject: {subject}, match: {ticker_map[subject]}")

        print(f"stat success {success}, failure {failure}")

    return ticker_map


if __name__ == '__main__':
    df1 = pd.read_csv("code/test001_nlp/sp500gics02.csv")
    tickers = [(' '.join(ls).upper(), ls[0]) for ls in list(df1[['Symbol', 'Security']].values)]

    from andromeda.util import read_pickle
    org_map = read_pickle("code/test003_prnewswire_v01/data/org_map_complete.pkl")
    orgs = set(org_map.values())
