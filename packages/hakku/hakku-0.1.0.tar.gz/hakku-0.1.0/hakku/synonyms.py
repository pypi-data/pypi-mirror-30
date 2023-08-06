# -*- coding: utf-8 -*-
""" Heuristic synonym detector and combiner. """

import string, re

CONVERSIONS = {'optimisation':'optimization',
               'maximisation':'maximization',
               'alexandroff':'alexandrov',
               'kullback-liebler':'kullback-leibler',
               'modelling':'modeling',
               'labelling':'labeling',
               '-based':' based'}

def process_word(word):
    word = re.sub('  *',' ',word)
    word = re.sub('--*','-',word)
    word = re.sub(' - ','-',word)
    word = re.sub(' \(.*?\)$','',word)

    # FIXME: This is not a good way to handle plurals:
    word = re.sub('sses$','ss',word)
    word = re.sub('(?<!ser)ies$','y',word)
    word = re.sub('(?<!s)s$','',word)

    # Revert some broken words:
    word = re.sub('qo$','qos',word)
    word = re.sub('chao$','chaos',word)
    word = re.sub('baye$','bayes',word)

    word = re.sub('kurtosi$','kurtosis',word)
    word = re.sub('analysi$','analysis',word)
    word = re.sub('basi$','basis',word)
    word = re.sub('genesi$','genesis',word)
    word = re.sub('synthesi$','synthesis',word)
    word = re.sub('axi$','axis',word)
    word = re.sub('hypothesi$','hypothesis',word)
    word = re.sub('diagnosi$','diagnosis',word)
    word = re.sub('metropoli$','metropolis',word)

    word = re.sub('consensu$','consensus',word)
    word = re.sub('bia$','bias',word)
    word = re.sub('focu$','focus',word)
    word = re.sub('campu$','campus',word)
    word = re.sub('heterogeneou$','heterogeneous',word)
    word = re.sub('continuou$','continuous',word)
    word = re.sub('viru$','virus',word)    
    word = re.sub('versu$','versus',word)

    word = re.sub('meshe$','mesh',word)
    
    word = re.sub('k-mean$','k-means',word)
    word = re.sub('knows what it know$','knows what it knows',word)
    word = re.sub('least square$','least squares',word)

    for a,b in CONVERSIONS.iteritems():
        word = string.replace(word,a,b)
        
    return word

def detect_synonyms(uniqlist):
    """Returns a reduced word list, and a dictionary that maps
    original words to indices of reduced words.

    Note: uniqlist must contain each word only once.
    """

    ind_of_word = {}
    reduced_list = []

    for original_word in uniqlist:
        # apply conversions and heuristics
        normalized_word = process_word(original_word)
        if reduced_list.count(normalized_word)>0:
            index = reduced_list.index(normalized_word)
        else:
            index = len(reduced_list)
            reduced_list.append(normalized_word)
            
        ind_of_word[original_word] = index

    return (reduced_list, ind_of_word)

