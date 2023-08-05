from __future__ import print_function


class CategoryConverter(object):
    def __init__(self, category_list, target_list, positive_tag):
        self._category_list = category_list
        self._target_list = target_list
        self._positive_tag = positive_tag
        self._positive_count = 0
        # Start parameter check
        self._parameter_check()

    def _parameter_check(self):
        if self._positive_tag not in self._target_list:
            print("Warm: positive tag %s not in target list %s" % (self._positive_tag, str(self._target_list)))
        if len(self._category_list) != len(self._target_list):
            raise ValueError("category list length is %d while target list length %d" %(len(self._category_list),
                             len(self._target_list)))

    def convert(self):
        category_dict = self.generate_category_dict()
        print("Generated category dict: %s" % str(category_dict))
        return [0 if item not in category_dict else category_dict[item] / (self._positive_count * 1.0) for item in self._category_list]

    def generate_category_dict(self):
        category_dict = {}
        for i in range(len(self._target_list)):
            if self._target_list[i] == self._positive_tag:
                self._positive_count += 1
                if self._category_list[i] not in category_dict:
                    category_dict[self._category_list[i]] = 1
                else:
                    category_dict[self._category_list[i]] += 1
        return category_dict
