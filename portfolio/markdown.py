# Based on https://gist.github.com/mikefromit/5a6fdfecc9310712f15a872df9f41f03
# Previously, the Flask-Markdown package was used but this is no longer working
# with Flask version 3 and is not being maintained, so the things we need
# have been added directly to the project.

from jinja2 import nodes
from jinja2.ext import Extension

import markdown as md

instance = md.Markdown(extensions=['markdown.extensions.fenced_code', 'markdown.extensions.meta'])

class Markdown(Extension):
    """
    A wrapper around the markdown filter for syntactic sugar.
    """

    tags = set(["markdown"])

    def __init__(self, environment):
        super(Markdown, self).__init__(environment)
        environment.filters['markdown'] = lambda v: instance.convert(v)

    def parse(self, parser): 
        """
        Parses the statements and defers to the markdown render method.
        """
        lineno = next(parser.stream).lineno
        body = parser.parse_statements(["name:endmarkdown"], drop_needle=True)

        return nodes.CallBlock(
            self.call_method("_render_markdown"), [], [], body
        ).set_lineno(lineno)

    def _render_markdown(self, caller=None):
        """
        Calls the markdown filter to transform the output.
        """
        if not caller:
            return ""
        
        return instance.convert(caller().strip())