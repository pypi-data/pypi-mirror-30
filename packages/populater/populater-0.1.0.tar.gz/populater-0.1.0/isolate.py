
import logging

log				= logging.getLogger("isolate")
log.setLevel( logging.DEBUG )

def method(name=None, fn=None, err=None):
    if fn is None:
        def wrap(f):
            method(f)
            return f
        return wrap

    if name is None:
        name			= fn.__name__
        if name == '<lambda>':
            raise Exception("Lambda given with no method name.  Method won't be callable without a name.")

    gvars			= globals()
    def wrapper(*args):
        nonlocal gvars
        ctx			= gvars.get('isolate/fnctx', {})
        try:
            return fn(ctx, *args)
        except Exception as e:
            log.exception("Method {} failed to execute with arguments: {}".format(name, args))
            if callable(err):
                err(e)
        return None
            
    wrapper.source		= fn
    gvars[name]			= wrapper

def error(fn=None):
    gvars			= globals()
    if fn is None:
        def wrap(f):
            gvars['isolate/errfn']	= f
            return f
        return wrap
    else:
        gvars['isolate/errfn']	= fn

def evaluate(code, context=None, fn_context=None):
    gvars			= globals()
    context			= context or gvars
    gvars['isolate/fnctx']	= fn_context or context
    err				= gvars.get('isolate/errfn')
    try:
        def __eval__(self, __code__):
            log.debug("Evaluating code '{}' in context {}".format(code, self))
            return eval( __code__ )
        return __eval__(context, code)
    except Exception as e:
        if callable(err):
            err(e)
        return None
