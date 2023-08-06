
import re

import isolate

class Template( object ):

    def __init__(self, text):
        if type(text) is not str:
            raise Exception("Template only takes 1 string, not type '{}'".format(type(text)))
        self.text		= text.strip()

        Populater.before	= self.text
        
    def fill(self, s, ctx, fn_ctx=None):
        text			= s
        matches			= re.findall("({{([^}]+)}})", s)
        for match,key in matches:
            key			= key.strip()
            value		= self.eval(key, ctx, fn_ctx)
            if value is None:
                value		= ""
            text		= text.replace(match, str(value))
        return text

    def eval(self, ref, ctx, fn_ctx=None):
        keys			= ref.split('.')
        for k in keys:
            if type(ctx) is not dict:
                return None
            ctx			= isolate.evaluate("self.get('{}')".format(k), ctx, fn_ctx)
        return ctx

    def context(self, ctx, fn_ctx=None):
        text			= self.fill(self.text, ctx, fn_ctx)
        
        ref			= text.startswith('<')
        raw			= text.startswith(':')
        run			= text.startswith('=')
        
        if ref or raw or run:
            text		= text[1:].strip()

        if ref:
            value		= self.eval(text, ctx, fn_ctx)
        elif run:
            value		= isolate.evaluate(text, ctx, fn_ctx)
        else:
            value		= text
            
        Populater.after		= value
        return value
            

def Populater(data, ctx=None):
    if type(data) is not dict:
        raise Exception("Populater can only take complex objects, not type '{}'.  See Populater.template() for other uses.".format(type(data)))

    def wrap(text):
        return Template(text).context(data, ctx)
    return wrap

Populater.template		= Template
Populater.error			= isolate.error
Populater.method		= isolate.method
