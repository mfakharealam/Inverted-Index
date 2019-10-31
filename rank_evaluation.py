import os
import math
from collections import OrderedDict
import re
import linecache
from bs4 import BeautifulSoup


def read_queries():
    q_list = []
    with open('topics.xml', 'r') as file:
        html_soup = BeautifulSoup(file, "xml")
    topics = html_soup.find_all('topic')
    for topic in topics:
        q_list.append((topic.attrs['number'], re.sub('[^a-zA-Z]+', ' ', topic.query.text)))
    return q_list


def read_ranking_file(file):
    with open(file, 'r') as ranking_file:
        while True:
            line = ranking_file.readline().split()
            if len(line) < 1:
                break
            if query_rank_dict.get(int(line[0])) is None:
                query_rank_dict[int(line[0])] = []
            query_rank_dict[int(line[0])].append(line[2])
    ranking_file.close()


def read_relevance_judge_q_rel():
    with open("relevance judgements.qrel", "r") as graded_file:
        while True:
            line = graded_file.readline().split()
            if len(line) < 1:
                break
            graded_docs_dict[(int(line[0]), line[2])] = int(line[3])    # tuple (query id, doc name)
            if query_id_grades.get(int(line[0])) is None:
                query_id_grades[int(line[0])] = []
            query_id_grades.get(int(line[0])).append(int(line[3]))
        graded_file.close()


def find_total_relevant_docs_query(que):
    no_of_docs = 0
    query_id = int(que[0])
    try:
        for grade in query_id_grades[query_id]:
            if grade > 0:
                no_of_docs += 1
    except KeyError:
        no_of_docs = 0
    return no_of_docs


def p_at(query, at_val):
    j = 1
    R = 0.0
    q_id = int(query[0])
    doc_names_ranked = query_rank_dict[q_id]
    for d in doc_names_ranked:
        try:
            doc_grade = graded_docs_dict[(q_id, d)]
        except KeyError:
            doc_grade = 0   # irrelevant
        if doc_grade > 0:
            R += 1
        j += 1
        if j == at_val + 1:
            break
    return R/at_val


def avg_p(query):
    j = 1
    q_id = int(query[0])
    doc_names_ranked = query_rank_dict[q_id]    # get ranked list of docs for current query
    rel_docs = find_total_relevant_docs_query(query)
    the_p_at = 0
    for d in doc_names_ranked:
        try:
            doc_grade = graded_docs_dict[(q_id, d)]
        except KeyError:
            doc_grade = 0   # irrelevant
        if doc_grade > 0:   # by gold label
            the_p_at += p_at(query, j)
        j += 1
    return the_p_at/rel_docs


query_rank_dict = OrderedDict()  # key: query_id ; value: doc_name
read_ranking_file('okapi_bm_25.txt')
query_list = read_queries()
query_id_grades = OrderedDict()
graded_docs_dict = OrderedDict()
read_relevance_judge_q_rel()
print("Different Precisions using Okapi BM-25: ")
for q in query_list:
    print("Query ID: " + q[0])
    print(p_at(q, 5))
    print(p_at(q, 10))
    print(p_at(q, 20))
    print(p_at(q, 30))
query_rank_dict.clear()
read_ranking_file('dirichlet_smoothing_model.txt')
print("Different Precisions using Dirichlet Smoothing Model: ")
for q in query_list:
    print("Query ID: " + q[0])
    print(p_at(q, 5))
    print(p_at(q, 10))
    print(p_at(q, 20))
    print(p_at(q, 30))

query_rank_dict.clear()
read_ranking_file('okapi_bm_25.txt')
avg_precision = 0
for q in query_list:
    avg_precision += avg_p(q)

print("mAP using Okapi BM-25: ")
print(avg_precision/len(query_list))

query_rank_dict.clear()
read_ranking_file('dirichlet_smoothing_model.txt')
avg_precision = 0
for q in query_list:
    avg_precision += avg_p(q)

print("mAP using Dirichlet Smoothing Model: ")
print(avg_precision/len(query_list))
