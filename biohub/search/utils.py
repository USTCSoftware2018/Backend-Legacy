import re
from string import punctuation, whitespace


punct_ws_re = r'[\s{}]+'.format(punctuation + whitespace).replace('-', r'\-')


def split_punct(x: str):
    r = re.compile(punct_ws_re)
    return r.split(x)

