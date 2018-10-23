import re
from string import punctuation, whitespace

def split_punct(x: str):
    r = re.compile(r'[\s{}]+'.format(punctuation + whitespace))
    return r.split(x)
