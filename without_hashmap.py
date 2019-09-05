import os
import sys
import re
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup


class MakeInvertedIndex:
    corpus_path = sys.argv[1]   # argv[0] is the file itself
    stemmer = PorterStemmer()
    corpus_dir = os.path.join(os.getcwd(), corpus_path)
    words_stop_list = []    # containing usual repetitive words
    doc_id = 1
    term_id = 1
    term_index_list = []
    doc_id_pos_list = []
    sorted_term_id_list = []
    words_vocabulary_list = {}  # only unique words

    def __init__(self):
        self.words_stop_list = self.make_stop_list("stoplist.txt")

    @staticmethod
    def make_stop_list(stop_list_path):
        stop_list = []
        with open(stop_list_path) as stop_file:
            for word in stop_file:
                stop_list.append(word.strip())
        stop_file.close()
        return stop_list

    def file_parser(self, filename, pos):
        with open(os.path.join(self.corpus_dir, filename), encoding="utf-8", errors='ignore') as curr_doc:
            html_soup = BeautifulSoup(curr_doc, "html.parser")
        ignored_tags = html_soup.find_all(["script", "style"])
        for tags in ignored_tags:
            tags.decompose()    # remove from the tree
        file_content = ''
        if html_soup.find("head"):
            file_content = html_soup.find("head").text
        if html_soup.find("body"):
            file_content += html_soup.find("body").text
        if file_content:
            tokenized_words_list = word_tokenize(file_content)
            for word in tokenized_words_list:
                stem_word = self.stemmer.stem(word).lower()
                stem_word = re.sub('[^a-zA-Z]+', '', stem_word)
                if stem_word not in self.words_stop_list and len(stem_word) > 1:
                    if self.words_vocabulary_list.get(stem_word) is None:
                        self.words_vocabulary_list[stem_word] = self.term_id
                        self.term_index_list.append((self.term_id, self.doc_id))    # tuples: <termID, docID>
                        temp_list = list()
                        temp_list.append((self.doc_id, pos))
                        self.doc_id_pos_list.append(temp_list)
                        self.term_id += 1
                    elif self.words_vocabulary_list[stem_word]:
                        existing_term_id = self.words_vocabulary_list.get(stem_word)
                        self.doc_id_pos_list[existing_term_id - 1].append((self.doc_id, pos))   # append to that temp_list
                        self.term_index_list.append((existing_term_id, self.doc_id))
                    pos += 1

    @staticmethod
    def write_inverted_index_to_file(sorted_list, doc_id_pos, max_term_id):
        with open("term_index_sorting.txt", 'a', encoding='utf8', errors='ignore') as term_info_file:
            for i in range(1, max_term_id):
                curr_term_id = i
                term_freq_corpus = Counter(term_ids[0] for term_ids in sorted_list)[curr_term_id]
                term_doc_freq = len(Counter(doc_ids[0] for doc_ids in doc_id_pos[curr_term_id - 1]))
                term_info_file.write(str(curr_term_id) + "\t" + str(term_freq_corpus) + "\t" +
                                     str(term_doc_freq) + "\t" + str(doc_id_pos[curr_term_id - 1]) + "\n")
        term_info_file.close()

    def sort_by_term_id(self):
        self.sorted_term_id_list = sorted(self.term_index_list, key=lambda tup: tup[0])  # by termID

    def construct_index(self):
        index_pos = 1  # position of term in doc
        for filename in os.listdir(self.corpus_dir):
            if os.path.isfile(os.path.join(self.corpus_dir, filename)):
                self.file_parser(filename, index_pos)
                index_pos = 1
                self.doc_id += 1
        if self.term_index_list is not None:
            self.sort_by_term_id()
            self.write_inverted_index_to_file(self.sorted_term_id_list, self.doc_id_pos_list, self.term_id)   # write at the end combined


if __name__ == "__main__":
    make_inverted_index = MakeInvertedIndex()
    make_inverted_index.construct_index()
