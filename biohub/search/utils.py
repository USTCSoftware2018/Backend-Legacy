import re
from string import punctuation, whitespace


punct_ws_re = r'[\s{}]+'.format(punctuation + whitespace)


def split_punct(x: str):
    r = re.compile(r'[\s{}]+'.format(punct_ws_re))
    return r.split(x)

