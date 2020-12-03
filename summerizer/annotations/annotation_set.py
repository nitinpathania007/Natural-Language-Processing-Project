import json
import os

from summerizer.annotations.annotation import Annotation


# pylint: disable=too-many-public-methods
class AnnotationSet:
    def __init__(self, n):
        self.__annotations = []
        self.__set_name = n

    def __len__(self):
        return len(self.__annotations)

    def __iter__(self):
        return self.forward()

    def __str__(self):
        return self.__set_name

    def __getitem__(self, index):
        try:
            return self.__annotations[index]
        except IndexError:
            return None

    def get_name(self):
        return self.__set_name

    def pop(self, i=0):
        """Pops the ith item from the set, defaults to the first."""
        return self.__annotations.pop(i)

    def forward(self):
        for ann in self.__annotations:
            yield ann

    def remove(self, i):
        """ removes the ith element from the annotations """
        del self.__annotations[i]

    def remove_annotation(self, annotation):
        remove_index = -1
        j = 0
        for ann in self.__annotations:
            if ann == annotation:
                remove_index = j
                break
            j += 1

        if remove_index > -1:
            del self.__annotations[remove_index]

    def remove_annotation_by_id(self, i):
        remove_index = -1
        for j in range(0, len(self.__annotations)):
            if self.__annotations[j].id == i:
                remove_index = j
        if remove_index > -1:
            del self.__annotations[remove_index]

    def add(self, annotation):
        """Put this annotation in the proper order."""
        if not self.__annotations:
            self.__annotations.append(annotation)
        elif annotation > self.__annotations[-1]:
            self.__annotations.append(annotation)
        else:
            for i in range(0, len(self.__annotations)):
                if annotation < self.__annotations[i]:
                    self.__annotations.insert(i, annotation)
                    break
            else:
                # catch the case where the next added is truly the last one.
                # *should be captured earlier by the elif
                self.__annotations.append(annotation)

    def contains(self, other):
        """Return true if this set has an annotation with the same span as the
        supplied annotation."""
        for ann in self.__annotations:
            if ann == other:
                return True
        return False

    def get_subset(self, start, end):
        """Returns a list of annotations that fall between the start and end
        provided."""
        subset = AnnotationSet("subset")
        for ann in self.__annotations:
            if ann.start >= start and ann.end <= end:
                subset.add(ann)
        return subset

    def get_over_lapping_annotations(self, annotation):
        """
        Return a set of annotations from this set that overlap the
        annotation provided.
        """
        overlapping = AnnotationSet("overlapping")
        overlapping.add_all(self.get_subset(annotation.start, annotation.end))
        return overlapping

    def get_contained_set(self, annotation):
        subset = AnnotationSet("contained")
        for ann in self.__annotations:
            if annotation.start >= ann.start and annotation.end <= ann.end:
                subset.add(ann)
        return subset

    def get_annotation_by_span(self, start, end):
        """Return annotation that matches the given span."""
        for ann in self.__annotations:
            if start == ann.start and end == ann.end:
                return ann
        return None

    def get_annotation_by_id(self, num):
        """Returns the annotation in the container that has the corresponding
        id number."""
        num = int(num)
        for ann in self.__annotations:
            if ann.id == num:
                return ann
        return None

    def get_list(self):
        return self.__annotations

    def get(self, i):
        """return the ith annotation from the container"""
        if i > len(self.__annotations):
            return None
        return self.__annotations[i]

    def get_next_annotation(self, other):
        """Returns the next annotation in the container, otherwise None"""
        for ann in self.__annotations:
            if ann.start > other.end:
                return ann
        return None

    def get_next_id(self):
        max_id = -1
        ids = [ann.id for ann in self.__annotations]
        for i in ids:
            if i > max_id:
                max_id = i
        return max_id + 1

    def get_previous_annotation(self, other):
        """returns the previous annotation."""
        prev = None
        for ann in self.__annotations:
            if ann.end >= other.start:
                return prev
            prev = ann
        return prev

    def extend(self, other):
        """Extend this annotation set from another annotation set or list, with the given one."""
        for ann in other:
            self.add(ann)

    def add_all(self, annotation_list):
        """Adds all annotations from a list to the current annotation set."""
        for ann in annotation_list:
            self.add(ann)

    def intersection(self, oset):
        """Returns the intersection between this set and the other """
        i = AnnotationSet("intersection of %s and %s" % (self.__set_name, oset.getName()))
        for ann in self.__annotations:
            if oset.contains(ann):
                i.add(ann)
        return i

    def to_json(self):
        as_dict = {
            "set_name": self.__set_name,
            "annotations": [ann.to_dict() for ann in self.__annotations]
        }
        return json.dumps(as_dict)

    def write_annotation_file(self, dest):
        """
        :param dest: where to write the annotations
        """
        with open(dest + os.path.sep + self.__set_name, 'w') as out_file:
            out_file.write(self.to_json())

    def read_annotation_file(self, src):
        """
        overwrites the existing annotation set
        :param src:  the file to read from
        """
        with open(src, 'r') as in_file:
            # reset this annotation set
            self.__annotations = []
            json_obj = json.loads(''.join(in_file.readlines()))
            for ann_dict in json_obj["annotations"]:
                self.add(Annotation(ann_dict["id"], ann_dict["text"],
                                    ann_dict["label"], ann_dict["start"],
                                    ann_dict["end"]))
            self.__set_name = json_obj["set_name"]
