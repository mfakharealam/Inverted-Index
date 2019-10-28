import os
import math
import re
import linecache
from collections import defaultdict, Counter, OrderedDict
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup

CORPUS_DIR = os.path.join(os.getcwd(), 'corpus')
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


# read and preprocess (somewhat) queries; return list of queries from xml file
def read_queries():
    q_list = []
    with open('topics.xml', 'r') as file:
        html_soup = BeautifulSoup(file, "xml")
    topics = html_soup.find_all('topic')
    for topic in topics:
        q_list.append((topic.attrs['number'], re.sub('[^a-zA-Z]+', ' ', topic.query.text)))
    return q_list


# for docs length, makes a file with each doc len info.
def make_docs_len_info():
    doc_no = 1
    term_id = 1
    doc_term_dict = {}
    print("Making a file for each document's terms information...")
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
                                doc_term_dict[(doc_no, term_id)] = 1   # count is 1 now
                                docs_info[doc_no].append(term_id)
                                term_id += 1
                            elif words_vocab[stem_word]:
                                already_existing_term_id = words_vocab.get(stem_word)
                                if already_existing_term_id not in docs_info.get(doc_no):
                                    docs_info[doc_no].append(already_existing_term_id)
                                else:
                                    try:
                                        temp_count = doc_term_dict[(doc_no, already_existing_term_id)]
                                    except KeyError:
                                        temp_count = 0
                                    doc_term_dict[(doc_no, already_existing_term_id)] = temp_count + 1
                else:
                    docs_info[doc_no] = []
                    docs_info[doc_no].append(0)     # to avoid skipped lines in file, want to match doc no with line no in file
        # print("Progress: " + str(100 * (doc_no/3465)) + "%")
        doc_no += 1
    file.close()
    if docs_info is not None:
        with open("terms_info_in_each_doc.txt", 'a', encoding="utf-8", errors='ignore') as doc_info_file:
            for doc in docs_info:
                doc_info_file.write(str(doc) + "\t" + str(len(docs_info[doc])) + "\t")
                t_sum = 0
                for t_id in docs_info[doc]:
                    try:
                        temp_count = doc_term_dict[(doc, t_id)]
                    except KeyError:
                        temp_count = 1
                    doc_info_file.write(str(t_id) + ": " + str(temp_count) + ", ")
                    t_sum += temp_count
                doc_info_file.write("\n")


# returns dict of all corpus unique terms, with key as term and value being ID
def read_term_ids():
    t_ids = {}
    with open("termids.txt", "r") as term_id_file:
        line = term_id_file.readline().split()
        while len(line) > 1:
            t_ids[line[1]] = int(line[0])  # term_name: id
            line = term_id_file.readline().split()
    term_id_file.close()
    return t_ids


def get_doc_names():
    doc_names = {}
    with open("docids.txt", "r") as doc_file:
        while True:
            line = doc_file.readline().split()
            if len(line) < 1:
                break
            doc_names[int(line[0])] = line[1]
        return doc_names


# returns dict of query terms as key and with ids as value
def get_query_terms_ids(ind_terms_in_query, all_corpus_terms):
    term_ids = {}
    for term in ind_terms_in_query:
        if len(term) > 1:
            try:
                term_ids[term] = all_corpus_terms[term]
            except KeyError:
                term_ids[term] = -1     # in case query term is not in corpus
    return term_ids


def get_relevant_docs_query(query_terms_ids):
    term_docs_dict = {}     # key is term_id and value is its relevant docs list
    query_docs_list = []    # contains all of the docs of all terms in query
    for term_id in query_terms_ids.values():
        if term_id != -1:
            this_term_docs = get_all_docs_of_term(term_id)
            term_docs_dict[term_id] = this_term_docs
            query_docs_list.extend(this_term_docs)
    query_docs_list = list(dict.fromkeys(query_docs_list))      # removes duplicates
    return term_docs_dict, query_docs_list


def get_all_docs_of_term(term_id):
    doc_list = []
    i = 3
    sum_docs_id = 0     # to decode delta encoding
    the_line = linecache.getline("term_index.txt", int(term_id)).split()    # gets the term info
    limit = int(the_line[1]) * 2 + 3
    while i < limit:
        sum_docs_id += int(the_line[i].replace(",", ""))    # actual current doc id after decoding
        if sum_docs_id not in doc_list:     # to remove redundancy
            doc_list.append(sum_docs_id)
        i += 2
    return doc_list


def read_docs_len_info():
    docs_len_dict = {}
    len_sum = 0
    with open("terms_info_in_each_doc.txt", "r") as docs_len_file:
        while True:
            line = docs_len_file.readline().split()
            if len(line) < 1:
                break
            doc_len = int(line[1])
            docs_len_dict[int(line[0])] = doc_len
            len_sum += doc_len
    avg_len = len_sum/len(docs_len_dict)
    return avg_len, docs_len_dict


def get_doc_terms_info(doc_id):
    doc_terms = {}
    i = 2   # for term id
    j = 3   # for freq of term
    the_line = linecache.getline("terms_info_in_each_doc.txt", doc_id).split()
    try:
        d_id_in_file = int(the_line[0])
    except IndexError:
        return doc_terms
    try:
        limit = int(the_line[1]) * 2 + 2    # since there are tuples, plus 2 because of i
    except IndexError:
        limit = 0
    while j <= limit:
        doc_terms[int(the_line[i].replace(":", ""))] = int(the_line[j].replace(",", ""))
        i += 2
        j += 2
    return doc_terms


def okapi_bm25(the_query):
    query_id = the_query[0]
    rank_info_dict = {}
    query_itself = the_query[1]
    current_query_terms_list = word_tokenize(query_itself)
    current_query_terms_list = [stemmer.stem(term) for term in current_query_terms_list if term not in stopwords_list]
    query_terms_ids_dict = get_query_terms_ids(current_query_terms_list, term_ids_list)
    term_docs_dict, query_docs_list = get_relevant_docs_query(query_terms_ids_dict)
    query_docs_list = sorted(query_docs_list)
    total_docs_in_collection = len(doc_lens)    # D
    k1 = 1.2
    k2 = 500
    b = 0.75
    # query_docs_list = list(dict.fromkeys(query_docs_list))  # removes duplicates
    for doc in query_docs_list:     # list has doc ids
        total_score = 0.0
        try:
            curr_doc_len = doc_lens[doc]
        except KeyError:
            curr_doc_len = 0
        K = k1 * ((1 - b) + (b * (curr_doc_len/avg_doc_len)))
        doc_terms_info_dict = get_doc_terms_info(doc)
        for term in current_query_terms_list:
            tfq = current_query_terms_list.count(term)
            try:
                term_id_from_corpus = term_ids_list[term]
            except KeyError:
                term_id_from_corpus = -1
            try:
                tfd = doc_terms_info_dict[term_id_from_corpus]     # term occurrence in doc
            except KeyError:
                tfd = 0
            try:
                df = len(term_docs_dict[term_id_from_corpus])     # document freq of term
            except KeyError:
                df = 0
            term_idf = math.log10((total_docs_in_collection + 0.5)/(df + 0.5))  # first in formula
            second_val = ((1 + k1) * tfd)/(K + tfd)
            third_val = ((1 + k2) * tfq)/(k2 + tfq)
            score_of_query_i = term_idf * second_val * third_val
            total_score += score_of_query_i
        rank_info_dict[(query_id, doc)] = total_score
    sorted_rank_list = sorted(rank_info_dict.items(), key=lambda kv: kv[1], reverse=True)
    rank_info_dict = OrderedDict(sorted_rank_list)
    pos = 1
    with open('okapi_bm_25.txt', 'a') as okapi_bm_file:
        for q_id in rank_info_dict.items():
            okapi_bm_file.write(
                str(q_id[0][0]) + "\t" + "0" + "\t" + doc_names_list[q_id[0][1]] + "\t" + str(q_id[0][1]) + "\t" +
                str(pos) + "\t" + str(q_id[1]) + "\t" + "run1" + "\n")
            pos += 1
        okapi_bm_file.close()


def get_term_corpus_info(query_ids):
    term_info = {}
    for q_id in query_ids:
        the_line = linecache.getline("term_index.txt", q_id).split()  # gets the term info
        if q_id == int(the_line[0]):
            term_info[q_id] = int(the_line[1])
    return term_info


def dirichlet_smoothing(the_query):
    query_id = the_query[0]
    rank_info = {}
    query_itself = the_query[1]
    current_query_terms_list = word_tokenize(query_itself)
    current_query_terms_list = [stemmer.stem(term) for term in current_query_terms_list if term not in stopwords_list]
    query_terms_ids_dict = get_query_terms_ids(current_query_terms_list, term_ids_list)
    collection_occurrences = get_term_corpus_info(query_terms_ids_dict.values())    # only passing ids
    total_collection_words = sum(doc_lens.values())
    term_docs_dict, query_docs_list = get_relevant_docs_query(query_terms_ids_dict)
    query_docs_list = sorted(query_docs_list)
    for doc in query_docs_list:
        doc_terms_info_dict = get_doc_terms_info(doc)   # gets info (each term freq in this doc) regrading current doc
        try:
            curr_doc_len = doc_lens[doc]
        except KeyError:
            curr_doc_len = 0
        dirichlet_factor = curr_doc_len/(curr_doc_len + MU)     # lambda = N/(N + mu)
        total_query_probability = 1
        for term in current_query_terms_list:
            if len(term) > 1:
                try:
                    term_id_from_corpus = term_ids_list[term]
                except KeyError:
                    term_id_from_corpus = -1
                try:
                    tfd = doc_terms_info_dict[term_id_from_corpus]
                except KeyError:
                    tfd = 0
                try:
                    tfc = collection_occurrences[term_id_from_corpus]
                except KeyError:
                    tfc = 0
                probability_doc = tfd/curr_doc_len
                probability_corpus = tfc/total_collection_words
                curr_term_probability = dirichlet_factor * probability_doc + (1 - dirichlet_factor) * probability_corpus
                total_query_probability *= curr_term_probability
        rank_info[(query_id, doc)] = total_query_probability
    sorted_rank = sorted(rank_info.items(), key=lambda kv: kv[1], reverse=True)
    rank_info = OrderedDict(sorted_rank)
    pos = 1
    with open('dirichlet_smoothing_model.txt', 'a') as dirichlet_file:
        for q_id in rank_info.items():
            dirichlet_file.write(str(q_id[0][0]) + "\t" + "0" + "\t" + doc_names_list[q_id[0][1]] + "\t" + str(q_id[0][1]) + "\t" +
                                 str(pos) + "\t" + str(q_id[1]) + "\t" + "run1" + "\n")
            pos += 1
        dirichlet_file.close()


stopwords_list = make_stop_list("stoplist.txt")
make_docs_len_info()

query_list = read_queries()
avg_doc_len, doc_lens = read_docs_len_info()
MU = avg_doc_len
doc_names_list = get_doc_names()
term_ids_list = read_term_ids()

print("Ranking Queries...")
for query in query_list:
    okapi_bm25(query)
    dirichlet_smoothing(query)
