import pytest

from acc_lcsh_check.lcsh import LCTerm


@pytest.mark.parametrize(
    "heading_id, heading_type, heading_str",
    [
        ("111", "subjects", "foo"),
        ("222", "names", "bar"),
        ("333", "demographicTerms", "baz"),
    ],
)
def test_current_term(
    heading_id, heading_str, heading_type, mock_changed_skos_json_response
):
    term = LCTerm(id=heading_id, old_heading=heading_str, id_type=heading_type)
    assert term.id == heading_id
    assert term.old_heading == heading_str
    assert term.id_type == heading_type
    assert term.format == ".skos.json"
    assert term.url == "https://id.loc.gov/authorities/"
    assert term.query == f"{term.url + heading_type + '/' + heading_id}"
    assert term.current_heading == "Spam"
    assert term.changes[0] == {
        "change_reason": "revised",
        "change_date": "2024-04-01T00:00:01",
    }
    assert term.recent_change is True
    assert term.is_deprecated is False
    assert term.check_heading is True


@pytest.mark.parametrize(
    "heading_id, heading_type",
    [
        ("111", "subjects"),
        ("222", "names"),
        ("333", "demographicTerms"),
    ],
)
def test_deprecated_term(heading_id, heading_type, mock_deprecated_skos_json_response):
    term = LCTerm(id=heading_id, old_heading="Foo", id_type=heading_type)
    assert term.id == heading_id
    assert term.id_type == heading_type
    assert term.format == ".skos.json"
    assert term.url == "https://id.loc.gov/authorities/"
    assert term.query == f"{term.url + heading_type + '/' + heading_id}"
    assert term.current_heading == "Bar"
    assert term.changes[0] == {
        "change_reason": "deprecated",
        "change_date": "2023-04-01T00:00:01",
    }
    assert term.recent_change is False
    assert term.is_deprecated is True
    assert term.check_heading is True


@pytest.mark.parametrize(
    "heading_id, heading_type",
    [
        ("111", "subjects"),
        ("222", "names"),
        ("333", "demographicTerms"),
    ],
)
def test_new_term(heading_id, heading_type, mock_new_skos_json_response):
    term = LCTerm(id=heading_id, old_heading="Foo", id_type=heading_type)
    assert term.id == heading_id
    assert term.id_type == heading_type
    assert term.format == ".skos.json"
    assert term.url == "https://id.loc.gov/authorities/"
    assert term.query == f"{term.url + heading_type + '/' + heading_id}"
    assert term.current_heading == "Foo"
    assert term.recent_change is False
    assert term.is_deprecated is False
    assert term.check_heading is False
