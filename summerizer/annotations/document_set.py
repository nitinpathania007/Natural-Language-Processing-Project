from sklearn.feature_extraction.text import CountVectorizer


class DocumentSet:
    def __init__(self, n):
        self.documents = []
        # attributes collected from all documents in the set
        self.attributes = {}
        self._set_name = n
        self.word_counts = None

    def __iter__(self):
        for doc in self.documents:
            yield doc

    def get_doc_by_name(self, doc_name):
        for doc in self.documents:
            if doc.name == doc_name:
                return doc
        return None

    def name(self):
        return self._set_name

    def add(self, doc):
        self.documents.append(doc)

    def create_word_probabilities(self):
        """
        :return: A dictionary mapping words to their counts in this document set
        """
        # iterate the documents and count the number of non-stop words
        counts = CountVectorizer()
        texts = self.get_corpus_text()
        cv_fit = counts.fit_transform([texts])
        word_list = counts.get_feature_names()
        count_list = cv_fit.toarray().sum(axis=0)
        self.word_counts = dict(zip(word_list, count_list))

    def get_corpus_text(self):
        """
        This method inserts a newline between every document.

        :return: All the text in this document set concatenated into one string
        """
        return "\n".join([doc.annotations["full_text"][0].text for doc in self.documents])
