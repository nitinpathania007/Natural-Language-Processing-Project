import os
import string

import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

from data_utils.data_organizer import get_subfolders
from summerizer.annotations.annotation_set import AnnotationSet
from summerizer.annotations.document import Document
from summerizer.annotations.document_set import DocumentSet
from summerizer.utils.scorer import Scorer


class Summerizer:
    def __init__(self):
        self.model = None
        self.training_dir = ""
        self.training_docs = []
        self.test_dir = ""
        self.test_docs = []
        self.scorer = Scorer()
        self.__remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

    @staticmethod
    def _stem_tokens(tokens):
        stemmer = nltk.stem.porter.PorterStemmer()
        return [stemmer.stem(item) for item in tokens]

    @staticmethod
    def _normalize(text):
        remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
        return nltk.word_tokenize(text.lower().translate(remove_punctuation_map))

    @staticmethod
    def _remove_stop_words(word_list):
        """
        :param word_list:
        :return: list of words with English stop words removed
        """
        return [word for word in word_list if word not in stopwords.words('english')]

    @staticmethod
    def _is_stop_word(word):
        """
        Returns true if the supplied word is an English stop word
        :param word:
        :return: boolean
        """
        return word in stopwords.words('english')

    @staticmethod
    def basic_text_preprocess(doc_dir, doc_list):
        """
        Create document sets for training files
        :return: training doc set
        """
        all_doc_sets = {}
        for doc in doc_list:
            # contains one set of documents from DUC
            print(f"{doc_dir}{os.path.sep}{doc}")
            doc_set = DocumentSet(doc)
            doc_path = doc_dir + os.path.sep + doc
            input_docs = get_subfolders(doc_path)
            for in_doc in input_docs:
                if in_doc == 'keys':
                    # skip the keys for now...
                    continue
                processed_doc = Document(doc_path, in_doc, ["full_text", "sentences", "tokens"])
                doc_set.add(processed_doc)
            all_doc_sets[doc] = doc_set
        return all_doc_sets

    def train(self):
        raise NotImplementedError

    def predict(self):
        raise NotImplementedError

    def create_summary(self, src_docs):
        raise NotImplementedError

    def score(self, summaries):
        sep = os.path.sep
        data = []
        for test_doc_path, hypothesis in summaries.items():
            print(f"Scoring document {test_doc_path}")
            keys = AnnotationSet("answer_keys")
            key_file = f"{test_doc_path}{sep}keys{sep}annotations{sep}answer_keys"
            keys.read_annotation_file(key_file)
            hyp = ' '.join(hypothesis)
            hyp = hyp.replace("\n", " ")
            ref = keys.get(0).text.replace("\n", " ")
            data.append({"hyp": hyp, "ref": ref})

        hyps, refs = map(list, zip(*[[d['hyp'], d['ref']] for d in data]))
        scores = self.scorer.rouge_score(hyps, refs)
        return scores

    def _cosine_sim_check(self, potential, summaries):
        """
         If the potential is similar with any existing sentence, don't add it
        :param potential: sentence to maybe add to summary
        :param summaries: the existing summary
        :return: True if similar, False if not
        """
        for summary in summaries:
            if self._cosine_similarity(potential, summary) >= 0.5:
                return False
        return True

    def _cosine_similarity(self, text1, text2):
        """
        Compare Cosine Similarity vectors of two texts
        :param text1:
        :param text2:
        :return: Cosine Similarity
        """
        vectorizer = TfidfVectorizer(tokenizer=self._normalize, stop_words='english')
        tfidf = vectorizer.fit_transform([text1, text2])
        return (tfidf * tfidf.T).A[0, 1]

    def _normalize_with_stem(self, text):
        """
        :param text:
        :return: Sentence tokens that are lowercase, no punctuation and stemmed
        """
        return self._stem_tokens(
            nltk.word_tokenize(text.lower().translate(self.__remove_punctuation_map))
        )

    def _size_check(self, summaries):
        """
        DUC summaries have a maximum of 100 words
        :param summaries:
        :return: True if summaries have more than 100 words, False otherwise
        """
        text = ' '.join(summaries)
        total_tokens = nltk.word_tokenize(
            text.lower().translate(self.__remove_punctuation_map)
        )
        return len(total_tokens) > 100
