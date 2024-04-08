import datetime
import os
import pytest
from acc_lcsh_check.log import LogSession


@pytest.mark.parametrize(
    "type, output",
    [
        ("new", "No changes to ACC terms this month."),
        ("deprecated", "DEBUG - Deprecated terms to check: ['sh00000000']"),
        ("revised", "DEBUG - Revised terms to check: ['sh00000000']"),
    ],
)
def test_logger(type, output, request):
    today = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
    if os.path.exists(f"tests/data/test_{type}.log"):
        os.remove(f"tests/data/test_{type}.log")
    request.getfixturevalue(f"mock_{type}_response")
    logger = LogSession(
        logger_name=f"test_{type}",
        logfile=f"tests/data/test_{type}.log",
        infile="tests/data/test_in.csv",
        outfile=f"tests/data/test_{type}_out.csv",
    )
    logger.run_logger()
    with open(f"tests/data/test_{type}.log", "r") as outfile:
        reader = outfile.readlines()
        assert output in reader[-2]
        assert today in reader[-2]


def test_rename_files_new(mock_new_response):
    today = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
    logger = LogSession(
        logger_name="test_new",
        logfile="tests/data/test_new.log",
        infile="tests/data/test_new_out.csv",
        outfile="tests/data/test_rename.csv",
    )
    logger.run_logger()
    logger.rename_files()
    assert os.path.isfile(f"tests/data/test_new_out_{today}.csv") is False


def test_rename_files(mock_revised_response):
    today = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
    logger = LogSession(
        logger_name="test_rename",
        logfile="tests/data/test_rename.log",
        infile="tests/data/test_new_out.csv",
        outfile="tests/data/test_rename.csv",
    )
    logger.run_logger()
    logger.rename_files()
    assert len(logger.session_data["revised_terms"]) > 0
    assert os.path.isfile(f"tests/data/test_new_out_{today}.csv") is True
