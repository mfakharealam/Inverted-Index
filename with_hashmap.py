import os
import sys
import re
from collections import defaultdict, Counter
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup


class MakeInvertedIndex:
    corpus_path = sys.argv[1]   # argv[0] is the file itself
    stemmer = PorterStemmer()
    corpus_dir = os.path.join(os.getcwd(), corpus_path)
    words_stop_list = []    # containing usual repetitive words
    words_list = []
    doc_id = 1
    term_id = 1
    term_dictionary = defaultdict(list)
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
        with open(os.path.join(self.corpus_dir, filename), encoding="utf-8", errors='ignore') as file:
            html_soup = BeautifulSoup(file, "html.parser")
        ignored_tags = html_soup.find_all(["script", "style"])
        for tags in ignored_tags:
            tags.decompose()    # remove from the tree
        file_content = ''
        if html_soup.find("head"):
            file_content = html_soup.find("head").text
        if html_soup.find("body"):
            file_content += html_soup.find("body").text
        if file_content:
            file_content = re.sub('[^a-zA-Z]+', ' ', file_content)
            tokenized_words_list = word_tokenize(file_content)
            with open("termids.txt", 'a', encoding="utf-8", errors='ignore') as term_file:
                for word in tokenized_words_list:
                    stem_word = self.stemmer.stem(word).lower()
                    if stem_word not in self.words_stop_list and len(stem_word) > 1:
                        if self.words_vocabulary_list.get(stem_word) is None:
                            self.term_dictionary[self.term_id] = []     # maintaining inverted index
                            self.term_dictionary[self.term_id].append((self.doc_id, pos))
                            self.words_list.append([stem_word, self.term_id])
                            self.words_vocabulary_list[stem_word] = self.term_id
                            term_file.write(str(self.term_id) + "\t" + stem_word + "\n")
                            self.term_id += 1
                        elif self.words_vocabulary_list[stem_word]:
                            already_existing_term_id = self.words_vocabulary_list.get(stem_word)
                            self.term_dictionary[already_existing_term_id].append((self.doc_id, pos))
                        pos += 1
            term_file.close()

    @staticmethod
    def write_inverted_index_to_file(term_dict):
        with open("term_index.txt", 'a', encoding='utf8', errors='ignore') as term_info_file:
            for key in term_dict:
                # term ID and total occurrences
                term_info_file.write(str(key) + "\t" + str(len(term_dict[key])))  # key is termID
                # occurrences in different documents
                term_info_file.write("\t" + str(len(Counter(doc_ids[0] for doc_ids in term_dict[key]))))
                # doc_ids and positions in each doc
                for i, doc_id_pos in enumerate(term_dict[key]):
                    if i == 0:
                        term_info_file.write("\t" + str(doc_id_pos[0]) + ", " + str(doc_id_pos[1]))
                    else:
                        encoded_doc_id = doc_id_pos[0] - term_dict[key][i-1][0]
                        encoded_pos = doc_id_pos[1]
                        if encoded_doc_id == 0:  # if same doc ids, then encode positional indices
                            encoded_pos -= term_dict[key][i-1][1]
                        term_info_file.write("\t" + str(encoded_doc_id) + ", " + str(encoded_pos))
                term_info_file.write("\n")
        term_info_file.close()

    def construct_index(self):
        index_pos = 1  # position of term in doc
        for filename in os.listdir(self.corpus_dir):
            if os.path.isfile(os.path.join(self.corpus_dir, filename)):
                with open("docids.txt", 'a') as doc_file:
                    doc_file.write(str(self.doc_id) + "\t" + filename + "\n")
                self.file_parser(filename, index_pos)
                index_pos = 1
                self.doc_id += 1
        self.write_inverted_index_to_file(self.term_dictionary)   # write at the end combined


if __name__ == "__main__":
    make_inverted_index = MakeInvertedIndex()
    make_inverted_index.construct_index()
