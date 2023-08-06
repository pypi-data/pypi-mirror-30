from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.template import Template, Context
from django.template.loader import get_template
import re

#from mycms.models import Paths, Pages
#from mycms.pageview.base import get_pageview


register = template.Library()
from . import registry

script_str_re_obj =re.compile(r"""(?P<name>src|type)="(?P<value>.*)"|((?P<name2>priority)=(?P<value2>(\d*)))""", re.DOTALL)


@register.inclusion_tag('mycms/templatetags/file_upload.html')
def file_upload():
    #Nothing to add to the context for now.
    return { "none": None }

@register.inclusion_tag('mycms/templatetags/article_editor.html')
def article_editor():
    #Nothing to add to the context for now.
    return { "none": None }




class NullNode(template.Node):
    
    def __init__(self):
        pass
    
    def render(self, context):
        return ""

@register.tag
def Script(parser, token_str):
    """
    Adds a name to the context for referencing an arbitrarily defined string.

    For example:

        {% define "my_string" as my_string %}

    Now anywhere in the template:

        {{ my_string }}
    """

    def parse_tokens(tokens):
        #parse the tokens into a key value dict
        attrs  = {}
        for entry in tokens: 
            #We are looking for name=value pairs
           
            match = script_str_re_obj.search(entry)
            if match:
                name = match.group("name")
                value = match.group("value")
                
                if name is None: 
                #We get here if our regex did not match src or type
                    name = match.group("name2")
                    value = match.group("value2")
                    
                attrs.update({ name: value})
                
            #if we manage to get value for src , then we register    
        return attrs


    tokens = token_str.split_contents()
   
    attrs = parse_tokens(tokens)
        
    if attrs.get("src", None) is not None: 
        #We need at minimum src
        
        registry.register(src=attrs.get("src","/dummy/path"),
                          type=attrs.get("type", "text/javascript"),
                          priority=attrs.get("priority", 9999))
    else: 
        print("skipped {}".format(token_str))
    return NullNode()
    
   
    
   
class ScriptCollectorNode(template.Node):
    def __init__(self):
        
        pass

    def __repr__(self):
        return "<ScriptCollectorNode>"

    def render(self, context):
       
        return registry.html()
    
@register.tag
def ScriptCollector(parser, token_str):
    return ScriptCollectorNode()

    
class NullNode(template.Node):
    
    def __init__(self):
        pass
    
    def render(self, context):
        return ""



@register.tag
def Link(parser, token_str):
    """
    Adds a <link> for our css at the header of the page.   
    """
 
    def parse_tokens(tokens):
        
        tokens = token_str.split_contents()
        tokens = tokens[1:] #the first is always the tag name.        
    
        #each token is expected to be of the format 
        # name=value


    
    
    
    