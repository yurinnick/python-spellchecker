import operator
import json
import time
import sys


class Spellchecker:
    def __init__(self, dictionary_path='en.txt', bigram_path='bigrams.json'):
        with open(dictionary_path) as f:
            self.dictionary = f.read().splitlines()
        try:
            print 'Loading %s' % bigram_path
            with open(bigram_path) as f:
                self.bigram_id = json.load(f)
        except IOError:
            print '%s not found! Generating...' % bigram_path
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
        word_indexes = {}
        word_count = {}
        for bigram in proccesed_word:
            words_ids = set(self.bigram_id[bigram])
            for word_id in words_ids:
                if word_id in word_count:
                    word_count[word_id] += 1
                else:
                    word_count[word_id] = 1
        top_words_ids = set([data[0] for data in sorted(
            word_count.items(),
            key=operator.itemgetter(1), reverse=True)[:200]])
        for word_id in top_words_ids:
            word_indexes[word_id] = self.levenshtein_distance(
                word,
                self.dictionary[word_id])
        top_entries = sorted(
            word_indexes.items(),
            key=operator.itemgetter(1))[:n]

        for word_id in top_entries:
            print self.dictionary[word_id[0]], word_id

    @staticmethod
    def levenshtein_distance(word1, word2):
        if len(word1) < len(word2):
            word1, word2 = word2, word1
        distances = range(len(word1) + 1)
        for index1, char1 in enumerate(word1):
            new_distances = [index1 + 1]
            for index2, char2 in enumerate(word2):
                if char1 == char2:
                    new_distances.append(distances[index2])
                else:
                    new_distances.append(1 + min(distances[index2],
                                                 distances[index2 + 1],
                                                 new_distances[-1]))
            distances = new_distances
        return distances[-1]

def main(argv=None):
    start = time.time()
    sp = Spellchecker()
    sp.spellcheck(argv[1], n=10)
    end = time.time()
    print end - start

if __name__ == '__main__':
    sys.argv.append('amimal')
    main(sys.argv)

