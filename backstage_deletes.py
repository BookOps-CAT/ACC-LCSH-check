import sys
import time

import pandas as pd

from acc_lcsh_check.backstage_utils import (
    get_batches,
    process_csv,
    write_delete_sheet,
)
from acc_lcsh_check.lcsh import LCTerm


def get_lc_results(row: pd.Series) -> list[str]:
    term = LCTerm(row.iloc[2], row.iloc[3])
    out = [
        row.iloc[0],
        row.iloc[1],
        term.id,
        term.heading,
        term.is_deprecated,
        term.status_code,
        term.current_heading,
    ]
    return out


def run(file: str, first_rec: str = "0") -> None:
    df = process_csv(file)
    batches = get_batches(df, int(first_rec))
    columns = [
        "RECORD_NUMBER",
        "LCCN",
        "NORMALIZED_LCCN",
        "HEADING_FROM_MARC_FILE",
        "IS_DEPRECATED",
        "STATUS_CODE",
        "HEADING_FROM_LC",
    ]

    for part in batches:
        chunk = df.loc[part[0] : part[1]]  # noqa: E203
        start = time.time()
        out = pd.DataFrame(data=None, columns=columns)
        out = chunk.apply(get_lc_results, axis=1).apply(pd.Series)

        out["COUNT"] = out.index.to_series().apply(lambda x: f"{x} of {len(df)}")
        record_count = out.pop("COUNT")
        out.insert(0, "COUNT", record_count)
        end = time.time()
        df.fillna("", inplace=True)
        write_delete_sheet(out, "1ljT9VxzdhuKHuYp9MhfOLcPxqfF6VgstKMSQgRELm-M")
        print(f"Records {part[0]} to {part[1]} took {end - start} seconds to run.")


if __name__ in "__main__":
    try:
        run(sys.argv[1], sys.argv[2])
    except IndexError:
        print("Invalid input. Provide filename and last row checked.")
