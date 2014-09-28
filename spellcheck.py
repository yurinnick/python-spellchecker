import operator
import json
import math
import time
import sys
from multiprocessing import Queue
from multiprocessing import Process


class Spellchecker:
    def __init__(
        self,
        dictionary_path='en.txt',
        bigram_path='bigrams.json'
    ):
        with open(dictionary_path) as f:
            self.dictionary = f.read().splitlines()
        try:
            print 'Loading %s' % bigram_path
            with open(bigram_path) as f:
                self.bigram_id = json.load(f)
        except IOError:
            print '%s not found! Generating...'
            self.bigram_id = self.generate_bigrams(self.dictionary)
            print 'Processed %d words' % len(self.dictionary)
        except Exception as e:
            raise e

    def generate_bigrams(self, dictionary):
        bigram_word_id = {}
        for idx, word in enumerate(dictionary):
            proccesed_word = self.bigram_word(word)
            for bigram in proccesed_word:
                if bigram in bigram_word_id.keys():
                    bigram_word_id[bigram].append(idx)
                else:
                    bigram_word_id[bigram] = [idx]
        with open('bigrams.json', 'w') as outfile:
            json.dump(bigram_word_id, outfile)
        return bigram_word_id

    def bigram_word(self, word):
        return [word[i-2:i] for i in range(2, len(word) + 1)]

    def spellcheck(self, word, n=5):
        print 'Checking %s word...' % word
        proccesed_word = self.bigram_word(word)
        word_indexs = {}
        for bigram in proccesed_word:
            words_ids = self.bigram_id[bigram]
            word_indexs = self.mp_l_distance(word, words_ids, 4)
        top_entries = sorted(
            word_indexs.items(),
            key=operator.itemgetter(1))[:n]

        for word_id in top_entries:
            print self.dictionary[word_id[0]], word_id

    def mp_l_distance(self, word, word_id_list, nprocs):
        def worker(word, word_id_list, values_list):
            word_indexs = {}
            for word_id in word_id_list:
                if not word_id in word_indexs.keys():
                    word_indexs[word_id] = self.levenshtein_distance(
                        word,
                        self.dictionary[word_id])
            values_list.put(word_indexs)

        values_list = Queue()
        chunksize = int(math.ceil(len(word_id_list) / float(nprocs)))
        procs = []

        for i in range(nprocs):
            p = Process(
                target=worker,
                args=(
                    word,
                    word_id_list[chunksize * i:chunksize * (i + 1)],
                    values_list))
            procs.append(p)
            p.start()

        resultdict = {}
        for i in range(nprocs):
            resultdict.update(values_list.get())
        for p in procs:
            p.join()

        return resultdict

    def levenshtein_distance(self, word1, word2):
        if len(word1) < len(word2):
            word1, word2 = word2, word1
        distances = range(len(word1) + 1)
        for index1, char1 in enumerate(word1):
            newDistances = [index1 + 1]
            for index2, char2 in enumerate(word2):
                if char1 == char2:
                    newDistances.append(distances[index2])
                else:
                    newDistances.append(1 + min(distances[index2],
                                                distances[index2 + 1],
                                                newDistances[-1]))
            distances = newDistances
        return distances[-1]

start = time.time()
sp = Spellchecker()
sp.spellcheck(sys.argv[1], n=10)
end = time.time()
print end - start
