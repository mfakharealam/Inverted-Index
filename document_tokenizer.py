import os
import sys
import nltk
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

    def file_parser(self, filename):
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
                    if stem_word not in self.words_stop_list:
                        if stem_word not in self.words_vocabulary_list:
                            self.words_list.append([stem_word, self.term_id])
                            self.words_vocabulary_list.add(stem_word)
                            term_file.write(str(self.term_id) + "\t" + stem_word + "\n")
                            self.term_id += 1
            term_file.close()

    def construct_index(self):
        for filename in os.listdir(self.corpus_dir):
            if os.path.isfile(os.path.join(self.corpus_dir, filename)):
                with open("docsid.txt", 'a') as doc_file:
                    doc_file.write(str(self.doc_id) + "\t" + filename + "\n")
                self.doc_id += 1
                self.file_parser(filename)


if __name__ == "__main__":
    tokenize_document = TokenizeDocument()
    tokenize_document.construct_index()
