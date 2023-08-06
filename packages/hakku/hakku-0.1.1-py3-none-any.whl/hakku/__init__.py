"""
Hakku - tool for article clustering based on word counts in titles
and keywords. 

Clustering can be run from inside a script by run_files function or
from command line with python -m hakku articles1.txt articles2.txt
"""

import sys
from codecs import open as copen
import numpy as np

from nltk.stem.snowball import EnglishStemmer

from .article import get_articles, Source
from .word_occurrance import append_from_file, create_article_word_matrix,\
        create_article_author_matrix, ask_for_source, ask_for_stopwords
from .analysis import analysis, create_csv
from .visualization import visualize

def run_files(fnames, outfile="result.csv", low_bound=10, up_bound=20):
    """
    fnames      --  Array filenames for files containing the article data
    outfile     --  Filename for clustering output
    low_bound   --  criteria to stop clustering iteration of certain cluster
    up_bound    --  criteria to stop clustering

    Do cluster analysis for articles contained in files listed in 
    fnames array.

    Result of the clustering is stored in csv file.

    Addittionally user can also select to visualize the clustering hierarchy.
    """

    if not fnames:
        print_help()
        return

    articles = []
    for fname in fnames:
        with copen(fname, 'r', encoding='utf-8') as f:
            articles += get_articles(f, ask_for_source(fname))

    # some default stopwords
    extended_stopwords = ["elsevier", "copyright"]
    extended_stopwords += ["based", "paper"]
    stemmed_extended_stopwords = ["studi", "use", "analysi", "method", "differ",
            "result", "model", "also", "signific", "among", "within"]

    EXTENDED_STOPW_FILENAME = 'stopwords_whole.txt'
    EXTENDED_STOPSW_FILENAME = 'stopwords_stem.txt'
    #extended_stopwords = append_from_file(EXTENDED_STOPWORDS,
                                          #EXTENDED_STOPW_FILENAME,
                                          #'Only default stopwords used!')
    #stemmed_extended_stopwords = append_from_file(STEMMED_EXTENDED_STOPWORDS,
                                                  #EXTENDED_STOPSW_FILENAME,
                                                  #'Stemmed stopwords not used!')

    words = []

    try:
        f = open("last_stopwords.txt", "r")
        lines = f.readlines()
        lines = [l[:-1] for l in lines]
        print("Previous stopwords:")
        print(" ".join(lines))
        ans = input("Use previous stopwords [y/N]: ")[0]
        if ans == "y" or ans == "Y":
            words += lines

        f.close()
    except OSError:
        pass
    except IOError:
        pass

    # TODO ask for stemmed words also
    glob_st = EnglishStemmer()
    words += ask_for_stopwords()
    words_stemmed = map(glob_st.stem, words)
    extended_stopwords += words
    stemmed_extended_stopwords += words_stemmed

    print("Used stopwords: " + ", ".join(words))

    try:
        f = open("last_stopwords.txt", "w")
        f.writelines([l + "\n" for l in words])
    except OSError:
        pass

    print("Starting clustering...")

    ### Create word occurrence matrix.
    (m, ai, words) = create_article_word_matrix(articles,
            extended_stopwords ,stemmed_extended_stopwords)

    ### Create author occurrence matrix.
    (m_authors, uniq_authors) = create_article_author_matrix(articles)

    # Create dictionary structure and save for further analysis in a file.
    data = {}
    data['m'] = np.array(m)
    data['ai'] = np.array(ai)
    data['year'] = np.array([a.year for a in articles])
    data['cite_count'] = np.array([a.cite_count for a in articles])
    data['words'] = np.array(words)
    data['m_authors'] = np.array(m_authors)
    data['uniq_authors'] = np.array(uniq_authors)
    data['articles'] = np.array(articles)

    # Print the whole wordlist to output file:
    wfreq = np.sum(m, 0).astype(int).tolist()
    pairs = zip(wfreq, words)
    kfunc = lambda x: x[0]
    pairs = reversed(sorted(pairs, key=kfunc))
    with open('words_frequency.out','w') as f:
        for (fr, w) in pairs:
            f.write('%-7d %s\n'%(fr, w))

    # perform clustering
    c, names, inds = analysis(data['m'], data['words'], data['ai'], up_bound, low_bound)

    # save results to csv
    create_csv(c, names, data['cite_count'][inds],
            data['articles'][inds], data['year'][inds], outfile)

    # create tree visualization
    ans = input("Visualize: [y/N]: ")
    ans = ans[0]

    if ans == "y" or ans == "Y":
        visualize(outfile)

def print_help():
    helptext = """usage: python -m hakku articles1.txt [articles2.txt ...]"""

    print(helptext)

