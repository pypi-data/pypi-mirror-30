import sys
import argparse
from program import settings
from program.generators.loader import load_places, load_suffixes, load_name_data, load_alpha_values, load_words
from program.generators.csv import generate_address_csv
from program.generators.randomize import get_random, get_random_object
from program.generators.address import get_addresses
from pprint import pprint
# TODO: figure out why --options don't work as expected with argparse


def process_work():

    if "-h" in sys.argv or "--help" in sys.argv:
        write_information("-h")  # Then exit
    if "-man" in sys.argv or "--manual" in sys.argv:
        write_information("-man")  # Then exit
    if "-ex" in sys.argv or "--example" in sys.argv:
        get_examples(load_name_data(), load_words(),
                     load_suffixes(use_variants=settings.use_suffix_variants,
                                   get_variant=get_random_object), load_places(), load_alpha_values(settings.iterations)
                     )

    # Then exit else process additional arguments

    parser = argparse.ArgumentParser(description="Creates CSV data for various use-cases", add_help=False)

    parser.add_argument("-GetRandomAlpha", "--ra", dest="GetRandomAlpha", help="Gets random alpha data",
                        required=False, nargs=3)
    parser.add_argument("-GetRandomNumeric", "--rn", dest="GetRandomNumeric", help="Gets random numeric data",
                        required=False, nargs=5)
    parser.add_argument("-GetStaticSequence", "--ss", dest="GetStaticSequence",  help="Gets static sequence data",
                        required=False, nargs=8)
    parser.add_argument("-GetRandomSequence", "--rs", dest="GetRandomSequence", help="Gets random sequence data",
                        required=False, nargs=7)
    parser.add_argument("-GetAddresses", "--a", dest="GetAddresses", help="Gets address data",
                        required=False, nargs=5)

    args = parser.parse_args()

    if args.GetRandomAlpha is not None:

        is_file, number_of_values, delimiter = args.GetRandomAlpha
        data = get_random_alpha(load_words(), int(number_of_values), delimiter)
        write_data(is_file, data)

    if args.GetRandomNumeric is not None:

        is_file, number_of_values, delimiter, start, end = args.GetRandomNumeric
        data = get_random_numeric(int(number_of_values), delimiter, start, end)
        write_data(is_file, data)

    if args.GetStaticSequence is not None:

        is_file, identifier, is_prefix, start, end, delimiter, joiner, is_alpha = args.GetStaticSequence
        data = get_static_sequence(identifier, convert_to_bool(is_prefix), int(start), int(end), delimiter, joiner,
                                   convert_to_bool(is_alpha), load_alpha_values(settings.iterations))
        write_data(is_file, data)

    if args.GetRandomSequence is not None:

        is_file, is_prefix, start, end, delimiter, joiner, is_alpha = args.GetRandomSequence
        data = get_random_sequence(convert_to_bool(is_prefix), int(start), int(end), delimiter, joiner,
                                   convert_to_bool(is_alpha), load_words(), load_alpha_values(settings.iterations))
        write_data(is_file, data)

    if args.GetAddresses is not None:

        is_file, is_filtered, length, address_type, include_header = args.GetAddresses
        addresses = get_addresses(convert_to_bool(is_filtered), int(length), load_name_data(), load_words(),
                                  load_suffixes(use_variants=settings.use_suffix_variants,
                                                get_variant=get_random_object), load_places())

        data = generate_address_csv(addresses, address_type, convert_to_bool(include_header), settings)
        write_data(is_file, data)


def get_random_alpha(word_list, number_of_values, delimiter):

    result = ""

    for i in range(number_of_values):
        w = get_random_object(word_list)
        result = result + ''.join((w.value, delimiter))

    output = result[:-1]

    return output


def get_random_numeric(number_of_values, delimiter, start, end):

    result = ""

    for i in range(number_of_values):
        w = get_random(start=start, end=end)
        result = result + ''.join((w, delimiter))

    output = result[:-1]

    return output


def get_static_sequence(identifier, is_prefix, start, end, delimiter, joiner, is_alpha, alpha_values):

    result = ""

    for i in range(start, end):
        if is_prefix is True:
            if is_alpha is True:
                result = result + ''.join((alpha_values[i], joiner, identifier, delimiter))
            else:
                result = result + ''.join((str(i), joiner, identifier, delimiter))
        else:
            if is_alpha is True:
                result = result + ''.join((identifier, joiner, alpha_values[i], delimiter))
            else:
                result = result + ''.join((identifier, joiner, str(i), delimiter))

    return result[:-1]


def get_random_sequence(is_prefix, start, end, delimiter, joiner, is_alpha, word_list, alpha_values):

    result = ""

    for i in range(start, end):
        if is_prefix is True:
            if is_alpha is True:
                result = result + ''.join((alpha_values[i], joiner, get_random_object(word_list).value, delimiter))
            else:
                result = result + ''.join((str(i), joiner, get_random_object(word_list).value, delimiter))
        else:
            if is_alpha is True:
                result = result + ''.join((get_random_object(word_list).value, joiner, alpha_values[i], delimiter))
            else:
                result = result + ''.join((get_random_object(word_list).value, joiner, str(i), delimiter))

    return result[:-1]


def get_examples(name_list, word_list, suffix_list, place_list, alpha_values):

    print("\nRANDOM ALPHA\n")
    print(get_random_alpha(word_list, 10, "~"))

    print("\nRANDOM NUMERIC\n")
    print(get_random_numeric(10, "|", 100, 1000))

    print("\nSTATIC SEQUENCES\n")
    print(get_static_sequence("ITEM", False, 10, 20, "|", "_", False, alpha_values))
    print(get_static_sequence("ITEM", True, 10, 20, "|", "_", False, alpha_values))
    print(get_static_sequence("ITEM", True, 10, 20, "|", "_", True, alpha_values))
    print(get_static_sequence("ITEM", False, 10, 20, "|", "_", True, alpha_values))

    print("\nRANDOM SEQUENCES\n")
    print(get_random_sequence(False, 0, 10, "|", "_", True, word_list,  alpha_values))
    print(get_random_sequence(True, 0, 10, "|", "_", True,  word_list, alpha_values))
    print(get_random_sequence(True, 0, 10, "|", "_", False,  word_list, alpha_values))
    print(get_random_sequence(False, 0,  10, "|", "_", False, word_list, alpha_values))

    print("\nADDRESSES - NON-FILTERED\n")
    addresses_1 = get_addresses(False, 10, name_list, word_list, suffix_list, place_list)
    result_a = generate_address_csv(addresses_1, "business", True, settings)
    pprint(result_a)

    print("\nADDRESSES - FILTERED\n")
    addresses_2 = get_addresses(True, 10, name_list, word_list, suffix_list, place_list)
    result_b = generate_address_csv(addresses_2, "business", True, settings)
    pprint(result_b)
    sys.exit(0)


def convert_to_bool(string_value):

    true_values = ["true", "t", "yes", "y"]
    false_values = ["false", "f", "no", "no"]

    bool_value = False

    if str.lower(string_value) in true_values:
        bool_value = True
    if str.lower(string_value) in false_values:
        bool_value = False

    return bool_value


def write_data(is_file, data):
    write_to_file = False

    if is_file == "f":
        write_to_file = True
    if is_file == "c":
        write_to_file = False

    if is_file not in ["c", "f"]:
        print("Data output option not recognized. Use [c] for console or [f] for file")
        return

    if write_to_file is True:
        if type(data) is list:
            with open(settings.file_names["output"], mode='w', encoding='utf-8') as file_output:
                file_output.write('\n'.join(data))
        else:
            with open(settings.file_names["output"], mode='w', encoding='utf-8') as file_output:
                file_output.write(data)
    else:
        pprint(data)

    pass


def write_information(args):

    if args == "-h":
        with open(settings.file_names["help"]) as f:
            for line in f:
                print(line.strip("\n"))

    if args == "-man":
        with open(settings.file_names["manual"]) as f:
            for line in f:
                print(line.strip("\n"))

    sys.exit(0)


