import sys
from nltk.stem import PorterStemmer


def get_term_details(term):
    if term is not None:
        stem_word = PorterStemmer.stem(term)





if __name__ == '__main__':
    if sys.argv[1] == '--term':
        get_term_details(sys.argv[2])
