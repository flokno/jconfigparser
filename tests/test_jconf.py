import json
from pathlib import Path

import jconfigparser as jp

parent = Path(__file__).parent


c1 = jp.ConfigDict(parent / "test.jconf", allow_multiple_options=True)


def test_read():
    c2 = json.load(open(parent / "ref.json"))

    assert c1 == c2


def test_write(tmp_path):
    outfile = tmp_path / "test.jconf"
    c1.write(outfile)
    c1.write_raw(outfile)


def test_api():
    assert isinstance(c1.get_string(), str)