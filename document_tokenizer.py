import os
import sys
import re
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from bs4 import BeautifulSoup


class TokenizeDocument:
    corpus_path = sys.argv[1]   # argv[0] is the file itself
    stemmer = PorterStemmer()
    corpus_dir = os.path.join(os.getcwd(), corpus_path)
    words_stop_list = []    # containing usual repetitive words
    words_list = []
    doc_id = 1
    term_id = 1
    words_vocabulary_list = set()  # all the unique words

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
        term_dictionary = {}
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
            tokenized_words_list = word_tokenize(file_content)
            with open("termsid.txt", 'a', encoding="utf-8", errors='ignore') as term_file:
                for word in tokenized_words_list:
                    stem_word = self.stemmer.stem(word).lower()
                    stem_word = re.sub('[^a-zA-Z]+', '', stem_word)
                    if stem_word not in self.words_stop_list:
                        if stem_word not in self.words_vocabulary_list:
                            term_dictionary[stem_word] = []
                            term_dictionary[stem_word].append(pos)
                            self.words_list.append([stem_word, self.term_id])
                            self.words_vocabulary_list.add(stem_word)
                            term_file.write(str(self.term_id) + "\t" + stem_word + "\n")
                            self.term_id += 1
                        elif stem_word in self.words_vocabulary_list:
                            if stem_word not in term_dictionary:
                                term_dictionary[stem_word] = []
                            term_dictionary[stem_word].append(pos)
                        pos += 1
            term_file.close()
            return term_dictionary

    def write_doc_info(self, doc_id, term_dict):
        with open("term_info.txt", 'a', encoding='utf8', errors='ignore') as term_info_file:
            for word in self.words_list:
                if term_dict.get(word[0]):
                    term_info_file.write(str(doc_id) + "\t" + str(word[1]))
                    for pos in term_dict.get(word[0]):
                        term_info_file.write("\t" + str(pos))
                    term_info_file.write("\n")
        term_info_file.close()

    def construct_index(self):
        index_pos = 1  # position of term in doc
        for filename in os.listdir(self.corpus_dir):
            if os.path.isfile(os.path.join(self.corpus_dir, filename)):
                with open("docsid.txt", 'a') as doc_file:
                    doc_file.write(str(self.doc_id) + "\t" + filename + "\n")
                term_dictionary = self.file_parser(filename, index_pos)
                if term_dictionary is not None:
                    self.write_doc_info(self.doc_id, term_dictionary)
                    term_dictionary.clear()
                self.doc_id += 1


if __name__ == "__main__":
    tokenize_document = TokenizeDocument()
    tokenize_document.construct_index()
