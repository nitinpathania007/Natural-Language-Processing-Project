import os

from bs4 import BeautifulSoup

from summerizer.utils.answer_key import AnswerKey
from summerizer.utils.full_text import FullText
from summerizer.utils.sentence_splitter import SentenceSplitter
from summerizer.utils.tokenizer import Tokenizer


class Preprocessor:
    @staticmethod
    def get_sgml_document_text(doc, sub_doc):
        file_name = f"{doc}{os.path.sep}{sub_doc}{os.path.sep}{sub_doc}.sgml"
        with open(file_name, 'r') as in_file:
            soup = BeautifulSoup(in_file, 'html.parser')
            text = soup.find_all("text")
            return text.pop().text

    @staticmethod
    def get_sub_document_folders(folder):
        dir_items = os.listdir(folder)
        dir_items = list(filter(lambda x: os.path.isdir(folder + os.path.sep + x), dir_items))
        dir_items.remove("keys")
        dir_items = list(map(int, dir_items))
        dir_items.sort()
        return list(map(str, dir_items)) + ["keys"]

    @staticmethod
    def get_key_files(folder):
        dir_items = os.listdir(folder)
        dir_items = list(filter(lambda x: not os.path.isdir(folder + os.path.sep + x), dir_items))
        dir_items = list(filter(lambda x: 'orig_key_name' not in x, dir_items))
        return dir_items

    def __init__(self, doc_list):
        self.__document_list = []
        self.__get_document_list(doc_list)

    def run(self):
        tok = Tokenizer()
        sent = SentenceSplitter()
        for doc in self.__document_list:
            print(f"Processing document {doc}")
            for sub_doc in self.get_sub_document_folders(doc):
                print(f"\tProcessing sub-document {sub_doc}")
                out_dir = doc + os.path.sep + sub_doc + os.path.sep + "annotations"
                if sub_doc == 'keys':
                    key_dir = doc + os.path.sep + sub_doc
                    key_files = self.get_key_files(key_dir)
                    AnswerKey.create_answer_keys(key_dir, key_files, out_dir)
                    continue
                doc_text = self.get_sgml_document_text(doc, sub_doc)
                if not os.path.exists(out_dir):
                    os.mkdir(out_dir)
                FullText.extract_full_text(out_dir, doc_text)
                tok.tokenize_document(out_dir, doc_text)
                sent.sentence_split_document(out_dir, doc_text)

    def __get_document_list(self, doc_list):
        with open(doc_list, 'r') as doc_list_file:
            self.__document_list = list(map(lambda x: x.strip(), doc_list_file.readlines()))


if __name__ == "__main__":
    pre = Preprocessor("/Users/nitin/Documents/Data/summarization/duc2003/duc2003.filelist")
    pre.run()
