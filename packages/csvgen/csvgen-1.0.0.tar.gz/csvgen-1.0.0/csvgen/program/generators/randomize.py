import random
from random import randint
from program import settings


def get_random(**kwargs):

    # all output values MUST be string values and is assumed
    # lists and dictionary object only contain strings

    # There are 3 cases this handles
    # 1. random integer string within a range without any other requirements using default range.
    # 2. random integer string within a specified range
    # 3. random integer string of a specified length

    i = ""
    if len(kwargs) == 0:
        i = str(randint(settings.randomize_range[0], settings.randomize_range[1]))
    else:
        if "start" in kwargs and "end" in kwargs:
            i = str(randint(int(kwargs["start"]), int(kwargs["end"])))
        elif "length" in kwargs:
            numbers = list("1234567890")
            for value in range(int(kwargs["length"])):
                i = i + random.choice(numbers)

    return i


def get_random_object(item):
    i = None
    if type(item) is list:
        i = random.choice(item)
    elif type(item) is dict:
        i = random.choice(item.keys())
    return i
