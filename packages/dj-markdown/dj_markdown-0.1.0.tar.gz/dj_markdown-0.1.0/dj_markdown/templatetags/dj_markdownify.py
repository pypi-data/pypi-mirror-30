from django import template
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from django.contrib.staticfiles.templatetags.staticfiles import static

register = template.Library()

CODE_THEMES = [
    'agate',
    'androidstudio',
    'arduino-light',
    'arta',
    'ascetic',
    'atelier-cave-dark',
    'atelier-cave-light',
    'atelier-dune-dark',
    'atelier-dune-light',
    'atelier-estuary-dark',
    'atelier-estuary-light',
    'atelier-forest-dark',
    'atelier-forest-light',
    'atelier-heath-dark',
    'atelier-heath-light',
    'atelier-lakeside-dark',
    'atelier-lakeside-light',
    'atelier-plateau-dark',
    'atelier-plateau-light',
    'atelier-savanna-dark',
    'atelier-savanna-light',
    'atelier-seaside-dark',
    'atelier-seaside-light',
    'atelier-sulphurpool-dark',
    'atelier-sulphurpool-light',
    'atom-one-dark',
    'atom-one-light',
    'brown-paper',
    'codepen-embed',
    'color-brewer',
    'darcula',
    'dark',
    'darkula',
    'docco',
    'dracula',
    'far',
    'foundation',
    'github-gist',
    'github',
    'googlecode',
    'grayscale',
    'gruvbox-dark',
    'gruvbox-light',
    'hopscotch',
    'hybrid',
    'idea',
    'ir-black',
    'kimbie.dark',
    'kimbie.light',
    'magula',
    'mono-blue',
    'monokai-sublime',
    'monokai',
    'obsidian',
    'ocean',
    'paraiso-dark',
    'paraiso-light',
    'pojoaque',
    'purebasic',
    'qtcreator_dark',
    'qtcreator_light',
    'railscasts',
    'rainbow',
    'routeros',
    'school-book',
    'solarized-dark',
    'solarized-light',
    'sunburst',
    'tomorrow-night-blue',
    'tomorrow-night-bright',
    'tomorrow-night-eighties',
    'tomorrow-night',
    'tomorrow',
    'vs',
    'vs2015',
    'xcode',
    'xt256',
    'zenburn',
]


class HighlightRenderer(mistune.Renderer):
    def block_code(self, code, lang):
        if not lang:
            return '\n<pre><code>%s</code></pre>\n' % \
                mistune.escape(code)
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter()
        return highlight(code, lexer, formatter)


@register.filter
def markdown_code(value):
    renderer = HighlightRenderer()
    markdown = mistune.Markdown(renderer=renderer)
    return markdown(value)


@register.filter
def markdown(value):
    markdown = mistune.Markdown()
    return markdown(value)


@register.simple_tag
def markdown_code_css(value='default'):
    if value in CODE_THEMES:
        url = static('dj_markdown/css/styles/{}.css'.format(value))
    else:
        url = static('dj_markdown/css/styles/default.css')
    return '<link rel="stylesheet" href="{}">'.format(url)


@register.simple_tag
def markdown_code_js(cdn=True):
    if cdn:
        return '<script src="//cdnjs.cloudflare.com/ajax/libs/highlight.js/9.12.0/highlight.min.js"></script>'
    url = static('dj_markdown/js/highlight.js')
    return '<script src="{}"></script>'.format(url)


@register.simple_tag
def markdown_code_js_init():
    init_highlight = """
    <script>
    $(document).ready(function () {
        $('pre code').each(function (i, block) {
            hljs.highlightBlock(block);
        });
        });
    </script>
    """
    return init_highlight


@register.simple_tag
def markdown_math():
    return "<script src='https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML' async></script>"