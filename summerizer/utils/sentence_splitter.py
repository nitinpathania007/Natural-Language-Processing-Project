from nltk.tokenize import sent_tokenize

from summerizer.annotations.annotation import Annotation
from summerizer.annotations.annotation_set import AnnotationSet


class SentenceSplitter:
    def __init__(self):
        self.__annotation_name = "sentences"

    @staticmethod
    def split(in_text):
        return sent_tokenize(in_text)

    def sentence_split_document(self, out_dir, doc_text):
        sentence_set = AnnotationSet("sentences")
        sentences = self.split(doc_text)
        ann_id = 0
        for sentence in sentences:
            start = doc_text.find(sentence)
            end = start + len(sentence)
            sentence_set.add(Annotation(ann_id, sentence, "sentence", start, end))
        sentence_set.write_annotation_file(out_dir)
