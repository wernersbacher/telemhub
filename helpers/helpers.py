import random
import string

from flask_sqlalchemy import xrange


def get_int(num):
    try:
        num = int(num)
    except:
        num = 0

    return num


def length(elem):
    try:
        l = len(elem)
    except:
        l = 0
    return l


def random_dir():
    return ''.join(random.choice(string.ascii_lowercase) for i in xrange(5))
