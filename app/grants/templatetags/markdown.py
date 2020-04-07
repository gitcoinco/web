from django import template
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html

register = template.Library()


class MarkdownRenderer(mistune.Renderer):
    def placeholder(self):
        return ''

    def block_code(self, code, lang=None):
        return code

    def block_quote(self, text):
        return text

    def block_html(self, html):
        return html

    def header(self, text, level, raw=None):
        return '\1md_header%d\1%s\2\n\n' % (level, text)

    def hrule(self):
        return '-----\n'

    def list(self, body, ordered=True):
        return "%s\n" % body

    def list_item(self, text):
        return u"\u2022 %s\n" % text

    def paragraph(self, text):
        return '%s\n' % text.strip(' ')

    def table(self, header, body):
        return '%s\n%s\n' % (header, body)

    def table_row(self, content):
        return '%s\n' % content

    def table_cell(self, content, **flags):
        return '%s' % (content)

    def double_emphasis(self, text):
        return '\1md_bold\1%s\2' % text

    def emphasis(self, text):
        return '\1md_italic\1%s\2' % text

    def codespan(self, text):
        return '%s' % text

    def linebreak(self):
        return '\n'

    def strikethrough(self, text):
        return '%s' % text

    def text(self, text):
        return text

    def escape(self, text):
        return text

    def autolink(self, link, is_email=False):
        return '%s' % (link)

    def link(self, link, title, text):
        return '%s' % (text)

    def image(self, src, title, text):
        return '%s' % text

    def inline_html(self, html):
        return html

    def newline(self):
        """Rendering newline element."""
        return '\n'

    def footnote_ref(self, key, index):
        return "%s" % key

    def footnote_item(self, key, text):
        return text

    def footnotes(self, text):
        return text


@register.filter
def markdown(value):
    renderer = MarkdownRenderer()
    markdown = mistune.Markdown(renderer=renderer)
    return mistune.markdown(value, escape=False, hard_wrap=True)