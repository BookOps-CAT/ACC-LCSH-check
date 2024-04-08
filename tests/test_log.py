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


@pytest.mark.parametrize(
    "type",
    ["deprecated", "revised"],
)
def test_rename_files(type, request):
    today = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
    request.getfixturevalue(f"mock_{type}_response")
    logger = LogSession(
        logger_name=f"test_{type}",
        logfile=f"tests/data/test_{type}.log",
        infile=f"tests/data/test_{type}_out.csv",
        outfile=f"tests/data/test_{type}.csv",
    )
    logger.run_logger()
    logger.rename_files()
    assert os.path.isfile(f"tests/data/test_{type}_out_{today}.csv") is True
