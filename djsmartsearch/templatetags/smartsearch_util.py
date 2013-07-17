import urllib
import urlparse
from django import template
from django.template.defaulttags import Node


register = template.Library()

class MergeKwargsNode(Node):

    def __init__(self, current_url, page_arg_name, start):
        self.current_url = template.Variable(current_url)
        self.page_arg_name = template.Variable(page_arg_name)
        self.start = template.Variable(start)
    
    def render(self, context):
        try:
            start = self.start.resolve(context)
            current_url = self.current_url.resolve(context)
            page_arg_name = self.page_arg_name.resolve(context)
        except Exception:
            raise template.TemplateSyntaxError("Invalid variables passed to start_url tag")
        
        params = {page_arg_name:start}
        url_parts = list(urlparse.urlparse(current_url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(params)
        
        url_parts[4] = urllib.urlencode(query)
        
        return urlparse.urlunparse(url_parts)


@register.tag
def start_url(parser, token, node_cls=MergeKwargsNode):

    try:
        tag_name, current_url, page_arg_name, start = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly 3 arguments" % token.contents.split()[0])
    return node_cls(current_url, page_arg_name, start)

