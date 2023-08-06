"""
Hakku - tool for article clustering based on word counts in titles
and keywords. This file generates the word occurrence matrix.
"""

import sys
import re
from codecs import open as copen
import numpy as np

from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.snowball import EnglishStemmer
from nltk.corpus import stopwords

glob_lm = WordNetLemmatizer()
glob_st = EnglishStemmer()
try:
    glob_sw = stopwords.words('english')
except LookupError:
    import nltk
    nltk.download("stopwords")
    glob_sw = stopwords.words('english')

def get_words_of_string(st, extended_stopwords, stemmed_extended_stopwords):
    """Normalization, stemming, other things here."""
    words = re.split(r"\W+", st.lower())
    #words = map(glob_lm.lemmatize, words)
    words = [w for w in words if w not in glob_sw]
    words = [w for w in words if w not in extended_stopwords]
    words = map(glob_st.stem, words)
    words = [w for w in words if w not in stemmed_extended_stopwords]
    # Remove single characters and numbers:
    wordsf = filter(lambda x: len(x) > 1, words)
    wordsf = filter(lambda x: (not x.isdigit()), words)
    return list(wordsf)

def create_article_word_matrix(alist, extended_stopwords, stemmed_extended_stopwords):
    """Returns a tuple (mat, articleIDs, words) where:

         mat = binary matrix where each row corresponds to one article
               in the given article list, and each column corresponds
               to one word in the list of unique words found in titles
               and abstracts of all the articles

         articleIDs = list of article identifications (TODO: which
               format?)

         words = list of unique words found in lexicographic order
    """

    wordlist = []

    # Pass 1: get raw word list
    for a in alist:
        abstr = a.abstract.replace("All rights reserved.", "")
        wordlist = wordlist + get_words_of_string(a.title,
                extended_stopwords, stemmed_extended_stopwords)
        wordlist = wordlist + get_words_of_string(abstr,
                extended_stopwords, stemmed_extended_stopwords)

    # Make list unique:
    # "sort(unique(wordlist))":
    wordset = set(wordlist)
    orig_wlist = list(wordset)
    orig_wlist.sort()

    # # indofword and final word list comes from synonym detector:
    # (uniqlist, indofword) = detect_synonyms(orig_wlist)
    uniqlist = orig_wlist
    indofword = {}
    for ind in range(len(uniqlist)):
        indofword[uniqlist[ind]] = ind

    # Pass 2: create occurrence matrix
    nwords = len(uniqlist)
    narticles = len(alist)

    m = np.zeros((narticles, nwords))

    ai = []
    for row in range(len(alist)):
        a = alist[row]
        ai.append("%s || %s"%(a.title, a.source))

        all_words = []
        all_words = all_words + get_words_of_string(a.title,
                extended_stopwords, stemmed_extended_stopwords)
        abstr = a.abstract.replace("All rights reserved.", "")
        all_words = all_words + get_words_of_string(abstr,
                extended_stopwords, stemmed_extended_stopwords)

        for w in all_words:
            col = indofword[w]
            m[row, col] = 1

    return (m, ai, uniqlist)

def create_article_author_matrix(alist):
    """Creates a matrix articles x authors, marking with 1 the articles
    where the authors participated in.
    Input:  alist - list of articles in a data structure.
    Output: result - articles x authors binary matrix."""

    # Collect all authors to list and take unique ones.
    authors = []
    for a in alist:
        authors += a.authors
    uniq_authors = list(set(authors))

    # Which authors have contributed to which articles.
    result = map(lambda a: map(lambda author: author in a.authors, uniq_authors), alist)
    return (result, uniq_authors)

def append_from_file(l, fname, msg):
    """ Appends words from file fname to list l. Prints msg to stderr if
    file not found."""
    try:
        with copen(fname, 'r') as f:
            for line in f:
                w = line.strip()
                l.append(w)
    except IOError:
        sys.stderr.write("File %s not found. %s\n"%(fname, msg))
    return l

