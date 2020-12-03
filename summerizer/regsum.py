import uuid
import operator
import os
import sys
from collections import defaultdict

import networkx as nx
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.utils import column_or_1d

sys.path.insert(0, '.')
sys.path.insert(0, '..')
from summerizer.summerizer import Summerizer
from summerizer.annotations.annotation_set import AnnotationSet
from data_utils.data_organizer import get_subfolders


class RegSum(Summerizer):
    def __init__(self):
        super().__init__()
        self.__summary = []
        self.training_feature_vectors = None
        self.top_1000_counts = None
        self.words2uuids = {}
        self.model = LogisticRegression()

    def train(self):
        """

        :return:
        """
        self.__generate_training_features()
        self.__get_labels()

        # create the Logistic Regression model
        self.training_feature_vectors = pd.DataFrame(self.training_feature_vectors)
        X = pd.DataFrame(self.training_feature_vectors.iloc[:, :-1])
        X = X.drop('uuid', axis=1)
        X = X.drop('word', axis=1)
        X = X.drop('word_key', axis=1)
        y = pd.DataFrame(self.training_feature_vectors.iloc[:, -1])
        y = column_or_1d(y, warn=True)
        self.model.fit(X, y)
        print("LogisticRegression model was trained.")

    def predict(self):
        """

        :return:
        """
        return self.__generate_testing_features()

    def create_summary(self, dss):
        """

        :param dss: document sentence scores
        :return:
        """
        doc_summaries = {}
        for doc in dss:
            print(f"Generating summary for document: {doc}")
            summary = {}
            sorted_by_score = sorted(doc_scores[doc].items(), key=operator.itemgetter(1), reverse=True)
            for text, score in sorted_by_score:
                if score < 1:
                    continue
                if self._cosine_sim_check(text, summary):
                    summary[text] = score
                if self._size_check(summary):
                    break
            if len(summary.items()) < 1:
                # grab the first 4 sentences
                summary = {k: v for (k, v) in sorted_by_score[:3]}
            doc_summaries[doc] = summary
        return doc_summaries

    def __generate_testing_features(self):
        self.testing_feature_vectors = []
        print("Testing on documents: ")
        # get all testing docs
        all_testing_doc_sets = self.basic_text_preprocess(self.test_dir, self.test_docs)
        doc_sentence_scores = defaultdict(dict)
        for doc_set in all_testing_doc_sets:
            # iterate over sentences
            for doc in all_testing_doc_sets[doc_set]:
                print(f"Scoring sentences for doc: {doc_set}/{doc.name}")
                test_doc_path = f"{self.test_dir}{os.path.sep}{doc_set}"
                sentences = doc.annotations["sentences"]
                feature_vectors = []
                sentence_scores = {}
                for sentence in sentences:
                    word_list = self._remove_stop_words(self._normalize(sentence.text))
                    for word in word_list:
                        feature_vector = {}
                        # get feature vector for word
                        self.top_word_features(feature_vector, word)
                        # add to feature vector list for sentence
                        feature_vectors.append(feature_vector)
                    # map word vectors to logreg prediction for sentence
                    X = pd.DataFrame(feature_vectors)
                    y = self.model.predict(X)
                    # sum words in a sentence
                    sentence_scores[sentence.text] = sum(y)
                doc_sentence_scores[test_doc_path].update(sentence_scores)
        return doc_sentence_scores

    def __generate_training_features(self):
        # map column name to index
        self.training_feature_vectors = []

        # iterate over sentences and build feature vectors
        print("Training on documents: ")
        all_training_doc_sets = self.basic_text_preprocess(self.training_dir, self.training_docs)

        global_counts = {}
        for doc_set in all_training_doc_sets.values():
            doc_set.create_word_probabilities()

            # create global word counts for top_k & LLR
            for word, count in doc_set.word_counts.items():
                # don't count stop words obvs
                if self._is_stop_word(word):
                    continue
                global_counts[word] = global_counts.get(word, 0) + count

            # get the top 1000 words in the training set
            self.top_1000_counts = sorted(global_counts.items(),
                                          key=operator.itemgetter(1),
                                          reverse=True)[:1000]

        self.__unsupervised_features(all_training_doc_sets, self.training_feature_vectors)
        # self.__word_location_features(all_training_doc_sets)
        # self.__word_type_features(all_training_doc_sets)
        # convert to Pandas Dataframe

    def __unsupervised_features(self, all_doc_sets, feature_vectors):
        if self.top_1000_counts is None:
            raise Exception("top 1000 counts is None")

        # FreqSum - take the top K (non stop word) words from training data
        for doc_set in all_doc_sets:
            # print(f"Document: {doc_set}...")
            # iterating over all documents in data
            for doc in all_doc_sets[doc_set]:
                sentences = doc.annotations["sentences"]
                textrank_sentences = self.__get_text_rank(sentences)[:3]
                s = 1
                # iterating over all sentences in data
                for sentence in sentences:
                    # print(f"\tSentence {s}/{len(sentences)}...")
                    word_list = self._remove_stop_words(self._normalize(sentence.text))
                    # iterating over words in sentences in documents of the data
                    word_id = 0
                    word_key = f"{doc_set}:{s}:{word_id}"
                    for word in word_list:
                        feature_vector = {}
                        row_uuid = uuid.uuid4()
                        # Where the mapping from a particular word in the data to uuid is set
                        self.words2uuids[word_key] = row_uuid
                        feature_vector["uuid"] = row_uuid
                        feature_vector["word"] = word
                        feature_vector["word_key"] = word_key
                        self.top_word_features(feature_vector, word)
                        word_id += 1

                        # TextRank
                        for _, trs in textrank_sentences:
                            if word in trs.text.lower():
                                feature_vector["textrank"] = True
                            else:
                                feature_vector["textrank"] = False
                        feature_vectors.append(feature_vector)

                    s += 1
                # FutureWork: LLR -  current document terms vs entire training corpus

    def top_word_features(self, feature_vector, word):
        for topK_word, _ in self.top_1000_counts:
            if topK_word == word:
                feature_vector[topK_word] = 1.0
            else:
                feature_vector[topK_word] = 0.0

    def __word_location_features(self, all_docs):
        # 6 types
        # earliest first location
        # latest last location
        # average location
        # average first location
        pass

    def __word_type_features(self, all_docs):
        # part of speech tags
        # named entity
        # unigrams from training documents
        pass

    def __get_labels(self):
        for doc in self.training_docs:
            doc_path = self.training_dir + os.path.sep + doc
            input_docs = get_subfolders(doc_path)
            for in_doc in input_docs:
                if in_doc != 'keys':
                    continue
                keys = AnnotationSet("answer_keys")
                key_file = f"{doc_path}{os.path.sep}keys{os.path.sep}annotations{os.path.sep}answer_keys"
                keys.read_annotation_file(key_file)
                key_text = keys.get(0).text.replace("\n", " ").lower()
                key_cleaned = self._remove_stop_words(key_text.split())

                for vec in self.training_feature_vectors:
                    if vec['word'] in key_cleaned:
                        vec['target'] = 1
                    else:
                        vec['target'] = 0

    # pylint: disable=too-many-locals
    def __get_text_rank(self, sentences):
        """
        Generate a ranked list of sentences from the document that are ranked
        by the PageRank algorithm.
        :return: ranked_sentences
        """
        # Extract word vectors
        word_embeddings = {}
        with open('/Users/nitin/Documents/Data/glove/glove.6B.100d.txt', encoding='utf-8') as in_file:
            for line in in_file:
                values = line.split()
                word = values[0]
                coefs = np.asarray(values[1:], dtype='float32')
                word_embeddings[word] = coefs

        clean_sentences = [self._remove_stop_words(s.text.split()) for s in sentences]
        sentence_vectors = []
        for i in clean_sentences:
            if len(i) != 0:
                s_v = sum(
                    [word_embeddings.get(w, np.zeros((100,))) for w in i]
                ) / (len(i) + 0.001)
            else:
                s_v = np.zeros((100,))
            sentence_vectors.append(s_v)

        # similarity matrix
        sim_mat = np.zeros([len(sentences), len(sentences)])
        for i in range(len(sentences)):
            for j in range(len(sentences)):
                if i != j:
                    sim_mat[i][j] = \
                        cosine_similarity(
                            sentence_vectors[i].reshape(1, 100), sentence_vectors[j].reshape(1, 100)
                        )[0, 0]

        nx_graph = nx.from_numpy_array(sim_mat)
        textrank_scores = nx.pagerank(nx_graph)
        ranked_sentences = sorted(((textrank_scores[i], s) for i, s in enumerate(sentences)), reverse=True)
        return ranked_sentences


if __name__ == "__main__":
    rs = RegSum()
    rs.training_dir = "/Users/nitin/Documents/Data/summarization/duc2003"
    rs.training_docs = ["0", "1", "10", "11", "12", "13", "14", "15", "16",
                             "17", "18", "19", "2", "20", "21", "22", "23", "24",
                             "25", "26", "27", "28", "29", "3", "30", "31", "32",
                             "33", "34", "35", "36", "37", "38", "39", "4", "40",
                             "41", "42", "43", "44", "45", "46", "47", "48", "49",
                             "5", "50", "51", "52", "53", "54", "55", "56", "57",
                             "58", "59", "6", "7", "8", "9"]
    rs.train()
    rs.test_dir = "/Users/nitin/Documents/Data/summarization/duc2004"
    rs.test_docs = ["0", "1"]
    #rs.test_docs = ["0", "1", "10", "11", "12", "13", "14", "15", "16", "17",
    #                "18", "19", "2", "20", "21", "22", "23", "24", "25", "26",
    #                "27", "28", "29", "3", "30", "31", "32", "33", "34", "35",
    #                "36", "37", "38", "39", "4", "40", "41", "42", "43", "44",
    #                "45", "46", "47", "48", "49", "5", "6", "7", "8", "9"]
    doc_scores = rs.predict()
    hyp_summaries = rs.create_summary(doc_scores)
    print("Summaries were generated... scoring ...")
    #print(hyp_summaries)
    scores = rs.score(hyp_summaries)
    print(scores)
