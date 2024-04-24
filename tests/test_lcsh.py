import pytest

from acc_lcsh_check.lcsh import LCTerm


@pytest.mark.parametrize(
    "heading_id, heading_str",
    [
        ("sh111", "foo"),
        ("na222", "bar"),
        ("dg333", "baz"),
    ],
)
def test_revised_term(heading_id, heading_str, mock_revised_response):
    term = LCTerm(
        id=heading_id,
        old_heading=heading_str,
    )
    assert term.id == heading_id
    assert term.old_heading == heading_str
    assert term.format == ".skos.json"
    assert term.url == "https://id.loc.gov/authorities/"
    assert term.query == f"{term.url + term.id_type + '/' + heading_id}"
    assert term.current_heading == "Spam"
    assert term.changes[0] == {
        "change_reason": "revised",
        "change_date": "2024-04-01T00:00:01",
    }
    assert term.recent_change is True
    assert term.is_deprecated is False
    assert term.revised_heading is True


@pytest.mark.parametrize(
    "heading_id",
    ["sh111", "na222", "dg333"],
)
def test_deprecated_term(heading_id, mock_deprecated_response):
    term = LCTerm(id=heading_id, old_heading="Foo")
    assert term.id == heading_id
    assert term.format == ".skos.json"
    assert term.url == "https://id.loc.gov/authorities/"
    assert term.query == f"{term.url + term.id_type + '/' + heading_id}"
    assert term.current_heading == "Bar"
    assert term.changes[0] == {
        "change_reason": "deprecated",
        "change_date": "2023-04-01T00:00:01",
    }
    assert term.recent_change is False
    assert term.is_deprecated is True
    assert term.revised_heading is True


@pytest.mark.parametrize(
    "heading_id",
    ["sh111", "na222", "dg333"],
)
def test_new_term(heading_id, mock_new_response):
    term = LCTerm(id=heading_id, old_heading="Foo")
    assert term.id == heading_id
    assert term.format == ".skos.json"
    assert term.url == "https://id.loc.gov/authorities/"
    assert term.query == f"{term.url + term.id_type + '/' + heading_id}"
    assert term.current_heading == "Foo"
    assert term.recent_change is False
    assert term.is_deprecated is False
    assert term.revised_heading is False


def test_heading_not_found(mock_error_response):
    term = LCTerm(id="n123", old_heading="n321")
    assert term.skos_json is None
    assert term.is_deprecated is None
    assert term.status_code == 404


def test_fromMarcFile(mock_marc, mock_new_response):
    term = LCTerm.fromMarcFile(record=mock_marc)
    assert term.old_heading == "Bar, Foo"
    assert term.id == "n123456789"
