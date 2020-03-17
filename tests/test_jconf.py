import json
from pathlib import Path

import jconfigparser as jp

parent = Path(__file__).parent


c1 = jp.Config(parent / "ref.jconf", allow_multiple_options=True)


def test_json_dump(tmp_path):
    json.dump(c1, open(tmp_path / "test.json", "w"), indent=1)


def test_read():
    c2 = json.load(open(parent / "ref.json"))

    for key in c2:
        assert c1[key] == c2[key]


def test_write(tmp_path):
    outfile = tmp_path / "test.jconf"
    c1.print()
    c1.write(outfile)


def test_api():
    assert isinstance(c1.get_string(), str)


def test_empty():
    jp.Config()
