
import logging
import re
import string

from .				import isolate

log				= logging.getLogger('Populater')
# log.setLevel(logging.DEBUG)

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

    def eval(self, ref, ctx, fn_ctx=None, create_path=False):
        log.debug("Eval path {}".format(ref))
        keys			= ref.split('.')
        for k in keys:
            prev_ctx		= ctx
            log.debug("Extracting path segment {}".format(k))
            if isinstance(ctx, dict):
                right		= k.lstrip(string.ascii_letters + string.digits + "_")
                k		= k.rstrip(right)
                ctx		= isolate.evaluate("self.get('{}')".format(k), ctx, fn_ctx)
                if right:
                    ctx		= isolate.evaluate("self{}".format(right), ctx, fn_ctx)
            elif isinstance(ctx, object) and ctx is not None:
                ctx		= isolate.evaluate("self.{}".format(k), ctx, fn_ctx)
            else:
                return None
            
            if ctx is None and create_path is True:
                if isinstance(prev_ctx, dict):
                    prev_ctx[k]	= {}
                    ctx		= prev_ctx[k]
                else:
                    setattr(prev_ctx, k, {})
                    ctx		= getattr(prev_ctx, k)
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
    if not isinstance(data, (object, dict)):
        raise Exception("Populater can only take complex objects, not type '{}'.  See Populater.template() for other uses.".format(type(data)))

    def wrap(text):
        return Template(text).context(data, ctx)
    
    def save(path, d):
        segments		= path.split('.')
        last			= segments.pop()
        path			= ".".join(segments)
        if path:
            endpoint		= Template("< {}".format(path)).eval(path, data, ctx, create_path=True)
        else:
            endpoint		= data
            
        if isinstance(endpoint, dict):
            endpoint[last]	= d
        else:
            setattr(endpoint, last, d)
            
        return wrap(path)
    
    wrap.save			= save
    return wrap

Populater.template		= Template
Populater.error			= isolate.error
Populater.method		= isolate.method
