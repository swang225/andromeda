import requests

from web.html_parser import PRNewswireParser
from nlp.util.common import clean_sentence, is_english
from util import read_pickle, nkeys


def get_archive_article(url, timestamp):
    # get article from wayback machine archive

    archive_url = f'https://web.archive.org/web/{timestamp}id_/{url}'

    # print(archive_url)

    r = requests.get(url=archive_url)

    res = r.text

    return res


def process_article(title, info):
    ts, url = info['url']
    raw = get_archive_article(url, ts)

    print('got article...')

    parser = PRNewswireParser()
    parser.feed(raw)
    article = parser.res
    article['title'] = clean_sentence(article['title'])
    article['body'] = clean_sentence(article['body'])

    try:
        if not is_english(' '.join([article['title'], article['body']])):
            print(f'article is not in english: {title}')
            return None
    except:
        print(f'invalid article: {title}')
        # print(' '.join([article['title'], article['body']]))
        # print('skipping..')
        return 'invalid'

    return article


def process_articles(data, **kwargs):

    articles = {}
    fail_art = {}
    inva_art = {}
    print(f'running for {len(data)} articles')
    for k, v in data.items():

        if len(k) > 0:
            try:
                print(f'processing: {k[:min(10, len(k))]}...')
                res = process_article(k, v)

                if res == 'invalid':
                    inva_art[k] = v
                elif res is not None:
                    articles[k] = res

            except:
                fail_art[k] = v
                # print(f'failure processing {k}')

    return articles, fail_art, inva_art


if __name__ == '__main__':

    import platform
    import multiprocessing
    if platform.system() == "Darwin":
        multiprocessing.set_start_method('spawn')

    from util import chunk_dict, multi_run
    path = '/Users/shuowang/pycharm/p001/data/process_articles_res'
    data_file = '/Users/shuowang/pycharm/p001/code/test003_prnewswire_v01/data/prnews_title_dict.pkl'
    res = chunk_dict(nkeys(read_pickle(data_file), 3))
    multi_run(process_articles, path, res)
