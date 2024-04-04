import datetime
from typing import Generator

import pytest

from acc_lcsh_check.checker import read_data, get_data


def test_read_data():
    data = read_data("tests/test_terms.txt")
    for term in data:
        assert term[0].strip('" ') == "Foo"
        assert term[1].strip('" ') == "sh00000000"
    assert isinstance(data, Generator)


def test_get_data_deprecated(mock_deprecated_skos_json_response):
    today = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
    get_data("tests/test_terms.txt", outpath="tests/out/")
    outfile = open(f"tests/out/deprecated_terms_{today}.txt", "r")
    assert outfile.read() == "sh00000000\n"


def test_get_data_changed(mock_changed_skos_json_response):
    today = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
    get_data("tests/test_terms.txt", outpath="tests/out/")
    outfile = open(f"tests/out/changed_terms_{today}.txt", "r")
    assert (
        outfile.read()
        == "{'id': 'sh00000000', 'current_heading': 'Spam', 'old_heading': 'Foo'}\n"
    )


def test_get_data_new_list(mock_new_skos_json_response):
    today = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
    get_data("tests/test_terms.txt", outpath="tests/out/")
    outfile = open(f"tests/test_{today}.txt", "r")
    assert outfile.read() == '"Foo", "sh00000000"\n'


def test_get_data_todays_file(mock_new_skos_json_response):
    today = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
    with pytest.raises(ValueError):
        get_data(f"test_{today}.txt", outpath="tests/out/")
    # outfile = open(f"tests/test_terms_updated_{today}.txt", "r")
