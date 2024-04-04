import datetime

import pytest
import requests


class MockLCResponseChanged:
    """Mock response from id.loc.gov for a current term"""

    def __init__(self):
        self.status_code = 200

    def json(self):
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
                    {"@value": "2024-04-01T00:00:01"}
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

    def json(self):
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
                    {"@value": "2023-04-01T00:00:01"}
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

    def json(self):
        change_date = datetime.datetime.strftime(
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
                    {"@value": str(change_date)}
                ],
                "http://purl.org/vocab/changeset/schema#changeReason": [
                    {"@value": "new"}
                ],
            },
        ]


@pytest.fixture
def mock_changed_skos_json_response(monkeypatch):
    def mock_lc_response(*args, **kwargs):
        return MockLCResponseChanged()

    monkeypatch.setattr(requests, "get", mock_lc_response)


@pytest.fixture
def mock_deprecated_skos_json_response(monkeypatch):
    def mock_lc_response(*args, **kwargs):
        return MockLCResponseDeprecated()

    monkeypatch.setattr(requests, "get", mock_lc_response)


@pytest.fixture
def mock_new_skos_json_response(monkeypatch):
    def mock_lc_response(*args, **kwargs):
        return MockLCResponseNew()

    monkeypatch.setattr(requests, "get", mock_lc_response)
