import string
import re


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


def format_date(value, format='%a, %d %b %Y'):
    return value.strftime(format)


def format_tags(tags):
    return ['#{}'.format(tag) for tag in tags.split(', ')]
