"""
TODO
"""

import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.sparse.linalg import svds
from scipy.stats import mode

THIS_YEAR = 2014

def analysis(m, words, ai, up_bound, low_bound):
    """
    m           --  articles x words matrix
    words       --  list of words correspoding to m's columns
    ai          --  article/journal list
    up_bound    --  critetria to stop clustering
    low_bound   --  criteria to clustering iteration of certain cluster

    returns     --  (cluster ids, cluster names) for articles

    Example:
    analysis(m, words, articles, ai, cite_count, year, 25, 10)

    Stops when largest cluster residual is 25 and don't cluster
    again cluster which size is less than 10.

    """

    print(m.shape)

    # select only feature words that occur more than once
    good_features = np.sum(m, axis=0) > 1
    # TODO filter short words
    flen = lambda x: len(x) < 3
    short_inds = np.array(list(map(flen, words)))
    good_features[short_inds] = False
    m = m[:, good_features]
    words = np.array([str(w).strip() for w in words])
    words = words[good_features]

    # dismiss articles that have no words included in clustering
    good_articles = np.sum(m, axis=1) > 0
    m = m[good_articles, :]
    ai = ai[good_articles]

    print(m.shape)

    raja = m.shape[0]

    # clustering roind index, 1 == initial unclustered
    kk = 1

    c = np.ones(shape=(raja, 1))

    # next clustering rounds article words matrix
    m_clust = m
    # corresponding word list
    words_cl = [words]

    # indix matrix for cluster names
    # words_cl[n][inds[m,n+1]] = cluster n's name for article m
    inds = np.zeros(shape=(m.shape[0], 6), dtype=np.int32)

    # boundary for the largest "redundant" cluster
    while raja > up_bound:
        print("Clustering level: " + str(kk))

        kk += 1
        if kk == 6:
            break

        # for cluster id numbering
        max_c_plus = 0

        # add new column to cluster ids
        if kk >= c.shape[1]:
            c_new = np.ones(shape=(c.shape[0], kk))
            c_new[:, 0:c.shape[1]] = c
            c = c_new
        c[:, kk-1] = 0
        
        # find unique clusters
        c_uni = np.unique(c[:, kk-2])

        # do clustering to each of last rounds clusters
        for ik in range(0, len(c_uni)):
            # indices for current cluster
            idx = c_uni[ik] == c[:, kk-2]

            # cc = cluster ids for articles
            # ii = cluster names for articles
            cc, ii = cluster_articles(m_clust[idx, :], low_bound)
            c[idx, kk-1] = cc
            inds[idx, kk-1] = ii

            # maintain sequential numbering of all the found clusters
            # if clustering results in ids 1,2,3
            # => add 3 to all coming cluster ids
            c[idx, kk-1] += max_c_plus
            max_c_plus = np.max(np.unique(c[:, kk-1]), axis=0)

        # if there are features, which are not used we should remove those
        if np.min(np.unique(inds[:, kk-1])) < 0:
            kkix = inds[:, kk-1] == 0
            inds[kkix, kk-1] = inds[kkix, kk-2]

        # remove cluster names (most common words)
        # from clustering in next level
        to_remove = np.unique(inds[:,kk-1])
        to_remove_i = np.ones((m_clust.shape[1],), dtype=bool)
        to_remove_i[to_remove] = False
        words_cl.append(words_cl[kk-2][to_remove_i])
        m_clust = m_clust[:,to_remove_i]

        # largest redundant cluster (??)
        raja = mode(c[:, kk-1])[1][0]

    # return cluster ids and cluster names
    return c, np.array([w[inds[:,i+1]] for i,w in enumerate(words_cl[:-1])]), good_articles

def create_csv(c, names, cite_count, articles, year, fname):
    """
    Creates a csv file of the clustering results

    c           --  clusters from analysis()
    names       --  cluster names from analysis()
    cite_count  --  Number of citations per article
    year        --  Articles years
    fname       --  Output file name
    """

    # delimiter to use in csv
    # note: ',' is bad since abstracts contain commas.
    delimiter = "\t"

    # create header row
    header = []
    header.append('\'Cluster ID\'')
    header.append('\'Cl. name\'')
    header.append('\'Cl. name\'')
    header.append('\'Cl. name\'')
    header.append('\'Cl. name\'')
    header.append('\'Cl. mean citation\'')
    header.append('\'Cl. mean weighted citation\'')
    header.append('\'Cl. median weighted citation\'')
    header.append('\'Article total citations\'')
    header.append('\'Article title\'')
    header.append('\'Journal title\'')
    header.append('\'Volume\'')
    header.append('\'DOI\'')
    header.append('\'ISSN\'')
    header.append('\'Page begin\'')
    header.append('\'Page end\'')
    header.append('\'Journal/Series/etc.\'')
    header.append('\'Abstract\'')

    # cluster mean citation
    c_cite = np.zeros(shape=(c.shape[0],))
    # citation mean, weighted with publising year
    c_citeW = np.zeros(shape=(c.shape[0],))
    # median citations, weighted with publising year
    c_citemW = np.zeros(shape=(c.shape[0],))

    # old versions of numpy didn't have axis in unique
    if np.__version__ < '1.13':
        c_uni = np.vstack({tuple(row) for row in c})
    else:
        c_uni = np.unique(c, axis=0)

    # calculate means and median
    for i in range(c_uni.shape[0]):
        inds = [np.all(c[j] == c_uni[i]) for j in range(c.shape[0])]
        m = np.mean(cite_count[inds])
        if np.all(THIS_YEAR - year[inds] > 0):
            w = np.mean(cite_count[inds] / (THIS_YEAR - year[inds]))
            mw = np.median(cite_count[inds] / (THIS_YEAR - year[inds]))
        else:
            w = np.mean(cite_count[inds])
            mw = np.median(cite_count[inds])
        c_cite[inds] = m
        c_citeW[inds] = w
        c_citemW[inds] = mw

    # generate csv rows
    rows = []

    for i in range(c.shape[0]):
        row = []
        # cluster ids eg. 1 2 3 4 5
        row.append(" ".join(c[i].astype(int).astype(str)))
        # cluster name stems eg. classroom cleaner click clinician
        # currently broken
        for j in range(len(names)):
            row.append(names[j][i])

        # append citation statistics
        row.append("'" + str(c_cite[i]) + "'")
        row.append("'" + str(c_citeW[i]) + "'")
        row.append("'" + str(c_citemW[i]) + "'")

        # article citations
        row.append(str(cite_count[i]))

        # add article info
        # replace 's with "s, for excel
        row.append("'" + str(articles[i].title).replace("'", "\"") + "'")
        row.append(str(articles[i].source).replace("'", "\""))
        row.append(str(articles[i].volume))
        row.append(str(articles[i].doi))
        row.append(str(articles[i].issn))
        row.append(str(articles[i].page_begin))
        row.append(str(articles[i].page_end))
        row.append(str(articles[i].source_type))
        row.append("'" + str(articles[i].abstract) + "'\n")

        # join to a single string
        rows.append(delimiter.join(row))

    # write to file
    fil = open(fname, "w")
    fil.write(delimiter.join(header) + "\n")
    fil.writelines(rows)

def diffusion_map(x, epsilon, kernel='euclidean', a=0, p=2, t=1):
    """
    Creates a dimension-reduced version of input matrix x.
    Compares all the time points to each other and maps
    using only the eigenvalues and eigenvectors.
    Needs pdist (in Octave statistics package or Matlab statistics toolbox).
    2010 Tuomo Sipola (tuomo.sipola@jyu.fi)
      [V,l,K,S] = diffusion_map(x, epsilon, kernel, a, p, t)
    Parameters:
      x       Input data which should be in format time x parameters.
      epsilon Epsilon value for the kernel.
      kernel  Can be 'euclidean' (default) or 'hamming'. Optional.
      a       The alpha value for diffusion families, 0, 0.5 or 1. Optional.
      p       To which power the distance is put.
      t       How many time steps to use, default 1. Optional.
    Returns:
      V       Eigenvectors in format values x vectors.
      l       Eigenvalues in descending order.
      K       Weight matrix of the graph.
      S       The symmetric graph Laplacian, S^t is good for clustering.

    kernel_params=''
    if kernel == 'weighted_hamming':
        kernel = wh_pdist
        kernel_params = number_of_categories(x)

    if kernel == 'bd'quareform
        disp('Using binary similarity')
        kernel = bs_pdist
        kernel_params = np.max(np.sum(x, axis=1))
        """

    # Create the kernel.
    K = squareform(pdist(x, kernel))
    K = np.exp(- K ** p / epsilon)
    # Create different families of diffusions.
    if a > 0:
        Q = np.diag(np.sum(K, axis=0))
        W = np.dot(np.dot(Q ** - a, K), Q ** - a)
    else:
        W = np.copy(K)

    # Calculate the integral of weights.
    d = np.sum(W, axis=0)
    # Create a Markov probability matrix and symmetrize it.
#D2 = D^-0.5;
    D2 = np.diag(1.0 / np.sqrt(d))
    S = np.dot(np.dot(D2, W), D2)
    # Calculate the 32 first eigenvalues and eigenvectors. (svds(S, 32))
    U, l, _ = svds(S, min(32, min(S.shape)-1))
    #l = np.diag(l ** t)
    l = l**t
    # Take right eigenvectors and normalize with the constant first eigenvector.
    #V = np.dot(D2,U)
    V = np.matmul(D2, U)
    V = V / V[0, 0]

    return V, l

def map_coordinates(V, l, N):
    Psi = np.matmul(V, np.diag(l))
    return Psi[:, N]

def silhouette(X, c):
    """Implementation
    of matlabs silhouette function

    The silhouette value for each point is a measure of
    how similar that point is to points in its own cluster,
    when compared to points in other clusters. The
    silhouette value for the ith point, Si, is defined as
    Si = (bi-ai)/ max(ai, bi)
    where ai is the average distance from the ith point to
    the other points in the same cluster as i, and bi is the
    minimum average distance from the ith point to points
    in a different cluster, minimized over clusters.
    """
    D = squareform(pdist(X))
    N = X.shape[0]

    k = len(np.unique(c))
    inds = [i+1 == c for i in range(k)]

    a = np.zeros(N)
    b = np.zeros(N)
    for i in range(N):
        # same cluster inds
        kk = inds[c[i]-1].copy()
        # dont count the studied point to mean
        kk[i] = False

        # mean distance to same cluster
        a[i] = np.mean(D[i][kk])

        # minimum mean distance to other clusters
        b[i] = np.min([np.mean(D[i][inds[j]]) for j in range(k) if j != i])

    return (b-a) / np.maximum(a, b)

def cluster_articles(m, low_b):
    """
    Cluster data points
    m       --  articles x words matrix
    low_b   --  don't do clustering for less than low_b articles
    """

    if m.shape[0] <= low_b:
        c = np.ones(shape=(m.shape[0], 1))
        inds = np.zeros(shape=(c.shape), dtype=np.int32)
        inds[:] = -1

    else:
        # reduce dimensionality
        ep = np.median(pdist(m, metric='jaccard'))
        V, l = diffusion_map(m, ep, 'jaccard', 0, 1, 1)
        y = map_coordinates(V, l, np.arange(1, 4))

        # Create a linkage tree
        tree = linkage(y, method='ward', metric='euclidean')

        # find best clustering
        N_OF_CLUSTERS = 15
        silhs = np.zeros(shape=(N_OF_CLUSTERS,))
        silhs[0] = np.nan
        for i in np.arange(2, 16):
            c = fcluster(tree, i, 'maxclust')
            s = silhouette(y, c)
            silhs[i-1] = np.mean(s)

        # best cluster = best silhouette value = datapoints most similiar to each other
        best_clustering = np.nanargmax(silhs)

        # Repeat clustering for best silhouette
        c = fcluster(tree, best_clustering+1, 'maxclust')

        # index array for cluster names
        inds = np.zeros(shape=(c.shape[0], ), dtype=np.int32)
        inds[:] = -1

        # iterate all clusters found
        for is_ in np.unique(c):
            # find how many times each feature occurs
            # within this cluster
            c_inds = c == is_
            n_words = np.sum(m[c_inds, :], axis=0)
            if np.sum(n_words) == 0:
                print("Cluster " + str(is_) + " has no keywords.")
                continue

            # get the most common keyword
            # and use it as cluster name
            w_inds = np.argsort(n_words)
            w_inds = np.flip(w_inds, axis=0)

            inds[c_inds] = w_inds[0]

    return c, inds
