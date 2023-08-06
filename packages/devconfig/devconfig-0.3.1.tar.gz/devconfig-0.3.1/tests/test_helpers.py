from devconfig.helper import is_stream
def test_is_stream_helper_detects_open_file_stream():
    with open('tests/__init__.py') as init:
        assert is_stream(init)