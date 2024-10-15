import datetime

import pytest
import requests
from pymarc import Record, Field, Subfield


class FakeUtcNow(datetime.datetime):
    @classmethod
    def now(cls, tz=datetime.timezone.utc):
        return cls(2024, 6, 1, 1, 0, 0, 0, datetime.timezone.utc)


class MockLCResponseRevised:
    """Mock response from id.loc.gov for a current term"""

    def __init__(self):
        self.status_code = 200
        self.ok = True

    def json(self):
        change_date = datetime.datetime.strftime(
            (
                datetime.datetime.now(tz=datetime.timezone.utc)
                - datetime.timedelta(days=60)
            ),
            "%Y-%m-%dT%H:%M:%S",
        )
        return [
            {
                "@id": "http://id.loc.gov/authorities/",
                "@type": ["http://www.w3.org/2004/02/skos/core#Concept"],
                "http://www.w3.org/2004/02/skos/core#prefLabel": [
                    {"@language": "en", "@value": "Spam"}
                ],
            },
            {
                "@id": "_:b83iddOtlocdOtgovauthorities",
                "@type": ["http://purl.org/vocab/changeset/schema#ChangeSet"],
                "http://purl.org/vocab/changeset/schema#createdDate": [
                    {"@value": str(change_date)}
                ],
                "http://purl.org/vocab/changeset/schema#changeReason": [
                    {"@value": "revised"}
                ],
            },
            {
                "@id": "_:b83iddOtlocdOtgovauthorities",
                "@type": ["http://purl.org/vocab/changeset/schema#ChangeSet"],
                "http://purl.org/vocab/changeset/schema#createdDate": [
                    {"@value": "2020-04-01T00:00:01"}
                ],
                "http://purl.org/vocab/changeset/schema#changeReason": [
                    {"@value": "new"}
                ],
            },
        ]


class MockLCResponseDeprecated:
    """Mock response from id.loc.gov for a deprecated term"""

    def __init__(self):
        self.status_code = 200
        self.ok = True

    def json(self):
        change_date = datetime.datetime.strftime(
            (
                datetime.datetime.now(tz=datetime.timezone.utc)
                - datetime.timedelta(days=7)
            ),
            "%Y-%m-%dT%H:%M:%S",
        )
        return [
            {
                "@id": "http://id.loc.gov/authorities/",
                "@type": ["http://www.w3.org/2004/02/skos/core#Concept"],
                "http://www.w3.org/2008/05/skos-xl#literalForm": [
                    {"@language": "en", "@value": "Bar"}
                ],
            },
            {
                "@id": "_:b83iddOtlocdOtgovauthorities",
                "@type": ["http://purl.org/vocab/changeset/schema#ChangeSet"],
                "http://purl.org/vocab/changeset/schema#createdDate": [
                    {"@value": str(change_date)}
                ],
                "http://purl.org/vocab/changeset/schema#changeReason": [
                    {"@value": "deprecated"}
                ],
            },
            {
                "@id": "_:b83iddOtlocdOtgovauthorities",
                "@type": ["http://purl.org/vocab/changeset/schema#ChangeSet"],
                "http://purl.org/vocab/changeset/schema#createdDate": [
                    {"@value": "2020-04-01T00:00:01"}
                ],
                "http://purl.org/vocab/changeset/schema#changeReason": [
                    {"@value": "new"}
                ],
            },
        ]


class MockLCResponseNew:
    """Mock response from id.loc.gov for a new term"""

    def __init__(self):
        self.status_code = 200
        self.ok = True

    def json(self):
        create_date = datetime.datetime.strftime(
            datetime.datetime.now(), "%Y-%m-%dT%H:%M:%S"
        )
        return [
            {
                "@id": "http://id.loc.gov/authorities/",
                "@type": ["http://www.w3.org/2004/02/skos/core#Concept"],
                "http://www.w3.org/2008/05/skos-xl#literalForm": [
                    {"@language": "en", "@value": "Foo"}
                ],
            },
            {
                "@id": "_:b83iddOtlocdOtgovauthorities",
                "@type": ["http://purl.org/vocab/changeset/schema#ChangeSet"],
                "http://purl.org/vocab/changeset/schema#createdDate": [
                    {"@value": str(create_date)}
                ],
                "http://purl.org/vocab/changeset/schema#changeReason": [
                    {"@value": "new"}
                ],
            },
        ]


class MockLCResponseError:
    """Simulates auth server response to successful token request"""

    def __init__(self):
        self.status_code = 404
        self.ok = False

    def json(self):
        return {
            "code": 404,
            "message": "Term not found.",
        }


@pytest.fixture
def mock_revised_response(monkeypatch):
    def mock_lc_response(*args, **kwargs):
        return MockLCResponseRevised()

    monkeypatch.setattr(requests, "get", mock_lc_response)
    monkeypatch.setattr(datetime, "datetime", FakeUtcNow)


@pytest.fixture
def mock_deprecated_response(monkeypatch):
    def mock_lc_response(*args, **kwargs):
        return MockLCResponseDeprecated()

    monkeypatch.setattr(requests, "get", mock_lc_response)
    monkeypatch.setattr(datetime, "datetime", FakeUtcNow)


@pytest.fixture
def mock_new_response(monkeypatch):
    def mock_lc_response(*args, **kwargs):
        return MockLCResponseNew()

    monkeypatch.setattr(requests, "get", mock_lc_response)


@pytest.fixture
def mock_error_response(monkeypatch):
    def mock_lc_response(*args, **kwargs):
        return MockLCResponseError()

    monkeypatch.setattr(requests, "get", mock_lc_response)


@pytest.fixture
def mock_marc():
    record = Record()
    record.add_field(
        Field(tag="001", data="n 123456789"),
        Field(
            tag="100",
            indicators=[" ", " "],
            subfields=[Subfield(code="a", value="Bar, Foo")],
        ),
    )
    return record
