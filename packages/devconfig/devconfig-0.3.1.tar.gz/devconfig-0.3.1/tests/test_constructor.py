import devconfig
from devconfig.helper import URL
import datetime

def test_proof_of_concept():
    from tests.samples import constructors0
    assert constructors0.x == 'http://www.google.com'
    assert isinstance(constructors0.x, URL)

def test_constructors_merge():
    devconfig.merges['tests.samples.constructors1']._with('tests.samples.constructors0')
    from tests.samples import constructors1
    assert constructors1.x == 'http://www.google.com'
    assert isinstance(constructors1.x, URL)
    assert constructors1.wait == datetime.timedelta(0, 7200)