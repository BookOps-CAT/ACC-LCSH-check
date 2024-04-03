import datetime
import os
import pytest

from acc_lcsh_check.checker import read_data, get_data


def test_read_data():
    data = read_data("tests/test_terms.txt")
    for term in data:
        assert term[0].strip('" ') == "Foo"
        assert term[1].strip('" ') == "sh00000000"


@pytest.mark.webtest
def test_get_data_deprecated(mock_deprecated_skos_json_response):
    today = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
    if os.path.exists(f"temp/deprecated_terms_{today}.txt"):
        os.remove(f"temp/deprecated_terms_{today}.txt")
    get_data("tests/test_terms.txt")
    outfile = open(f"temp/deprecated_terms_{today}.txt", "r")
    assert outfile.read() == "sh00000000\n"


@pytest.mark.webtest
def test_get_data_changed(mock_current_skos_json_response):
    today = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
    if os.path.exists(f"temp/changed_terms_{today}.txt"):
        os.remove(f"temp/changed_terms_{today}.txt")
    get_data("tests/test_terms.txt")
    outfile = open(f"temp/changed_terms_{today}.txt", "r")
    assert (
        outfile.read()
        == "{'id': 'sh00000000', 'current_heading': 'Spam', 'old_heading': 'Foo'}\n"
    )
