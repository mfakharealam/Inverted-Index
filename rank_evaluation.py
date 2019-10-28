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
    with open(file, 'r') as okapi_bm_file:
        while True:
            line = okapi_bm_file.readline().split()
            if len(line) < 1:
                break
            if query_rank_dict.get(int(line[0])) is None:
                query_rank_dict[int(line[0])] = []
            query_rank_dict[int(line[0])].append(line[2])


def read_relevance_judge_q_rel():
    with open("relevance judgements.qrel", "r") as graded_file:
        while True:
            line = graded_file.readline().split()
            if len(line) < 1:
                break
            graded_docs_dict[(int(line[0]), line[2])] = int(line[3])    # tuple (query id, grade)
        graded_file.close()


def p_at(query, i):
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
        if j == i + 1:
            break
    print(R/i)


query_rank_dict = OrderedDict()  # key: query_id ; value: doc_name
# read_ranking_file('okapi_bm_25.txt')
query_list = read_queries()
graded_docs_dict = {}
read_relevance_judge_q_rel()
for q in query_list:
    print("Query ID: " + q[0])
    p_at(q, 5)
    p_at(q, 10)
    p_at(q, 20)
    p_at(q, 30)
read_ranking_file('dirichlet_smoothing_model.txt')
for q in query_list:
    print("Query ID: " + q[0])
    p_at(q, 5)
    p_at(q, 10)
    p_at(q, 20)
    p_at(q, 30)
