import itertools
import threading
import time
import sys
from program import settings
from program.models.model import Word, Place, FirstName, LastName, Suffix

#  Optionally: we could use the python csv library here but it's not necessary or required.


def load_words():

    words = []

    def load():
        position = 0
        with open(settings.file_names["words"]) as f:
            for line in f:
                row = line.split(",")
                w = Word(row[0])
                w.container_name = settings.file_names["words"]
                w.container_position = position
                if position != 0:
                    words.append(w)
                position += 1

    show_progress(load)

    return words


def load_places():

    places = []

    def load():
        position = 0
        with open(settings.file_names["cities"]) as f:
            for line in f:
                row = line.split("|")
                place = Place(row[1])
                place.value = row[1]
                place.state = row[0]
                place.city = row[1]
                place.state_name = row[2]
                place.county = row[3]
                place.city_alias = row[4]
                place.zip_code = row[5]
                place.latitude = row[6]
                place.longitude = row[7]
                place.country = "USA"
                place.container_name = settings.file_names["cities"]
                place.container_position = position

                if position != 0:  # exclude header
                    places.append(place)

                position += 1

    show_progress(load)

    return places


def load_name_data():
    first_names = []
    last_names = []

    def load():

        with open(settings.file_names["male_first_names"]) as m:
            male_names = m.readlines()
        with open(settings.file_names["female_first_names"]) as f:
            female_names = f.readlines()
        with open(settings.file_names["all_last_names"]) as a:
            all_last_names = a.readlines()

        male_names.pop(0)  # remove headers
        female_names.pop(0)
        all_last_names.pop(0)
        all_first_names = list(set(male_names)) + list(set(female_names))

        for line in range(len(all_first_names)):
            row = all_first_names[line].split(" ")
            first_name = FirstName(row[0])
            first_name.container_position = line
            first_name.container_name = "first and last name files combined"
            first_names.append(first_name)

        for line in range(len(all_last_names)):
            row = all_last_names[line].split(" ")
            last_name = LastName(row[0])
            last_name.container_position = line
            last_name.container_name = "first and last name files combined"
            last_names.append(last_name)

    show_progress(load)

    return first_names, last_names


def load_suffixes(use_variants, get_variant):

    suffixes = []

    def load():
        position = 0

        with open(settings.file_names["suffixes"]) as f:
            for line in f:
                row = line.split(",")
                variants = row[1].split("|")
                suffix = Suffix()
                suffix.abbreviated = row[0]
                suffix.variants = variants
                suffix.container_name = settings.file_names["suffixes"]
                suffix.container_position = position
                if position != 0:
                    suffix.set_value(use_variants, get_variant)
                    suffixes.append(suffix)
                position += 1

    show_progress(load)

    return suffixes


def load_alpha_values(iterations):

    prefixes = []
    characters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    prefixes = prefixes + characters

    for iteration in range(iterations):
        for character in characters:
            for char in characters:
                if iteration == 0:
                    prefixes.append(character + char)
                if iteration > 0:
                    prefix = character * iteration
                    prefixes.append(character + prefix + char)

    return prefixes


def show_progress(process):

    done = False
    chars = [".", "..", "...", "....", ".....", "......", "........", ".........", ".........."]

    def run():
        for c in itertools.cycle(chars):
            if done:
                break
            sys.stdout.write('\rloading ' + c)
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\rData Processing: Done!')

    t = threading.Thread(target=run)
    t.start()

    # wait for this finish to process
    process()
    time.sleep(0)
    done = True

