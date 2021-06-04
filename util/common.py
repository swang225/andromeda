import pickle
import os


def write_pickle(data, file, ensure_exist=True):

    if ensure_exist:
        path = os.path.dirname(file)
        if len(path) > 0:
            os.makedirs(path, exist_ok=True)

    with open(file, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)


def read_pickle(file):
    with open(file, 'rb') as handle:
        b = pickle.load(handle)

    return b


def nkeys(data_dict, n=10):

    res = {}
    for i, k in enumerate(data_dict.keys()):
        if i >= n:
            break

        res[k] = data_dict[k]

    return res


def str_to_date(date_string):
    # date string to date

    import datetime
    import pytz
    et = pytz.timezone("US/Eastern")
    date = datetime.datetime.strptime(date_string, "%b %d, %Y,  %H:%M ET")

    return date


