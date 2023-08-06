from program.models.model import Address
from program.generators.randomize import get_random, get_random_object
from program import settings


def get_addresses(is_filtered, length, name_list, word_list, suffix_list, place_list):

    address_list = []

    for value in range(length):
        address_list.append(get_address(is_filtered, name_list, word_list, suffix_list, place_list))

    return address_list


def get_address(is_filtered, name_list, word_list, suffix_list, place_list):

    address = Address()

    if is_filtered is True:

        filtered_first = [first for first in name_list[0]
                          if len(first.value) == settings.character_lengths["first_name"]]

        filtered_last = [last for last in name_list[1]
                         if len(last.value) == settings.character_lengths["last_name"]]

        first = get_random_object(filtered_first).value

        last = get_random_object(filtered_last).value

        filtered_places = [place for place in place_list if len(place.city) == settings.character_lengths["city"]
                           and len(place.state) == settings.character_lengths["state"]
                           and len(place.zip_code) == settings.character_lengths["zip_code"]
                           and len(place.county) == settings.character_lengths["county"]]

        place = (get_random_object(filtered_places))

        filtered_line_1 = [word for word in word_list
                           if len(word.value) == settings.character_lengths["address_line_1"]]

        filtered_line_2 = [word for word in word_list
                           if len(word.value) == settings.character_lengths["address_line_2"]]

        filtered_suffixes = [suffix for suffix in suffix_list
                             if len(suffix.value) == settings.character_lengths["suffix"]["characters"]]

        address.recipient = ''.join((first, " ", last))
        street_name = (get_random_object(filtered_line_1)).value
        suffix_name = (get_random_object(filtered_suffixes)).value
        street_number = get_random(length=settings.character_lengths["delivery_number"])
        address.address_line_1 = ' '.join((street_number, street_name, suffix_name))
        address.address_line_2 = (get_random_object(filtered_line_2)).value
        address.city = place.city
        address.state = place.state
        address.zip_code = place.zip_code
        address.county = place.county

    else:
        first = get_random_object(name_list[0]).value
        last = get_random_object(name_list[1]).value
        place = (get_random_object(place_list))
        address.recipient = ''.join((first, " ", last))
        street_number = get_random()
        street_name = (get_random_object(word_list)).value
        suffix_name = (get_random_object(suffix_list)).value
        address.address_line_1 = ' '.join((street_number, street_name, suffix_name))
        address.address_line_2 = (get_random_object(word_list)).value
        address.city = place.city
        address.state = place.state
        address.zip_code = place.zip_code
        address.county = place.county

    return address
