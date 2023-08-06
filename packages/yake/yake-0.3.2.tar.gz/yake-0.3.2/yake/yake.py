# -*- coding: utf-8 -*-

"""Main module."""

import string
import os
import jellyfish

from yake.datarepresentation import DataCore

class KeywordExtractor(object):

    def __init__(self, lan="en", n=3, dedupLim=0.8, dedupFunc='levenshtein', windowsSize=2, top=20, features=None):

        self.lan = lan

        dir_path = os.path.dirname(os.path.realpath(__file__))
        
        local_path = os.path.join("StopwordsList", "stopwords_%s.txt" % lan[:2].lower())
        resource_path = os.path.join(dir_path,local_path)

        with open(resource_path, encoding='utf8') as stop_fil:
            self.stopword_set = set( stop_fil.read().lower().split("\n") )

        self.n = n
        self.top = top
        self.dedupLim = dedupLim
        self.features = features
        self.windowsSize = windowsSize

        if dedupFunc == 'jaro_winkler' or dedupFunc == 'jaro':
            self.dedu_function = self.jaro
        else:
            self.dedu_function = self.levs

    def jaro(self, cand1, cand2):
        return jellyfish.jaro_winkler(cand1, cand2 )

    def levs(self, cand1, cand2):
        return 1.-jellyfish.levenshtein_distance(cand1, cand2 ) / max(len(cand1),len(cand2))
    
    def extract_keywords(self, text):

        text = text.replace('\n\t',' ')

        dc = DataCore(text=text, stopword_set=self.stopword_set, windowsSize=self.windowsSize, n=self.n)
        dc.build_single_terms_features(features=self.features)
        dc.build_mult_terms_features(features=self.features)

        candidates = sorted([(cand.H, cand.unique_kw) for cand in dc.candidates.values() if cand.isValid()], key=lambda x: x[0])
        resultSet = []

        for cand in candidates:

            if len(resultSet) == self.top:
                break

            if len(resultSet) == 0:
                resultSet.append(cand)
            toAdd = True

            for candResult in resultSet:
                dist = self.dedu_function(cand[1], candResult[1])
                if dist > self.dedupLim:
                    toAdd = False
                    break

            if toAdd:
                resultSet.append(cand)

        return resultSet
