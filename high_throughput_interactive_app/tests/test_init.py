import re
import high_throughput_interactive_app as ht


def test_version():
    assert isinstance(ht.__version__, str)
    assert re.search(r"^\d+.\d+.?\d*$", ht.__version__)
