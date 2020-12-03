import os
from summerizer.annotations.annotation import Annotation
from summerizer.annotations.annotation_set import AnnotationSet


class AnswerKey:
    @staticmethod
    def create_answer_keys(parent_dir, key_files, out_dir):
        answer_key_set = AnnotationSet("answer_keys")
        for kf in key_files:
            with open(parent_dir + os.path.sep + kf, 'r') as in_file:
                key_text = ''.join(in_file.readlines())
            key_id = int(kf.replace(".txt", ""))
            answer_key_set.add(Annotation(key_id, key_text, "answer_key", 0, len(key_text)))
        try:
            answer_key_set.write_annotation_file(out_dir)
        except FileNotFoundError:
            if not os.path.exists(out_dir):
                os.mkdir(out_dir)
