from pathlib import Path

import jconfigparser as jp


parent = Path(__file__).parent


def test_write(tmp_path):
    c1 = jp.Config(parent / "order.jconf")

    c1["a"]["d"] = "e"

    c1.write(tmp_path / "test_order.jconf")

    c2 = jp.Config(tmp_path / "test_order.jconf")

    assert c1["a.b"] == c2["a.b"]
