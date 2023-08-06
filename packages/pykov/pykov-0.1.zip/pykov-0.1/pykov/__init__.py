import random
import pickle


class Chain:
    def __init__(self):
        self.chainchances = {}
        self.worddata = {}

    def add_text(self, text):
        words = text.split(' ')
        for index, word in enumerate(words):
            if word in self.chainchances:
                try:
                    self.chainchances[word].append(words[index + 1])
                except IndexError:
                    pass
            else:
                try:
                    self.chainchances[word] = [words[index + 1]]
                except IndexError:
                    pass

    def generate_words(self, amount: str, start_word=None):
        if not start_word:
            start_word = random.choice(list(self.chainchances))
        endstring = [start_word]
        firstword = random.choice(self.chainchances[start_word])
        for x in range(amount):
            try:
                nw = random.choice(self.chainchances[firstword])
            except KeyError:
                nw = random.choice(list(self.chainchances))
            firstword = nw
            endstring.append(firstword)
        return ' '.join(endstring)

    def save_chain(self, path):
        try:
            pickle.dump(self, open(path, 'wb'))
        except PermissionError:
            raise PermissionError('unable to write file to path')


def load_chain(path: str):
    try:
        pl = pickle.load(open(path, 'rb'))
        if type(pl) != Chain:
            raise TypeError('file loaded was not a chain file')
        return pl
    except FileNotFoundError:
        raise FileNotFoundError('no file found at that path')
    except pickle.UnpicklingError:
        raise TypeError('file loaded was not a chain file')