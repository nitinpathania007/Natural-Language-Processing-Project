from summerizer.annotations.annotation import Annotation
from summerizer.annotations.annotation_set import AnnotationSet


class FullText:
    @staticmethod
    def extract_full_text(out_dir, doc_text):
        full_text_set = AnnotationSet("full_text")
        full_text_set.add(Annotation(0, doc_text, "full_text", 0, len(doc_text)))
        full_text_set.write_annotation_file(out_dir)
