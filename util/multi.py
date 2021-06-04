import multiprocessing as mp
import os

from andromeda.util import write_pickle


def _save_data(res, path, idx):

    try:
        path = os.path.join(path, f'{idx}.pkl')
        print(f'writing results {idx} to {path}')
        write_pickle(res, path)
    except:
        print(f'failed to save intermediate results {idx} to path {path}')


def multi_process(func, path, idx, data, ignore, **kwargs):

    if path is not None:
        if not ignore and os.path.exists(path):
            print(f"data already exist for {path}")
            return
        res = func(data, **kwargs)
        _save_data(res, path, idx)
    else:
        func(data, **kwargs)


def multi_run(func,
              path,
              data_list,
              num_workers=10,
              ignore=False,
              **kwargs):

    print(f'processing {len(data_list)} tasks...')

    pool = mp.Pool(num_workers)
    with mp.Manager() as manager:

        for idx, data in enumerate(data_list):

            curr_kwargs = dict(
                func=func,
                path=path,
                idx=idx,
                data=data,
                ignore=ignore,
            )
            curr_kwargs.update(kwargs)

            pool.apply_async(multi_process, kwds=curr_kwargs)

        pool.close()
        pool.join()


if __name__ == '__main__':

    data_list = [1, 2, 3]

    def test_func(x):
        print(x * x)

    multi_run(func=test_func, path=None, data_list=data_list)

