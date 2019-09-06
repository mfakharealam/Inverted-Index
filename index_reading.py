import sys
from nltk.stem import PorterStemmer
import re
import time
import linecache


def get_term_details(term):
    term_id = 0
    total_corpus_occurrences = 0
    occurrences_in_diff_docs = 0
    if term is not None:
        stemmer = PorterStemmer()
        stem_word = stemmer.stem(term).lower()
        stem_word = re.sub('[^a-zA-Z]+', '', stem_word)     # clear punctuation
        with open("termsid.txt", "r", encoding="utf-8") as terms_id_file, open("term_index.txt", "r", encoding="utf-8") as term_index_file:
            term_id_doc = terms_id_file.read().split()
            for i in range(1, len(term_id_doc)):
                if term_id_doc[i] == stem_word:
                    term_id = term_id_doc[i - 1]    # since it is matching the term, id is at index - 1
                    break
                i += 2  # since term name is at 2nd pos each time
            if term_id != 0:
                read_line_no = term_id
                the_line = linecache.getline("term_index.txt", int(read_line_no)).split()
                term_id = the_line[0]
                total_corpus_occurrences = the_line[1]
                occurrences_in_diff_docs = the_line[2]
                # while True:
                #     each_line = term_index_file.readline().split()
                #     if len(each_line) > 0:
                #         if term_id == each_line[0]:
                #             total_corpus_occurrences = each_line[1]
                #             occurrences_in_diff_docs = each_line[2]
                #             break
                #     else:
                #         break
                print("Listing for term:", term)
                print("Term ID:", term_id)
                print("Number of documents containing term:", occurrences_in_diff_docs)
                print("Term frequency in corpus:", total_corpus_occurrences)
            else:
                print("Term not found!")
        terms_id_file.close()
        term_index_file.close()


if __name__ == '__main__':
    start_time = time.perf_counter()
    if sys.argv[1] == '--term':
        get_term_details(sys.argv[2])

    print("Total execution time: {}".format(time.perf_counter() - start_time))
