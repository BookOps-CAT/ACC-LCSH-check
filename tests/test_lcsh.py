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
        heading=heading_str,
    )
    assert term.id == heading_id
    assert term.heading == heading_str
    assert term.marc_xml is not None
    assert term.status_code == 200
    assert term.change_date == "2024-04-02T01:00:00"
    assert term.change_type == "revised"
    assert term.current_heading == "Spam"
    assert term.deprecated_date is None
    assert term.is_deprecated is False
    assert term.recent_change is False
    assert term.revised_heading is True


@pytest.mark.parametrize(
    "heading_id",
    ["sh111", "na222", "dg333"],
)
def test_deprecated_term(heading_id, mock_deprecated_response):
    term = LCTerm(id=heading_id, heading="Foo")
    assert term.id == heading_id
    assert term.marc_xml is not None
    assert term.current_heading == "Bar"
    assert term.change_date == "2024-05-25T01:00:00"
    assert term.change_type == "deprecated"
    assert term.deprecated_date == "2024-05-25T01:00:00"
    assert term.is_deprecated is True
    assert term.recent_change is True
    assert term.revised_heading is True


@pytest.mark.parametrize(
    "heading_id",
    ["sh111", "na222", "dg333"],
)
def test_new_term(heading_id, mock_new_response):
    term = LCTerm(id=heading_id, heading="Foo")
    assert term.id == heading_id
    assert term.marc_xml is not None
    assert term.change_date is None
    assert term.change_type == "new"
    assert term.current_heading == "Foo"
    assert term.deprecated_date is None
    assert term.is_deprecated is False
    assert term.recent_change is False
    assert term.revised_heading is False


def test_heading_not_found(mock_error_response):
    term = LCTerm(id="n123", heading="n321")
    assert term.marc_xml is None
    assert term.status_code == 404
    assert term.change_date is None
    assert term.change_type is None
    assert term.current_heading is None
    assert term.deprecated_date is None
    assert term.id_type == "names"
    assert term.is_deprecated is False
    assert term.recent_change is False
    assert term.revised_heading is False


def test_fromMarcFile(mock_marc, mock_new_response):
    term = LCTerm.fromMarcFile(record=mock_marc)
    assert term.heading == "Bar, Foo"
    assert term.id == "n123456789"


def test_invalid_id(mock_new_response):
    term = LCTerm(id="foo123", heading="Foo")
    with pytest.raises(ValueError) as exc:
        term.id_type
    assert str(exc.value) == "ID type not recognized."


@pytest.mark.livetest
def test_lc_term_live():
    term = LCTerm(
        id="sh96000082",
        heading="Manic-depressive persons",
    )
    assert term.id == "sh96000082"
    assert term.heading == "Manic-depressive persons"
    assert term.marc_xml["150"].format_field() == "People with bipolar disorder"
    assert term.current_heading == "People with bipolar disorder"
    assert len(term.changes) == 2
    assert term.changes[0] == {
        "change_reason": "new",
        "change_date": "1996-01-04T00:00:00",
    }
    assert term.changes[1] == {
        "change_reason": "revised",
        "change_date": "2022-11-14T11:33:07",
    }
    assert term.recent_change is False
    assert term.is_deprecated is False
    assert term.revised_heading is True
