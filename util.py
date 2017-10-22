import string
import re
from unicodedata import normalize

PUNCTUATION_RE = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def count_words(text):
    '''
        Count the words in a string given by `text`.

        The text generally will come from a Markdown file, which allows
        for arbitary HTML tags, which must be removed as they do not count
        towards the final total. Additionally, puncutation must be replaced
        by whitespace where appropriate.
    '''
    html_tags = re.compile('<.*?>')
    text = re.sub(html_tags, '', text)

    punctuation = re.compile('[{}]'.format(re.escape(string.punctuation)))
    text = punctuation.sub(' ', text)
    words = text.split()

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
        normalised = [v.title() for v in value]

        return ', '.join(normalised)
    else:
        # Just convert the value to a string if we get any other type.
        return str(value)
