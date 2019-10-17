import os
import sys
import re
from collections import defaultdict, Counter
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup

query_list = []
stemmer = PorterStemmer()


def read_queries():
    with open('topics.xml', 'r') as file:
        html_soup = BeautifulSoup(file, "xml")
    topics = html_soup.find_all('topic')
    for topic in topics:
        query_list.append((topic.attrs['number'], topic.query.text))
    print(query_list)


read_queries()
