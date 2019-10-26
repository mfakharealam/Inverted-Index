import os
import sys
import re
from collections import defaultdict, Counter
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup

CORPUS_DIR = os.path.join(os.getcwd(), 'corpus')
query_list = []
stemmer = PorterStemmer()
words_vocab = {}
docs_info = {}


def make_stop_list(stop_list_path):
    stop_list = []
    with open(stop_list_path) as stop_file:
        for word in stop_file:
            stop_list.append(word.strip())
    stop_file.close()
    return stop_list


# read preprocess queries
def read_queries():
    with open('topics.xml', 'r') as file:
        html_soup = BeautifulSoup(file, "xml")
    topics = html_soup.find_all('topic')
    for topic in topics:
        query_list.append((topic.attrs['number'], re.sub('[^a-zA-Z]+', ' ', topic.query.text)))
    print(query_list)


# for docs length
def make_docs_len_info():
    doc_no = 1
    term_id = 1
    for filename in os.listdir(CORPUS_DIR):
        if os.path.isfile(os.path.join(CORPUS_DIR, filename)):
            with open(os.path.join(CORPUS_DIR, filename), encoding="utf-8", errors='ignore') as file:
                html_soup = BeautifulSoup(file, "html.parser")
                ignored_tags = html_soup.find_all(["script", "style"])
                for tags in ignored_tags:
                    tags.decompose()  # remove from the tree
                file_content = ''
                if html_soup.find("head"):
                    file_content = html_soup.find("head").text
                if html_soup.find("body"):
                    file_content += html_soup.find("body").text
                if file_content:
                    file_content = re.sub('[^a-zA-Z]+', ' ', file_content)
                    tokenized_words_list = word_tokenize(file_content)
                    docs_info[doc_no] = []
                    for word in tokenized_words_list:
                        stem_word = stemmer.stem(word).lower()
                        if stem_word not in stopwords_list and len(stem_word) > 1:
                            if words_vocab.get(stem_word) is None:
                                words_vocab[stem_word] = term_id
                                docs_info[doc_no].append(term_id)
                                term_id += 1
                            elif words_vocab[stem_word]:
                                already_existing_term_id = words_vocab.get(stem_word)
                                if already_existing_term_id not in docs_info.get(doc_no):
                                    docs_info[doc_no].append(already_existing_term_id)
        doc_no += 1
        print("Progress: " + str(100 * (doc_no/3465)) + "%")
    file.close()
    if docs_info is not None:
        d_id = 1
        with open("docs_len_info.txt", 'a', encoding="utf-8", errors='ignore') as doc_info_file:
            while d_id < doc_no:
                if docs_info[d_id] is not None:
                    doc_info_file.write(str(d_id) + "\t" + str(len(docs_info[d_id])) + "\t")
                    d_id += 1
                    # for t_id in docs_info[doc]:
                    #     doc_info_file.write(str(t_id) + ", ")
                    doc_info_file.write("\n")


def read_term_ids():
    t_ids = {}
    with open("termids.txt", "r") as term_id_file:
        line = term_id_file.readline().split()
        while len(line) > 1:
            t_ids[line[1]] = int(line[0])  # term_name: id
            line = term_id_file.readline().split()
    term_id_file.close()
    return t_ids


stopwords_list = make_stop_list("stoplist.txt")
# read_queries()
make_docs_len_info()
# read_term_ids()
