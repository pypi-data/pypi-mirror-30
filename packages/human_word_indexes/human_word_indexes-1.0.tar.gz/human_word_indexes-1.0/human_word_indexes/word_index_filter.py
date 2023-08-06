import re, logging
logger = logging.getLogger(__name__)

class WordIndexFilter:

    def __init__(self):
        logger.info('Creating a WordIndexFilter with default values')
        self._negative_regex = re.compile(r'oe|sc|kh|x|z')
        self._double_letter_regex = re.compile(r'([a-zA-Z]).*?\1')
        self._max_word_length = 8
        self._min_word_length = 2


    def set_negative_regex(self, r):
        self._negative_regex = re.compile(r)
        return self

    def set_max_length(self,l):
        self._max_word_length = l
        return self

    def set_min_length(self,l):
        self._min_word_length = l
        return self

    def filter_word(self, w):
        if len(w) > self._max_word_length or \
                len(w) < self._min_word_length or \
                bool(self._negative_regex.search(w)):
            return False
        else:
            return True
