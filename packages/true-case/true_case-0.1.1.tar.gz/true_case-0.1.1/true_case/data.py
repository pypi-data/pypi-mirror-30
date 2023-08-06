from functools import partial


class Reader(object):

    def __init__(self, file_name, clean_func):
        self.file_name = file_name
        self.clean_func = clean_func

    def __call__(self):
        corpus = open(self.file_name).read()
        corpus = self.clean_func(corpus)
        return corpus


def cnn_clean(corpus, start_cutoff=50):
    start_index = corpus.find("--")
    if start_index < start_cutoff and start_index > 0:
        corpus = corpus[start_index + 2:]
    end_index = corpus.find("@highlight")
    if end_index >= 0:
        corpus = corpus[:end_index]
    return corpus


def dm_clean(corpus):
    end_index = corpus.find("@highlight")
    if end_index >= 0:
        corpus = corpus[:end_index]
    return corpus


def dataset(files, reader, clean, preprocess):
    readers = [reader(x, clean) for x in files]
    for r in readers:
        yield r, preprocess


def preprocess(data):
    return data.split()

cnn_data = partial(
    dataset,
    reader=Reader, clean=cnn_clean, preprocess=preprocess
)

dm_data = partial(
    dataset,
    reader=Reader, clean=dm_clean, preprocess=preprocess
)
