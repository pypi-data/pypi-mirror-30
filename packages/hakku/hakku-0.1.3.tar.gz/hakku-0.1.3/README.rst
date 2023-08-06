Hakku
=====

Hakku is a Python package that does cluster analysis for scientific articles.
Original Hakku by Ilkka Pölönen, Tuomo Sipola and Paavo Nieminen.
Python conversion by Jarno Kiesiläinen.

Installation
------------

Dependencies

- Python 3
- pip for installation

For manual installation, Python library dependencies:

- Numpy
- Scipy
- nltk
- PyQt5
- ete3

Directions:

Optionally start by creating virtualenvironment or conda environment.
See https://virtualenv.pypa.io/ and https://conda.io/docs/user-guide/tasks/manage-environments.html.

**From git**

1. Clone this repo with ``git clone -b python git@yousource.it.jyu.fi:data-mining-papers/hakku-survey-generator.git``
2. Change folder ``cd hakku-survey-generator``
3. Install package with pip: ``pip install .``

**From pip**

``pip install hakku``

Getting article list
--------------------

Get article from one of the supported sources:

**Web of Knowledge**

1. Do a search
2. Select *Save to Other File Formats*
3. Set article range and select *Full Records and Cited References*
4. For file format select *Plain text*

**IEEE Xplore**

1. Do a search
2. Select *Export*, *Search Results*, format CSV and *Download*

**ScienceDirect**

1. Do a search
2. Select articles
3. Select *Export*, *Export citation to RIS*

Running
-------

Run clustering with ``python -m hakku articles1.txt [articles2.txt ...]`` and follow the instructions.
Clustering results are generated in csv-file ``result.csv``.
When opening results csv in Excel or equivalent use tab as separator and ``'`` as text delimiter.

Clustering visualization can be reshown with command ``python -m hakku.visualization result.csv``.

Clustering can also be run from python script by the ``run_files`` command.

About stopwords
---------------

Stop words are words that are excluded from the clustering.
Some common stopwords are automatically included by the application.
When running the clustering the application asks the user for any addittional stopwords.
Some obvious choises are the search words used to produce the article text file. 

viridis.npy
-----------

This package contains file viridis.npy:
The file contains colordata of Viridis colormap created by Stefan van der Walt and Nathaniel Smith for the matplotlib library.
Viridis is under CC0 "no rights reserved" license.

See http://bids.github.io/colormap/.

