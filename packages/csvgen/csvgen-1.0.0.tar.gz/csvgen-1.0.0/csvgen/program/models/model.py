class Word:
    def __init__(self, value):

        self.value = value
        self.character_count = len(value)
        self.distinct_character_count = len(''.join(set(value)))
        self.word_count = len(value.split(" "))
        self.distinct_word_count = len(set(value.split(" ")))
        self.start_character = value[:1]
        self.end_character = value[-1:]
        self.container_name = ""
        self.container_position = ""
        self.contains_duplicate_characters = False
        self.contains_duplicate_words = False

        if self.character_count - self.distinct_character_count != 0:
            self.contains_duplicate_characters = True

        if self.word_count - self.distinct_word_count !=0:
            self.contains_duplicate_words = True


class Place(Word):
    def __init__(self, value):
        Word.__init__(self, value)
        self.state = ""
        self.city = ""
        self.state_name = ""
        self.county = ""
        self.city_alias = ""
        self.zip_code = ""
        self.latitude = ""
        self.longitude = ""
        self.country = ""


class FirstName(Word):
    def __init__(self, value):
        Word.__init__(self, value)


class LastName(Word):
    def __init__(self, value):
        Word.__init__(self, value)


class Address:
    def __init__(self):
        self.recipient = ""
        self.address_line_1 = ""
        self.address_line_2 = ""
        self.city = ""
        self.state = ""
        self.county = ""
        self.zip_code = ""


class Suffix:
    def __init__(self):
        self.variants = None  # []
        self.abbreviated = ""
        self.container_name = ""
        self.container_position = 0
        self.value = ""

    def set_value(self, use_variant, get_variant):

        if use_variant is True:
            self.value = get_variant(self.variants)
        else:
            self.value = self.abbreviated






