import csv
import datetime
import logging
import logging.handlers
import os

from acc_lcsh_check.lcsh import LCTerm


class LogSession:
    def __init__(self, logger_name: str, logfile: str, infile: str, outfile: str):
        self.logger_name = logger_name
        self.logfile = logfile
        self.infile = infile
        self.outfile = outfile
        self.logger = logging.getLogger(logger_name)
        self.logger_handler = logging.handlers.RotatingFileHandler(
            logfile, encoding="utf-8", delay=True
        )
        self.formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        self.logger_handler.setFormatter(self.formatter)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.logger_handler)
        self._check_terms()

    def _check_terms(self) -> dict[str, list[str]]:
        deprecated_terms: list[str] = []
        revised_terms: list[str] = []
        current_terms: list[str] = []

        with open(self.infile, "r") as csvfile:
            reader = csv.reader(csvfile)
            for term in reader:
                loc = LCTerm(
                    id=str(term[1].strip('" ')), heading=str(term[0].strip(' "'))
                )
                if loc.is_deprecated is True:
                    deprecated_terms.append(loc.id)
                elif loc.revised_heading is True:
                    revised_terms.append(loc.id)
                else:
                    current_terms.append(f'"{loc.heading}", "{loc.id}"')
        self.session_data = {
            "deprecated_terms": deprecated_terms,
            "revised_terms": revised_terms,
            "current_terms": current_terms,
        }
        return self.session_data

    def run_logger(self) -> None:
        if os.path.exists(f"{self.outfile}"):
            os.remove(f"{self.outfile}")

        with open(self.outfile, "a") as out:
            for term in self.session_data["current_terms"]:
                out.write(f"{term}\n")

        self.logger.info("Checking id.loc.gov")
        revised = self.session_data["revised_terms"]
        deprecated = self.session_data["deprecated_terms"]
        if len(deprecated) == 0 and len(revised) == 0:
            self.logger.info("No changes to ACC terms this month.")
        if len(revised) > 0:
            self.logger.debug(f"Revised terms to check: {revised}")
        if len(deprecated) > 0:
            self.logger.debug(f"Deprecated terms to check: {deprecated}")
        self.logger.info(f"Updated list of current terms is in {self.outfile}")

    def rename_files(self) -> None:
        today = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
        if os.path.exists(f"{self.infile.split('.')[0]}_{today}.csv"):
            os.remove(f"{self.infile.split('.')[0]}_{today}.csv")
        if (
            len(self.session_data["deprecated_terms"]) == 0
            and len(self.session_data["revised_terms"]) == 0
        ):
            os.remove(self.infile)
        else:
            os.rename(self.infile, f"{self.infile.split('.')[0]}_{today}.csv")
        os.rename(self.outfile, f"{self.infile}")
