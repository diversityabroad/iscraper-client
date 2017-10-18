import urllib
try:
    import urlparse as url_parse
except ImportError:
    import urllib.parse as url_parse
from django import template
from django.conf import settings
from django.template.defaulttags import Node
try:  # Python 2.4 shim
    from urlparse import parse_qsl
except ImportError:
    from urllib.parse import parse_qsl
    # from cgi import parse_qsl

MAX_SNIPPIT_LENGTH = getattr(settings, 'MAX_SNIPPIT_LENGTH', 175)

register = template.Library()


class MergeKwargsNode(Node):

    def __init__(self, current_url, page_arg_names, start):
        self.current_url = template.Variable(current_url)
        self.page_arg_names = template.Variable(page_arg_names)
        self.start = template.Variable(start)

    def render(self, context):
        try:
            start = self.start.resolve(context)
            current_url = self.current_url.resolve(context)
            page_arg_names = self.page_arg_names.resolve(context)
        except Exception:
            raise template.TemplateSyntaxError(
                "Invalid variables passed to start_url tag")

        names = page_arg_names.split(",")

        params = {names[0]: start}
        url_parts = list(url_parse.urlparse(current_url))
        query = dict(parse_qsl(url_parts[4]))
        for name in names[1:]:
            if name not in query:
                query.update({name: 1})

        query.update(params)

        try:
            url_parts[4] = urllib.urlencode(query)
        except AttributeError:
            url_parts[4] = url_parse.urlencode(query)

        return url_parse.urlunparse(url_parts)


@register.tag
def start_url(parser, token, node_cls=MergeKwargsNode):

    try:
        tag_name, current_url, page_arg_names, start = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires exactly 3 arguments" % token.contents.split()[0])
    return node_cls(current_url, page_arg_names, start)


@register.filter
def display_iscape_result_url(value):
    url = list(value.keys())[0]  # Python3 keys() returns a dictionary view object
    schemes = value[url]['schemes']
    if schemes is None:
        schemes = []
    return 'https:' + url if 'https' in schemes else 'http:' + url


@register.filter
def truncate_snippit(value):
    if value:
        if len(value) > MAX_SNIPPIT_LENGTH:
            last_space = value.rfind(" ", 0, MAX_SNIPPIT_LENGTH)
            value = value[:last_space] + " ..."
    return value


@register.filter
def display_iscape_result(value):
    page_hit = list(value.values())[0]  # only ever 1 here...
    hit_results = page_hit['hits']
    result = None
    for hit in hit_results:
        if hit.get('always_key_content_matches', None) != 'title':
            result = hit['content']
            break
    return result


@register.filter
def display_iscape_title(value):
    # accomadates both v1 and v2 api response to grab site title
    page_hit = list(value.values())[0]
    if page_hit.get("always", None):
        return page_hit['always'].get('title', "")
    if page_hit.get('title', None):
        return page_hit['title']
    hit_results = page_hit['hits']
    for hit in hit_results:
        if hit['field'] == 'title':
            return hit['raw_content']
    return ''


@register.filter
def display_greater_than(value, max):
    return_value = "%s" % (value)
    value = str(value)  # just in case value comes in as an int
    if value.isdigit() and int(value) > int(max):
        return_value = "%s (maximum %s results returned)" % (return_value, max)
    return return_value
