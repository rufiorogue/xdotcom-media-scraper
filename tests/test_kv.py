from x_media_scraper.kv import KV
import tempfile
import os, os.path


def get_temp_file():
    return tempfile.gettempdir() + '/8472947539927/test_kv.db'

def cleanup():
    os.unlink(get_temp_file())
    os.rmdir(os.path.dirname(get_temp_file()))


def test_kv_empty():
    kv = KV(get_temp_file())

    assert kv.is_empty()
    assert kv.get_value('aaa') is None

    cleanup()

def test_kv_getset():
    kv = KV(get_temp_file())

    kv.set_value('x', 'y')
    assert not kv.is_empty()
    assert kv.get_value('x') == 'y'

    cleanup()


def test_kv_update_value():
    kv = KV(get_temp_file())

    kv.set_value('x', 'y')
    assert kv.get_value('x') == 'y'

    kv.set_value('x', 'z')
    assert kv.get_value('x') == 'z'

    cleanup()

def test_kv_setmany():
    kv = KV(get_temp_file())

    kv.set_many( [('x', 1), ('y', 2)] )
    assert kv.get_value('x') == 1
    assert kv.get_value('y') == 2

    cleanup()

def test_kv_varioustypes():
    kv = KV(get_temp_file())

    kv.set_value('a', 'b')
    kv.set_value('x', 1)
    kv.set_value('y', [3,4,5])
    kv.set_value('z', {'foo':'bar', 'bar': 3})

    assert kv.get_value('a') == 'b'
    assert kv.get_value('x') == 1
    assert kv.get_value('y') == [3,4,5]
    assert kv.get_value('z') == {'foo':'bar', 'bar': 3}

    cleanup()
