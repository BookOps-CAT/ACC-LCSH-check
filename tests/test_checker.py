import datetime
import pytest

from acc_lcsh_check.checker import read_data, get_data


def test_read_data():
    data = read_data("tests/test_terms.txt")
    for term in data:
        assert term[0].strip('" ') == "Foo"
        assert term[1].strip('" ') == "sh00000000"


@pytest.mark.parametrize("heading_type", ["subjects", "names", "demographicTerms"])
def test_get_data_deprecated(mock_deprecated_skos_json_response, heading_type):
    today = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
    get_data("tests/test_terms.txt", id_type=heading_type)
    outfile = open(f"temp/deprecated_terms_{today}.txt", "r")
    assert outfile.read() == "sh00000000\n"


@pytest.mark.parametrize("heading_type", ["subjects", "names", "demographicTerms"])
def test_get_data_changed(mock_changed_skos_json_response, heading_type):
    today = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
    get_data("tests/test_terms.txt", id_type=heading_type)
    outfile = open(f"temp/changed_terms_{today}.txt", "r")
    assert (
        outfile.read()
        == "{'id': 'sh00000000', 'current_heading': 'Spam', 'old_heading': 'Foo'}\n"
    )
