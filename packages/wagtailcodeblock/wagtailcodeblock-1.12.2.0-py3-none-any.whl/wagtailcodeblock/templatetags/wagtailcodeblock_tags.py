from django.template import Library, Node
from django.utils.safestring import mark_safe

from ..settings import (
    get_prism_version,
    get_theme
)

register = Library()


@register.simple_tag
def get_script_version():
    prism_version = get_prism_version()
    return prism_version


@register.simple_tag
def load_prism_theme():
    prism_version = get_prism_version()
    theme = get_theme()

    if theme:
        script = "<link href='https://cdnjs.cloudflare.com/ajax/libs/prism/{0}/themes/prism-{1}.min.css' rel='stylesheet'/>".format(
            prism_version,
            theme,
        )
        return mark_safe(script)
    return ''


@register.simple_tag
def load_prism_js():
    prism_version = get_prism_version()
    script = "<script defer src='https://cdnjs.cloudflare.com/ajax/libs/prism/{0}/prism.min.js'></script>".format(
        prism_version,
    )
    return mark_safe(script)


@register.tag
def renderonce(parser, token):
    """
    Usage: {% renderonce %}This will only be rendered the first time.{% endrenderonce %}
    This is useful in StreamField blocks for JS and CSS.
    """

    nodelist = parser.parse(('endrenderonce',))
    parser.delete_first_token()

    return RenderOnceNode(nodelist)


class RenderOnceNode(Node):
    """
    Class to store which sections have already been rendered once, so they aren't
    rendered again. This is useful in a StreamField that needs CSS or JS included
    once, but not in each section.
    """

    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context: dict) -> str:
        from hashlib import md5

        context['already_rendered'] = context.get('already_rendered', set())

        output = self.nodelist.render(context)
        output_hash = md5(output.encode('utf-8')).hexdigest()

        print(output_hash)
        print(context['already_rendered'])

        if output_hash in context['already_rendered']:
            return ''

        context['already_rendered'].add(output_hash)

        return self.nodelist.render(context)
