from pathlib import Path
import os


data_path = ''.join((os.path.dirname(os.path.abspath(__file__)), "/data"))
output_path = ''.join((os.path.dirname(os.path.abspath(__file__)), "/output"))
document_path = ''.join((os.path.dirname(os.path.abspath(__file__)), "/docs"))

iterations = 1000
delimiter = "|"
randomize_range = 1, 999999
use_suffix_variants = True

file_names = {
    "all_last_names": Path(data_path, "all.last.txt"),
    "cities": Path(data_path, "cities.txt"),
    "male_first_names": Path(data_path, "male.first.txt"),
    "female_first_names": Path(data_path, "female.first.txt"),
    "places": Path(data_path, "places.txt"),
    "suffixes": Path(data_path, "suffixes.txt"),
    "words": Path(data_path, "words.txt"),
    "zips": Path(data_path, "zip.codes.txt"),
    "help": Path(document_path, "help.txt"),
    "manual": Path(document_path, "man.txt"),
    "output": Path(output_path, "output.txt")
}

display_formats = {
    "standard": "{Recipient}\n{AddressLine1}\n{City}, {State}, {ZipCode}",
    "business": "{Recipient}\n{AddressLine1}\n{AddressLine2}\n{City}, {State}, {ZipCode}"
}

file_formats = {
    "standard": delimiter.join(("{0}", "{1}", "{2}", "{3}", "{4}")),
    "business": delimiter.join(("{0}", "{1}", "{2}", "{3}", "{4}", "{5}")),
    "standard_header": "Recipient|Address Line 1|City|State|Zip Code",
    "business_header": "Recipient|Address Line 1|AddressLine 2|City|State|Zip Code"
}

character_lengths = {
    "recipient": 20,
    "address_line_1": 5,
    "address_line_2": 5,
    "city": 5,
    "state": 2,
    "county": 10,
    "zip_code": 5,
    "delivery_number": 3,
    "first_name": 5,
    "last_name": 5,
    "suffix": {"useVariants": True, "characters": 4}
}

