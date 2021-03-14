import string
import re
from unicodedata import normalize
import datetime

PUNCTUATION_RE = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def first_occurence_of(strings, substring) -> int:
    for i, s in enumerate(strings):
        if substring in s:
              return i

    return -1

def slugify(text: str) -> str:
    result = []

    for word in PUNCTUATION_RE.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')

        if word:
            result.append(word.decode('utf-8'))

    return '-'.join(result)

def format_date(value, format='%a, %d %b %Y'):
    return value.strftime(format)

def format_value(value):
    if isinstance(value, str) or isinstance(value, int):
        # Don't need to do anything special for strings/ints
        return value
    elif isinstance(value, list):
        # Convert the list to a print format.
        return ', '.join(value)
    elif isinstance(value, datetime.datetime):
        # Use the nice date formatter for dates
        return format_date(value)
    else:
        # Just convert the value to a string if we get any other type.
        return str(value)
