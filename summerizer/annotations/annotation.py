import json


class Annotation:
    # pylint: disable=too-many-arguments
    def __init__(self, i, text, label, start, end):
        self.id = int(i)
        self.start = int(start)
        self.end = int(end)
        self.text = str(text)
        self.label = str(label)

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return self.to_json()

    def __lt__(self, other):
        return self.start < other.start

    def __le__(self, other):
        return self.start <= other.start

    def __gt__(self, other):
        return self.start > other.start

    def __ge__(self, other):
        return self.start >= other.start

    def __eq__(self, other):
        if self.start == other.start and self.end == other.end \
            and self.text == other.text and self.label == other.label:
            return True
        return False

    def __ne__(self, other):
        if self.start != other.start or self.end != other.end \
            or self.text != other.text or self.label != other.label:
            return True
        return False

    def get_span(self):
        return self.start, self.end

    def contains(self, other):
        return (self.start <= other.start) and (self.end >= other.end)

    def clean_text(self):
        return "%s" % self.text.replace("\n", " ")

    def clean_text_and_span(self):
        txt = self.text.replace("\n", " ")
        return "%s (%d,%d)" % (txt, self.start, self.end)

    def to_dict(self):
        a_dict = {
            "id": self.id,
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "label": self.label
        }
        return a_dict

    def to_json(self):
        return json.dumps(self.to_dict())
