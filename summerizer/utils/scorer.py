from rouge import Rouge


# pylint: disable=too-few-public-methods
class Scorer:
    def __init__(self):
        self.rouge = Rouge()

    def rouge_score(self, hypothesis, reference):
        scores = self.rouge.get_scores(hypothesis, reference, avg=True)
        return scores
