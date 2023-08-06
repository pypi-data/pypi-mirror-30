from enum import Enum
from pathlib import Path
import multiprocessing as mp
from multiprocessing import Process, Queue

from tqdm import tqdm

from true_case.data import cnn_data, dm_data
from true_case.model import TrueCase, MODEL_LOC


Signal = Enum("Signal", "DONE")


def train_doc(inputs, model=TrueCase):
    data = inputs[0]
    preprocess = inputs[1]
    corpus = preprocess(data())
    m = model()
    m.train(corpus)
    return m


def aggregate_model(model, in_q, out_q):
    base = model()
    new = None
    while new is not Signal.DONE:
        base += new
        new = in_q.get()
    out_q.put(base)


def train(train_func, model, save_loc):
    data_q = Queue()
    result_q = Queue()
    aggregator = Process(target=aggregate_model, args=(model, data_q, result_q))
    aggregator.start()

    cnn_files = list((Path(__file__).parent / 'data' / 'cnn_stories_tokenized').glob('*.story'))
    dm_files = list((Path(__file__).parent / 'data' / 'dm_stories_tokenized').glob('*.story'))

    cnn = cnn_data(cnn_files)
    dm = dm_data(dm_files)

    datasets = [cnn, dm]
    lengths = [len(cnn_files), len(dm_files)]

    pool = mp.Pool(processes=mp.cpu_count())
    for data, count in zip(datasets, lengths):
        for x in tqdm(pool.imap_unordered(train_func, data), total=count):
            data_q.put(x)

    data_q.put(Signal.DONE)
    result = result_q.get()
    aggregator.join()
    result.save(save_loc)
    return result


def main():
    train(train_doc, TrueCase, MODEL_LOC)

if __name__ == "__main__":
    main()
