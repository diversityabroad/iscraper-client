import urllib
import urlparse
from django import template
from django.template.defaulttags import Node


register = template.Library()

class MergeKwargsNode(Node):

    def __init__(self, current_url, start):
        self.current_url = template.Variable(current_url)
        self.start = template.Variable(start)
    
    def render(self, context):
        try:
            start = self.start.resolve(context)
            current_url = self.current_url.resolve(context)
        except Exception:
            raise template.TemplateSyntaxError("Invalid variables passed to start_url tag")
        
        params = {'start':start}
        url_parts = list(urlparse.urlparse(current_url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(params)
        
        url_parts[4] = urllib.urlencode(query)
        
        return urlparse.urlunparse(url_parts)


@register.tag
def start_url(parser, token, node_cls=MergeKwargsNode):

    try:
        tag_name, current_url, start = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly two arguments" % token.contents.split()[0])
    return node_cls(current_url, start)

