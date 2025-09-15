import datetime
import os

import pandas as pd
import pytest
import requests
from pymarc import Field, Record, Subfield


class FakeUtcNow(datetime.datetime):
    @classmethod
    def now(cls, tz=datetime.timezone.utc):
        return cls(2024, 6, 1, 1, 0, 0, 0, datetime.timezone.utc)


@pytest.fixture
def mock_now(monkeypatch) -> None:
    monkeypatch.setattr(datetime, "datetime", FakeUtcNow)


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
def mock_revised_response(monkeypatch, mock_now):
    def mock_lc_response(*args, **kwargs):
        return MockLCResponseRevised()

    monkeypatch.setattr(requests, "get", mock_lc_response)


@pytest.fixture
def mock_deprecated_response(monkeypatch, mock_now):
    def mock_lc_response(*args, **kwargs):
        return MockLCResponseDeprecated()

    monkeypatch.setattr(requests, "get", mock_lc_response)


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


class MockCreds:
    def __init__(self):
        self.token = "foo"
        self.refresh_token = "bar"

    @property
    def valid(self, *args, **kwargs):
        return True

    @property
    def expired(self, *args, **kwargs):
        return False

    def refresh(self, *args, **kwargs):
        self.expired = False
        self.valid = True

    def to_json(self, *args, **kwargs):
        pass

    def run_local_server(self, *args, **kwargs):
        return self


@pytest.fixture
def mock_open_file(mocker) -> None:
    token = """{"token": "foo","refresh_token": "bar","token_uri": "baz","client_id": "foo","client_secret": "bar","universe_domain": "foo","account": "bar","expiry": "2025-01-06T15:53:41.298707Z"}"""
    m = mocker.mock_open(read_data=token)
    mocker.patch("acc_lcsh_check.backstage_utils.open", m)
    mocker.patch.dict(os.environ, {"USERPROFILE": "test"})
    mocker.patch("os.path.exists", lambda *args, **kwargs: True)


@pytest.fixture
def mock_read_csv(monkeypatch) -> None:
    def mock_df(*args, **kwargs):
        return pd.DataFrame(
            data={
                "RECORD_NUMBER": ["123"],
                "LCCN": ["20251234567890"],
                "heading1": ["FOO"],
                "heading2": ["BAR"],
                "heading3": ["BAZ"],
            }
        )
    def mock_to_csv(*args, **kwargs):
        return None   

    monkeypatch.setattr(pd, "read_csv", mock_df)
    monkeypatch.setattr("pandas.DataFrame.to_csv", mock_to_csv)    
    monkeypatch.setattr("os.path.exists", lambda *args, **kwargs: False)


@pytest.fixture
def mock_read_csv_exists(monkeypatch) -> None:
    def mock_df(*args, **kwargs):
        return pd.DataFrame(
            data={
                "RECORD_NUMBER": ["123"],
                "LCCN": ["20251234567890"],
                "NORMALIZED_LCCN": ["FOO"],
                "HEADING_FROM_MARC_FILE": ["BAR"],
            }
        )

    monkeypatch.setattr(pd, "read_csv", mock_df)
    monkeypatch.setattr("os.path.exists", lambda *args, **kwargs: True)


@pytest.fixture
def mock_sheet_config(monkeypatch, mock_open_file):
    def build_sheet(*args, **kwargs):
        return MockResource()

    monkeypatch.setattr("googleapiclient.discovery.build", build_sheet)
    monkeypatch.setattr("googleapiclient.discovery.build_from_document", build_sheet)
    monkeypatch.setattr(
        "google.oauth2.credentials.Credentials.from_authorized_user_info",
        lambda *args, **kwargs: MockCreds(),
    )
    monkeypatch.setattr("acc_lcsh_check.backstage_utils.load_creds", lambda *args: None)
    monkeypatch.setenv("GOOGLE_SHEET_TOKEN", "foo")
    monkeypatch.setenv("GOOGLE_SHEET_REFRESH_TOKEN", "bar")
    monkeypatch.setenv("GOOGLE_SHEET_CLIENT_ID", "baz")
    monkeypatch.setenv("GOOGLE_SHEET_CLIENT_SECRET", "qux")


@pytest.fixture
def mock_sheet_config_expired_creds(monkeypatch, mock_sheet_config):
    monkeypatch.setattr(MockCreds, "valid", False)
    monkeypatch.setattr(MockCreds, "expired", True)


@pytest.fixture
def mock_sheet_config_no_creds(monkeypatch, mock_sheet_config):
    monkeypatch.setattr(
        "google_auth_oauthlib.flow.InstalledAppFlow.from_client_config",
        lambda *args, **kwargs: MockCreds(),
    )
    monkeypatch.setattr(
        "google.oauth2.credentials.Credentials.from_authorized_user_info",
        lambda *args, **kwargs: None,
    )


@pytest.fixture
def mock_sheet_config_invalid_creds(monkeypatch, mock_sheet_config):
    def mock_error(*args, **kwargs):
        raise ValueError

    monkeypatch.setattr(
        "google.oauth2.credentials.Credentials.from_authorized_user_info", mock_error
    )


class MockResource:
    def __init__(self):
        self.spreadsheetId = "foo"
        self.range = "bar"

    def append(self, *args, **kwargs):
        return self

    def execute(self, *args, **kwargs):
        return dict(spreadsheetId=self.spreadsheetId, tableRange=self.range)

    def spreadsheets(self, *args, **kwargs):
        return self

    def values(self, *args, **kwargs):
        return self


@pytest.fixture
def mock_sheet_timeout_error(monkeypatch):
    def mock_error(*args, **kwargs):
        raise TimeoutError

    monkeypatch.setattr("googleapiclient.discovery.build", mock_error)
    monkeypatch.setattr("googleapiclient.discovery.build_from_document", mock_error)
