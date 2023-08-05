class Word(object):
    def __init__(self, word, case_insensitive=True):
        self.word = word
        self.is_case_insensitive = case_insensitive

    def starts_with(self, char):
        """
        Returns True if the word starts with char, False otherwise.
        """
        return self.char_equal(char, 0)

    def char_equal(self, char, index):
        """
        Returns True if the character at index equals char, False otherwise.
        """
        word_char = self.word[index]
        compare_char = char

        if self.is_case_insensitive:
            word_char = word_char.lower()
            compare_char = compare_char.lower()

        return word_char == compare_char

    def __str__(self):
        return "<Word: '" + reduce(lambda s1, s2: s1 + s2, self.word, '') + "'>"

    def __len__(self):
        return len(self.word)


class CamelHumpFilter(object):
    def __init__(self):
        self._filter_string = ''
        self._processed_filter_string = ''

    @property
    def filter_string(self):
        return self._filter_string

    @filter_string.setter
    def filter_string(self, value):
        self._filter_string = value
        self._processed_filter_string = self.process_filter_string(self._filter_string)

    @staticmethod
    def process_filter_string(filter_string):
        if len(filter_string) == 0:
            return []

        return filter(lambda s: s.isalnum(), filter_string.lower())

    @staticmethod
    def find_index(words, predicate, start_index=0):
        for index, word in enumerate(words):
            if index >= start_index and predicate(word):
                return index

        return None

    def is_filter_match(self, query):
        if len(self._processed_filter_string) == 0:
            return True

        words = self.to_word_list(query)

        if len(words) == 0:
            return False

        first_char = self._processed_filter_string[0]

        first_word_index = self.find_index(words, lambda w: w.starts_with(first_char))

        is_match = False
        while not is_match and first_word_index is not None:
            is_match = self.is_match_from_word(words, first_word_index, 0)
            first_word_index = self.find_index(words, lambda w: w.starts_with(first_char), first_word_index + 1)

        return is_match

    def is_match_from_word(self, words, word_index, start_filter_index=0):
        current_word = words[word_index]

        if len(words) > word_index + 1:
            next_word = words[word_index + 1]
        else:
            next_word = None

        next_word_start_indexes = []

        filter_index = start_filter_index
        current_word_index = 0

        while filter_index < len(self._processed_filter_string):
            current_char = self._processed_filter_string[filter_index]

            if (filter_index > start_filter_index and
                    next_word is not None and
                    next_word.starts_with(current_char)):
                next_word_start_indexes.append(filter_index)

            if (len(current_word) > current_word_index and
                    current_word.char_equal(current_char, current_word_index)):

                filter_index += 1
                current_word_index += 1
            else:
                is_match = False
                while not is_match and len(next_word_start_indexes) > 0:
                    is_match = self.is_match_from_word(words, word_index + 1, next_word_start_indexes.pop())

                return is_match

        return True

    @staticmethod
    def to_word_list(query):
        word_list = []
        current_word = []

        if len(query) == 0:
            return word_list

        for char in query:
            if not char.isalnum():
                # new word
                if len(current_word) > 0:
                    word_list.append(Word(current_word))
                    current_word = []

                continue

            if char.isupper() or char.isdigit():
                # New word
                if len(current_word) > 0:
                    word_list.append(Word(current_word))
                    current_word = []

            current_word.append(char)

        if len(current_word) > 0:
            word_list.append(Word(current_word))

        return word_list
