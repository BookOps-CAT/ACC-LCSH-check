import datetime
import csv
import os
from typing import Generator
from acc_lcsh_check.lcsh import LCTerm


def read_data(file: str) -> Generator:
    with open(file, "r") as csvfile:
        reader = csv.reader(csvfile)
        for item in reader:
            yield item


def delete_old_files(files: list):
    for file in files:
        if os.path.exists(f"{file}"):
            os.remove(f"{file}")


def get_data(infile: str, outpath: str = "data/") -> None:
    today = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
    deprecated_terms = []
    changed_terms = []

    if infile == f"{infile.split('_')[0]}_{today}.txt":
        raise ValueError("Check infile. Filename must not contain today's date.")

    delete_old_files(
        [
            f"{infile.split('_')[0]}_{today}.txt",
            f"{outpath}deprecated_terms_{today}.txt",
            f"{outpath}changed_terms_{today}.txt",
        ]
    )

    for term in read_data(infile):
        loc = LCTerm(id=f"{term[1].strip('" ')}", old_heading=f"{term[0].strip(' "')}")
        print(f"Checking {loc.id}...")
        if loc.is_deprecated is True:
            deprecated_terms.append(loc.id)
        elif loc.check_heading is True:
            changed_terms.append(
                {
                    "id": loc.id,
                    "current_heading": loc.current_heading,
                    "old_heading": loc.old_heading,
                }
            )
        else:
            with open(f"{infile.split('_')[0]}_{today}.txt", "a") as outfile:
                outfile.write(f'"{loc.old_heading}", "{loc.id}"\n')
    if len(deprecated_terms) >= 1:
        with open(f"{outpath}deprecated_terms_{today}.txt", "a") as writer_1:
            for d_term in deprecated_terms:
                writer_1.write(f"{d_term}\n")
        print(f"Deprecated term in: {outpath}deprecated_terms_{today}.txt")
    if len(changed_terms) >= 1:
        with open(f"{outpath}changed_terms_{today}.txt", "a") as writer_2:
            for c_term in changed_terms:
                writer_2.write(f"{c_term}\n")
        print(f"Changed terms in: {outpath}changed_terms_{today}.txt")
