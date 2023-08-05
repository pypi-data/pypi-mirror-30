__version__ = '0.0.1'

import math

# Scoring ---------------------------------------------------------------------

from nltk.metrics import aline
from functools import lru_cache

@lru_cache(maxsize=None)
def kon_delta(p, q):
    """For two phonemes, get distance."""
    len_p, len_q = len(p), len(q)
    if len_p == len_q == 1:
        # phoneme is individual token
        return aline.delta(p, q)
    else:
        # phoneme is a pair of tokens
        paired = zip(p*len_q, q*len_p)
        return sum(aline.delta(ii, jj) for ii, jj in  paired) / 2

def utt_distance(ps, qs, low_thresh = 0):
    if len(ps) != len(qs):
        raise Exception("len mismatch, p - %s, q - %s" %(len(ps), len(qs)))

    ttl = sum(kon_delta(p, q) for p, q in zip(ps, qs))
    return ttl if ttl > low_thresh else math.inf

# for a word, match against all words with equal phoneme length
def min_distance(words, target):
    return min(utt_distance(wrd, target) for wrd in words)



# AStar -----------------------------------------------------------------------

from frozendict import frozendict
from itertools import chain
from astar import AStar

def parse_sentence(sent, d):
    tmp = sent.lower().split(" ", 1)
    tokens = []
    count = 0
    
    while len(tmp) > 1:
        word, rest = tmp
        if word == "":
            tokens.append(dict(char = " ", word = " ", word_pos = count))
        else:
            for ltr in sentence_to_phonemes(word, d):
                tokens.append(dict(char = ltr, word = word, word_pos = count))
        count += 1
        tmp = rest.split(" ", 1)

    # end token
    tokens.append(dict(char = None, word = None, word_pos = None))    

    for ii, token in enumerate(tokens):
        token['indx'] = ii
    
    return [frozendict(x) for x in tokens]


def sentence_to_phonemes(sent, d):
    words = sent.lower().split(" ")
    split = lambda wrd:  d.loc[d.index == wrd, 'split'].iloc[0]
    return list(chain.from_iterable(map(split, words)))

class HasteTar(AStar):

    def __init__(self, sentence, d, d_parse = None, max_len = 12):
        self.sentence = sentence
        self.nodes = parse_sentence(sentence, 
                                    d_parse if d_parse is not None else d)
        self.max_len = max_len
        self.d = d


    def neighbors(self, node):                          # abstract methods ----
        start = node['indx'] + 1
        neighbors = self.nodes[start:start + self.max_len]
        return neighbors


    def distance_between(self, src, dst):
        d = self.d
        dst_phones = [x['char'] for x in self.nodes_between(src, dst)]
        candidates = d.loc[d.length == len(dst_phones), 'split']
        min_dist = min_distance(candidates, dst_phones)

        return self.cost_func(min_dist, len(dst_phones))


    def heuristic_cost_estimate(self, src, goal):
        if src is goal:
            return 0
        
        dst_phones = [x['char'] for x in self.nodes_between(src, goal)]
        return self.cost_func(1, len(dst_phones))


    def nodes_between(self, src, dst):                      # helper funcs ----
        return self.nodes[src['indx']:dst['indx']]


    @staticmethod
    def cost_func(distance, length):
        return distance * 2#(1 / length)


    def best_fit_words(self, dst):
        d_len = self.d.loc[self.d.length == len(dst)]
        word_splits = zip(d_len['word'], d_len['split'])
        dist = {wrd: utt_distance(splits, dst) for wrd, splits in word_splits}
        return {k: v for k, v in dist.items() if v == min(dist.values())}


    def path_to_phonemes(self, path):
        out = []
        for start, end in zip(path[:-1], path[1:]):
            out.append([x['char'] for x in self.nodes_between(start, end)])
        return out



if __name__ == "__main__":
    import pandas as pd
    d_orig = pd.read_csv('cmudict-xsampa.csv')
    d_orig['split'] = d_orig['pronounce'].apply(lambda s: s.split(" "))
    d_orig['length'] = d_orig['split'].apply(len)
    d_orig.index = d_orig.word
    print('unique pronunciations:', len(d_orig.pronounce.unique()))

    # for homophones, keep only most popular
    d_orig.sort_values(by = 'prob', ascending = False, inplace = True)
    d = d_orig.drop_duplicates(subset = 'pronounce')

    sentence = """her hair
will keep changing
it will grow and we will cut it
and maybe it will turn
white or grey or silver
and i wont recognize her
the way i recognize her now,
her hair plastered to her cheeks .""".replace('.', '').replace(',','').replace('\n', " ")
    d_small = d[d.prob > -16]

    ht = HasteTar(sentence, d_small, d_orig)
    out = list(ht.astar(ht.nodes[0], ht.nodes[-1]))
    for phons in ht.path_to_phonemes(out):
        print(", ".join(ht.best_fit_words(phons).keys()))

