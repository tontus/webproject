from __future__ import division
import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import brown
import math
import numpy as np
import sys
import csv

# nltk.download()
class Calculate:
    ALPHA = 0.2
    BETA = 0.45
    ETA = 0.4
    PHI = 0.2
    DELTA = 0.85

    brown_freqs = dict()
    N = 0
    def __init__(self):
        self.ALPHA = 0.2
        self.BETA = 0.45
        self.ETA = 0.4
        self.PHI = 0.2
        self.DELTA = 0.85
        self.brown_freqs = dict()
        self.N = 0




######################### word similarity ##########################

    def get_best_synset_pair(self,word_1, word_2):
        max_sim = -1.0
        synsets_1 = wn.synsets(word_1)
        synsets_2 = wn.synsets(word_2)
        if len(synsets_1) == 0 or len(synsets_2) == 0:
            return None, None
        else:
            max_sim = -1.0
            best_pair = None, None
            for synset_1 in synsets_1:
                for synset_2 in synsets_2:
                    sim = wn.path_similarity(synset_1, synset_2)
                    if sim > max_sim:
                        max_sim = sim
                        best_pair = synset_1, synset_2
            return best_pair


    def length_dist(self,synset_1, synset_2):
        l_dist = 10000000
        if synset_1 is None or synset_2 is None:
            return 0.0
        if synset_1 == synset_2:
            # if synset_1 and synset_2 are the same synset return 0
            l_dist = 0.0
        else:
            wset_1 = set([str(x.name()) for x in synset_1.lemmas()])
            wset_2 = set([str(x.name()) for x in synset_2.lemmas()])
            if len(wset_1.intersection(wset_2)) > 0:
                # if synset_1 != synset_2 but there is word overlap, return 1.0
                l_dist = 1.0
            else:
                # just compute the shortest path between the two
                l_dist = synset_1.shortest_path_distance(synset_2)
                if l_dist is None:
                    l_dist = 0.0
        # normalize path length to the range [0,1]
        return math.exp(-self.ALPHA * l_dist)


    def hierarchy_dist(self,synset_1, synset_2):
        h_dist = 10000000
        if synset_1 is None or synset_2 is None:
            return h_dist
        if synset_1 == synset_2:
            # return the depth of one of synset_1 or synset_2
            h_dist = max([x[1] for x in synset_1.hypernym_distances()])
        else:
            # find the max depth of least common subsumer
            hypernyms_1 = {x[0]: x[1] for x in synset_1.hypernym_distances()}
            hypernyms_2 = {x[0]: x[1] for x in synset_2.hypernym_distances()}
            lcs_candidates = set(hypernyms_1.keys()).intersection(
                set(hypernyms_2.keys()))
            if len(lcs_candidates) > 0:
                lcs_dists = []
                for lcs_candidate in lcs_candidates:
                    lcs_d1 = 0
                    if hypernyms_1.has_key(lcs_candidate):
                        lcs_d1 = hypernyms_1[lcs_candidate]
                    lcs_d2 = 0
                    if hypernyms_2.has_key(lcs_candidate):
                        lcs_d2 = hypernyms_2[lcs_candidate]
                    lcs_dists.append(max([lcs_d1, lcs_d2]))
                h_dist = max(lcs_dists)
            else:
                h_dist = 0
        return ((math.exp(self.BETA * h_dist) - math.exp(-self.BETA * h_dist)) /
                (math.exp(self.BETA * h_dist) + math.exp(-self.BETA * h_dist)))


    def word_similarity(self, word_1, word_2):
        for syn in wn.synsets(word_1):
            for l in syn.lemmas():
                if l.antonyms():
                    if l.antonyms()[0].name() == word_2:
                        return 0

        synset_pair = self.get_best_synset_pair(word_1, word_2)
        return (self.length_dist(synset_pair[0], synset_pair[1]) *
                self.hierarchy_dist(synset_pair[0], synset_pair[1]))


    ######################### sentence similarity ##########################

    def most_similar_word(self,word, word_set):
        max_sim = -1.0
        sim_word = ""
        for ref_word in word_set:
            sim = self.word_similarity(word, ref_word)
            if sim > max_sim:
                max_sim = sim
                sim_word = ref_word
        return sim_word, max_sim


    def info_content(self,lookup_word):

        if self.N == 0:
            # poor man's lazy evaluation
            for sent in brown.sents():
                for word in sent:
                    word = word.lower()
                    if not self.brown_freqs.has_key(word):
                        self.brown_freqs[word] = 0
                        self.brown_freqs[word] = self.brown_freqs[word] + 1
                    self.N = self.N + 1
        lookup_word = lookup_word.lower()
        n = 0 if not self.brown_freqs.has_key(lookup_word) else self.brown_freqs[lookup_word]
        return 1.0 - (math.log(n + 1) / math.log(N + 1))


    def semantic_vector(self,words, joint_words, info_content_norm):
        sent_set = set(words)
        semvec = np.zeros(len(joint_words))
        i = 0
        for joint_word in joint_words:
            if joint_word in sent_set:
                # if word in union exists in the sentence, s(i) = 1 (unnormalized)
                semvec[i] = 1.0
                if info_content_norm:
                    semvec[i] = semvec[i] * math.pow(self.info_content(joint_word), 2)
            else:
                # find the most similar word in the joint set and set the sim value
                sim_word, max_sim = self.most_similar_word(joint_word, sent_set)
                semvec[i] = self.PHI if max_sim > self.PHI else 0.0
                if info_content_norm:
                    semvec[i] = semvec[i] * self.info_content(joint_word) * self.info_content(sim_word)
            i = i + 1
        return semvec


    def semantic_similarity(self,sentence_1, sentence_2, info_content_norm):
        words_1 = nltk.word_tokenize(sentence_1)
        words_2 = nltk.word_tokenize(sentence_2)

        for w1 in words_1:
            for syn in wn.synsets(w1):
                for l in syn.lemmas():
                    if l.antonyms():
                        for w2 in words_2:
                            if l.antonyms()[0].name() == w2:
                                return 0

        joint_words = set(words_1).union(set(words_2))
        vec_1 = self.semantic_vector(words_1, joint_words, info_content_norm)
        vec_2 = self.semantic_vector(words_2, joint_words, info_content_norm)
        return np.dot(vec_1, vec_2.T) / (np.linalg.norm(vec_1) * np.linalg.norm(vec_2))


    ######################### word order similarity ##########################

    def word_order_vector(self,words, joint_words, windex):
        wovec = np.zeros(len(joint_words))
        i = 0
        wordset = set(words)
        for joint_word in joint_words:
            if joint_word in wordset:
                # word in joint_words found in sentence, just populate the index
                wovec[i] = windex[joint_word]
            else:
                # word not in joint_words, find most similar word and populate
                # word_vector with the thresholded similarity
                sim_word, max_sim = self.most_similar_word(joint_word, wordset)
                if max_sim > self.ETA:
                    wovec[i] = windex[sim_word]
                else:
                    wovec[i] = 0
            i = i + 1
        return wovec


    def word_order_similarity(self,sentence_1, sentence_2):
        words_1 = nltk.word_tokenize(sentence_1)
        words_2 = nltk.word_tokenize(sentence_2)
        joint_words = list(set(words_1).union(set(words_2)))
        windex = {x[1]: x[0] for x in enumerate(joint_words)}
        r1 = self.word_order_vector(words_1, joint_words, windex)
        r2 = self.word_order_vector(words_2, joint_words, windex)

        for w1 in words_1:
            for syn in wn.synsets(w1):
                for l in syn.lemmas():
                    if l.antonyms():
                        for w2 in words_2:
                            if l.antonyms()[0].name() == w2:
                                if len(sentence_1) < len(sentence_1) - 4:
                                    return 0

        return 1.0 - (np.linalg.norm(r1 - r2) / np.linalg.norm(r1 + r2))


    ######################### overall similarity ##########################

    def similarity(self,sentence_1, sentence_2, info_content_norm):
        return self.DELTA * self.semantic_similarity(sentence_1, sentence_2, info_content_norm) + \
               (1.0 - self.DELTA) * self.word_order_similarity(sentence_1, sentence_2)


    ######################### main / test ##########################

    word_pairs = [
        ["asylum", "fruit", 0.21],
        ["autograph", "shore", 0.29],
        ["autograph", "signature", 0.55],
        ["automobile", "car", 0.64],
        ["bird", "woodland", 0.33],
        ["boy", "rooster", 0.53],
        ["boy", "lad", 0.66],
        ["boy", "sage", 0.51],
        ["cemetery", "graveyard", 0.73],
        ["coast", "forest", 0.36],
        ["coast", "shore", 0.76],
        ["cock", "rooster", 1.00],
        ["cord", "smile", 0.33],
        ["cord", "string", 0.68],
        ["cushion", "pillow", 0.66],
        ["forest", "graveyard", 0.55],
        ["forest", "woodland", 0.70],
        ["furnace", "stove", 0.72],
        ["glass", "tumbler", 0.65],
        ["grin", "smile", 0.49],
        ["gem", "jewel", 0.83],
        ["hill", "woodland", 0.59],
        ["hill", "mound", 0.74],
        ["implement", "tool", 0.75],
        ["journey", "voyage", 0.52],
        ["magician", "oracle", 0.44],
        ["magician", "wizard", 0.65],
        ["midday", "noon", 1.0],
        ["oracle", "sage", 0.43],
        ["serf", "slave", 0.39]
    ]
    for word_pair in word_pairs:
        print "%s\t%s\t%.2f\t%.2f" % (word_pair[0], word_pair[1], word_pair[2],
                                      word_similarity(word_pair[0], word_pair[1]))

    sentence_pairs = [
        ["I like that bachelor.he is cute", "I like that unmarried man. he looks good", 0.561],
        ["Newton's second law states that rate of change of momentum is proportional to force applied in the object",
         "Newton's second law states that rate of change of momentum is proportional to force applied in the object",
         0.977],
        ["Red alcoholic drink.", "A bottle of wine.", 0.585],
        ["Red alcoholic drink.", "Fresh orange juice.", 0.611],
        ["Red alcoholic drink.", "An English dictionary.", 0.0],
        ["Red alcoholic drink.", "Fresh apple juice.", 0.420],
        ["A glass of cider.", "A full cup of apple juice.", 0.678],
        ["It is a dog.", "That must be your dog.", 0.739],
        ["It is a dog.", "It is a pet.", 0.623],
        ["It is a dog.", "It is a pig.", 0.790],
        ["Dogs are animals.", "They are common pets.", 0.738],
        ["Canis familiaris are animals.", "Dogs are common pets.", 0.362],
        ["I have a pen.", "Where do you live?", 0.0],
        ["I have a pen.", "Where is ink?", 0.129],
        ["I have a hammer.", "Take some nails.", 0.508],
        ["I have a hammer.", "Take some apples.", 0.121],
        ["I love hammer.", "I hate hammer", 0.121]
    ]
    for sent_pair in sentence_pairs:
        sent_pair.append(similarity(sent_pair[0], sent_pair[1], False))
        sent_pair.append(similarity(sent_pair[0], sent_pair[1], True))
        print "%s\t%s\t%.3f\t%.3f\t%.3f" % (sent_pair[0], sent_pair[1], sent_pair[2],
                                            similarity(sent_pair[0], sent_pair[1], False),
                                            similarity(sent_pair[0], sent_pair[1], True))
    
    with open('output.csv', 'wb') as test_file:
        file_writer = csv.writer(test_file, quoting=csv.QUOTE_ALL, quotechar=' ')
        file_writer.writerows(sentence_pairs)