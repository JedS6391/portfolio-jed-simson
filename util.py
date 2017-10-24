import string
import re
from unicodedata import normalize
import datetime

PUNCTUATION_RE = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def first_occurence_of(strings, substring):
    for i, s in enumerate(strings):
        if substring in s:
              return i

    return -1

def count_words(text):
    '''
        Count the words in a string given by `text`.

        The text generally will come from a Markdown file, which allows
        for arbitary HTML tags, which must be removed as they do not count
        towards the final total. Additionally, puncutation must be replaced
        by whitespace where appropriate.
    '''

    # First, we need to ignore until the end of the metadata section.
    # This is signalled by the "Tags" attribute (note this is very specific to my blog implementation).

    lines = text.split('\n')
    idx = first_occurence_of(lines, 'Tags:')
    # Approximate the number of words if the original text has no tag metadata attribute.
    body_text = text if idx == -1 else ''.join(lines[idx + 1:])

    html_tags = re.compile('<.*?>')
    body_text = re.sub(html_tags, '', body_text)

    punctuation = re.compile('[{}]'.format(re.escape(string.punctuation)))
    body_text = punctuation.sub(' ', body_text)
    words = body_text.split()

    return len(words)

def slugify(text):
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
