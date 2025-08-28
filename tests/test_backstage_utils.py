import os

import pandas as pd
import pytest

from acc_lcsh_check.backstage_utils import (
    configure_sheet,
    get_batches,
    get_date,
    load_creds,
    process_csv,
    write_delete_sheet,
)


def test_configure_sheet_success(mock_sheet_config):
    creds = configure_sheet()
    assert creds.token == "foo"
    assert creds.valid is True
    assert creds.expired is False
    assert creds.refresh_token is not None


def test_configure_sheet_expired(mock_sheet_config_expired_creds):
    creds = configure_sheet()
    assert creds.token == "foo"
    assert creds.valid is True
    assert creds.expired is False
    assert creds.refresh_token is not None


def test_configure_sheet_generate_new_creds(mock_sheet_config_no_creds):
    creds = configure_sheet()
    assert creds.token == "foo"
    assert creds.valid is True
    assert creds.expired is False
    assert creds.refresh_token is not None


def test_configure_sheet_no_creds(mock_sheet_config_no_creds):
    creds = configure_sheet()
    assert creds.token == "foo"
    assert creds.valid is True
    assert creds.expired is False
    assert creds.refresh_token is not None


def test_configure_sheet_invalid_creds(mock_sheet_config_invalid_creds):
    with pytest.raises(ValueError):
        configure_sheet()


@pytest.mark.parametrize("range_count, batch_count", [(101, 2), (201, 3), (500, 5)])
def test_get_batches(range_count, batch_count):
    df = pd.DataFrame(data={"col1": [i + 1 for i in range(range_count)]})
    batches = get_batches(df)
    assert len(batches) == batch_count


def test_get_date(mock_now):
    today = get_date()
    assert today == "240601"


def test_load_creds(mock_open_file):
    load_creds()
    assert os.environ["token"] == "foo"
    assert os.environ["refresh_token"] == "bar"
    assert os.environ["token_uri"] == "baz"
    assert os.environ["client_id"] == "foo"
    assert os.environ["client_secret"] == "bar"
    assert os.environ["universe_domain"] == "foo"
    assert os.environ["account"] == "bar"
    assert os.environ["expiry"] == "2025-01-06T15:53:41.298707Z"


def test_process_csv(mock_read_csv, mock_now):
    data = process_csv("data/backstage/Q_12-31review.txt")
    assert sorted(list(data.columns)) == sorted(
        [
            "RECORD_NUMBER",
            "LCCN",
            "NORMALIZED_LCCN",
            "HEADING_FROM_MARC_FILE",
        ]
    )


def test_process_csv_exists(mock_read_csv_exists, mock_now):
    data = process_csv("data/backstage/Q_12-31review.txt")
    assert sorted(list(data.columns)) == sorted(
        [
            "RECORD_NUMBER",
            "LCCN",
            "NORMALIZED_LCCN",
            "HEADING_FROM_MARC_FILE",
        ]
    )


def test_write_delete_sheet(mock_sheet_config):
    mock_data = {"file_name": ["foo.mrc"], "vendor_code": ["FOO"]}
    data = write_delete_sheet(
        data=pd.DataFrame(data=mock_data),
        spreadsheet_id="1hGzVYaqxXXBSJa3GY52UFKteZgLoWBo6X0sGsTVTpFU",
    )
    keys = data.keys()
    assert sorted(list(keys)) == sorted(["spreadsheetId", "tableRange"])


def test_write_delete_sheet_timeout_error(mock_sheet_config, mock_sheet_timeout_error):
    mock_data = {"file_name": ["foo.mrc"], "vendor_code": ["FOO"]}
    with pytest.raises(TimeoutError):
        write_delete_sheet(
            data=pd.DataFrame(data=mock_data),
            spreadsheet_id="1hGzVYaqxXXBSJa3GY52UFKteZgLoWBo6X0sGsTVTpFU",
        )
