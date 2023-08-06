#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, csv
import codecs
import re
from enum import Enum
import csv

class Source(Enum):
    WebOfKnowledge = 1
    IEEE = 2
    ScienceDirect = 3

class Article:
    """Article. Reads from string to an object."""

    def __init__(self, source=u"", title=u"", doi=u""):
        """Creates an article."""
        self.title = title
        self.authors = []
        self.abstract = u""
        self.cite_count = 0
        self.doi = doi
        self.source = source
        self.source_type = u""
        self.volume = u""
        self.issue = u""
        self.page_begin = u""
        self.page_end = u""
        # self.year = 0 <-- Missing. What is a safe default? 
        self.year = 1970 # is this sensible?
        self.issn = u""

class PeekingLineReader:
    """Reads a file line-by-line, peeking into the next line. Assume that
       the file is opened as unicode using codecs.open. TODO: Handling
       of end-of-file is not implemented!
    """
    def __init__(self, ifile):
        self.fh = ifile
        self.buffer_line()

    def buffer_line(self):
        self.next_line = self.fh.readline()

    def peek2(self):
        """Peek ahead to check the next two characters."""
        return self.next_line[0:2]

    def readline(self):
        tmp = self.next_line
        self.buffer_line()
        return tmp;

    def skip_empty_rows(self):
        """Skips whitespace lines. Next readline() will return non-white."""
        while self.next_line.strip() == '':
            self.buffer_line()

def parse_string(fh):
    """Parse string field."""
    result = u''
    line = fh.readline().encode('utf-8')
    line = line[3:].rstrip()
    result = line.decode("utf-8")
    while fh.peek2() == '  ':
        result = result + ' '
        line = fh.readline().encode('utf-8')
        line = line[3:].rstrip()
        result = result + line.decode("utf-8")
    return result

def parse_string_list(fh):
    """Parse list of strings."""
    result = []
    line = fh.readline().encode('utf-8')
    line = line[3:].rstrip()
    result.append(line)
    while fh.peek2() == '  ':
        line = fh.readline().encode('utf-8')
        line = line[3:].rstrip()
        result.append(line)
    return result

def parse_int(fh):
    """Parse int field."""
    line = fh.readline().encode('utf-8')
    line = line[3:].rstrip()
    return int(line)


def parse_article_wok(fh):
    """Parses one article from Web of Knowldedge database. 
    Continues until ER code occurs. 
    http://images.webofknowledge.com/WOKRS57B4/help/WOK/hs_alldb_fieldtags.html
    Input: fh - PeekingLineReader instance."""

    article = Article()

    while True:
        code = fh.peek2()
        if code == u'ER':
            fh.readline()
            break
        elif code == u'TI':
            article.title = parse_string(fh)
        elif code == u'AU':
            article.authors = parse_string_list(fh)
        elif code == u'CA':
            article.authors.append(parse_string(fh))
        elif code == u'AB':
            article.abstract = parse_string(fh)
        elif code == u'Z9':
            article.cite_count = parse_int(fh)
        elif code == u'DI':
            article.doi = parse_string(fh)
        elif code == u'PT':
            article.source_type = parse_string(fh)
        elif code == u'SO':
            article.source = parse_string(fh)
        elif code == u'VL':
            article.volume = parse_string(fh)
        elif code == u'IS':
            article.issue = parse_string(fh)
        elif code == u'BP':
            article.page_begin = parse_string(fh)
        elif code == u'EP':
            article.page_end = parse_string(fh)
        elif code == u'PY':
            article.year = parse_int(fh)
        elif code == u'SN':
            article.issn = parse_string(fh)
        else:
            fh.readline()

    return article

def parse_articles_ieee(f):
    creader = csv.reader(f, delimiter=",")
    header = False
    articles = []
    for row in creader:
        if not header:
            header = True
            continue
        article = Article()
        article.title = row[0]
        article.authors = row[1]
        article.issue = row[3]
        article.year = int(row[5])
        article.volume = row[6]
        article.issue = row[7]
        article.page_begin = row[8]
        article.page_end = row[9]
        article.abstract = row[10]
        article.issn = row[11]
        article.doi = row[13]
        if row[21]:
            article.cite_count = int(row[21])
        
        articles.append(article)
    return articles

def parse_article_sd(f):
    article = Article()
    line = f.readline()[:-1]

    if not line:
        line = f.readline()[:-1]

    if not line:
        return None

    while line:
        letters = line[0:2]
        rest = line[6:].strip(" \t\n\r")
        if letters == "TY":
            article.source_type = rest[0]
        elif letters == "T1" or letters == "TI":
            article.title = rest
        elif letters == "JO":
            article.source = rest
        elif letters == "VL":
            article.volume = rest
        elif letters == "IS":
            article.issue = rest
        elif letters == "SP":
            article.page_begin = rest
        elif letters == "EP":
            article.page_end = rest
        elif letters == "PY":
            year_str = rest.split("/")[0]
            if len(year_str) == 4:
                article.year = int(rest[0:4])
        elif letters == "AU":
            article.authors.append(rest)
        elif letters == "SN":
            article.issn = rest
        elif letters == "DO":
            article.doi = rest
        elif letters == "AB":
            abstract = f.readline()
            article.abstract = abstract[:-1].strip(" \t\n\r")
        elif letters == "ER":
            break

        line = f.readline()[:-1]

    return article

def get_articles(f, source):
    """Gives a list of articles."""

    articles = []

    if source == Source.WebOfKnowledge:
        fh = PeekingLineReader(f)

        while True:
            articles.append(parse_article_wok(fh))
            fh.skip_empty_rows()
            if fh.peek2() == 'EF':
                break

    elif source == Source.IEEE:
        articles = parse_articles_ieee(f)

    elif source == Source.ScienceDirect:
        a = parse_article_sd(f)
        while a:
            articles.append(a)
            a = parse_article_sd(f)

    return articles

if __name__ == "__main__":
    articles = get_articles(sys.stdin)


