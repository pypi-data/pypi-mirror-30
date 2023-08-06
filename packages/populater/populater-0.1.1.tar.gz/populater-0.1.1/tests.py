
import logging

from .				import isolate
from .				import Populater

log				= logging.getLogger("tests")
log.setLevel( logging.DEBUG )


def test_isolate_method():
    isolate.method('chin', lambda self, *args: max(*args))

    assert isolate.evaluate('chin(1,2,3)') == 3

def test_isolate_method_decorator():
    @isolate.method()
    def chin(self, *args):
        return max(*args)

    assert isolate.evaluate('chin(1,2,3)') == 3

def test_isolate_method_fail():
    def assert_error(e):
        log.warn("ERROR: {}".format(e))
        assert isinstance(e, Exception)
        
    isolate.method('chin', max, assert_error)

    assert isolate.evaluate('chin(1,2,3)') == None

def test_populater_ctx():
    Person = {
        "age": 20,
        "name": {
	    "first": "Travis",
	    "last": "Mottershead",
	    "full": "Travis Mottershead"
        }
    }
    ctx			=  Populater( Person )

    assert ctx('{{ age }}') == '20'
    assert ctx('< age') == 20
    assert ctx('= {{ age }}') == 20
    assert ctx("{{ name.first }} {{ name.last }}") == "Travis Mottershead"
    assert ctx("{{ name.first }} {{ name.first }}") == "Travis Travis"
    assert ctx("< name.first")			== "Travis"
    assert ctx("= {{ age }} > 18") is True
    assert ctx("{{ name.none }}")		== ""
    assert ctx("= {{ name.none }}") is None
    assert ctx(":= {{ name.full }}")		== "= Travis Mottershead"
    assert ctx("= '= {{ name.full }}'")		== "= Travis Mottershead"
    assert ctx(":: {{ name.full }}")		== ": Travis Mottershead"
    assert ctx("= self['name']['full']")	== "Travis Mottershead"

