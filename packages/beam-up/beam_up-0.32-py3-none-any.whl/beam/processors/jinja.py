from .base import BaseProcessor

from jinja2 import Environment, FileSystemLoader, ChoiceLoader, DictLoader


from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

class JinjaProcessor(BaseProcessor):

    def highlight_styles(self, language=None):
        return '<style type="text/css">{}</style>'.format(HtmlFormatter().get_style_defs('.highlight'))

    def highlight(self, code, language=None):
        return highlight(code, PythonLexer(), HtmlFormatter())

    def get_jinja_env(self, input):
        dict_loader = DictLoader({'input' : input})
        theme_path = self.site.theme_path
        choice_loader = ChoiceLoader([dict_loader, FileSystemLoader('{}/templates'.format(theme_path)), FileSystemLoader(self.site.src_path)])
        env = Environment(loader=choice_loader)
        env.filters['href'] = self.href
        env.filters['file'] = self.file
        env.filters['highlight'] = self.highlight
        env.filters['highlight_styles'] = self.highlight_styles
        env.filters['translate'] = self.translate
        return env

    def process(self, input, vars):
        env = self.get_jinja_env(input)
        template = env.get_template('input')
        return template.render(**vars)