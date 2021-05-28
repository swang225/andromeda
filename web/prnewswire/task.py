from nlp.processor import SVOStanford, WordVector
from nlp.util import get_org


def create_svo(data):

    print('extracting svo...')
    svo_p = SVOStanford()
    data = data['title'].apply(svo_p.process)
    data = data[~data['s'].isnull()]
    data['vo'] = data['v'] + ' ' + data['o']
    data = data[['s', 'v', 'o', 'vo']]

    return data



def create_wv_average(data):

    print('calc word vec average...')
    wv_p = WordVector()
    data['wv'] = data['vo'].apply(wv_p.process)
    data = data[~data['wv'].isnull()]

    return data


def create_wv_separate(data):

    print('calc word vec separate...')
    wv_p = WordVector()
    data['wv_v'] = data['v'].apply(wv_p.process)
    data['wv_o'] = data['o'].apply(wv_p.process)
    data = data[~data['wv_v'].isnull() & ~data['wv_o'].isnull()]

    return data


def create_org_map(subjects):

    org_map = {}

    total = len(subjects)
    count = 0
    success = 0
    failure = 0
    for subject in subjects:
        count = count + 1
        print(f"processing {count} out of {total}")
        org_map[subject] = get_org(subject)

        if org_map[subject] is not None:
            success = success + 1
        else:
            failure = failure + 1
        print(f"subject: {subject}, match: {org_map[subject]}")
        print(f"stat success {success}, failure {failure}")

    return org_map


if __name__ == "__main__":

    print("tasks for pr news wire")


    # title processing
    # 1. download titles (web.wayback_machine.title.get_titles .clean_titles)
    # 2. extract s, v, o (create_svo)
    # 3. create word vector (create_wv_average, create_wv_separate)
    # 4. create organization map (create_org_map)
    # 5. create ticker map for sp500 (nlp.util.match.create_ticker_map)
    # 6. create ticker sector for sp500 (straight from file)
    # 7. retrieve prices from yahoo finance (finance.util.common.get_prices)

    # kmean clustering
    # start jupyter lab
    # export PYTHONPATH=/Users/shuowang/pycharm/p001/repo
    # jupyter lab



