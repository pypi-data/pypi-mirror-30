import pickle
from pathlib import Path
from collections import defaultdict

MODEL_LOC = Path(__file__).parent / 'data' / 'model.p'


class CaseCount(object):

    def __init__(self, word):
        self.word = word
        self.cap = 0
        self.total = 0

    @property
    def percentage(self):
        if self.total == 0:
            return None
        return self.cap / self.total

    def __add__(self, other):
        if self.word != other.word:
            raise ValueError("Words must match.")
        count = CaseCount(self.word)
        count.cap = self.cap + other.cap
        count.total = self.total + other.total
        return count

    def __radd__(self, other):
        if other == 0:
            return self
        return self.__add__(other)

    def __eq__(self, other):
        return (
            self.word == other.word and
            self.cap == other.cap and
            self.total == other.total
        )

    def __str__(self):
        return f"CaseCount for `{self.word}`\n\tCap: {self.cap}\n\tTotal: {self.total}\n\tPercentage: {self.percentage}"

    def __repr__(self):
        return self.__str__()


class TrueCase(defaultdict):

    def __missing__(self, key):
        val = self[key] = CaseCount(key)
        return val

    def __add__(self, other):
        if other is None:
            return self
        for k in other:
            self[k] += other[k]
        return self

    def __radd__(self, other):
        if other == 0 or other is None:
            return self
        return self.__add__(other)

    def save(self, file_name=MODEL_LOC):
        pickle.dump(self, open(file_name, 'wb'))

    @classmethod
    def load(cls, file_name=MODEL_LOC):
        return pickle.load(open(file_name, 'rb'))

    def __call__(self, doc):
        return [self[token] for token in doc]

    def train(self, doc):
        for token in doc:
            lower_token = token.lower()
            if token[0].isupper():
                self[lower_token].cap += 1
            self[lower_token].total += 1
