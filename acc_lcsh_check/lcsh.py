from __future__ import annotations

import datetime
import io
from functools import cached_property

import requests
from pymarc import Record, parse_xml_to_array


class LCTerm:
    """A class that defines a LC subject heading."""

    STATUS = {
        "c": "revised",
        "d": "deprecated",
        "n": "new",
        "o": "deprecated",
        "s": "deprecated",
        "x": "deprecated",
    }

    def __init__(self, id: str, heading: str) -> None:
        self.id = id
        self.heading = heading

    @cached_property
    def marc_xml(self) -> Record | None:
        if self.status_code == 200:
            xml_data = self.xml_response.content
            return parse_xml_to_array(io.BytesIO(xml_data))[0]
        return None

    @cached_property
    def xml_response(self) -> requests.Response:
        """Send request to id.loc.gov and return the response."""
        query = f"https://id.loc.gov/authorities/{self.id_type}/{self.id}.marcxml.xml"
        return requests.get(query, headers={"user-agent": "BookOps-LCSH-checker/0.1"})

    @cached_property
    def status_code(self) -> int:
        return self.xml_response.status_code

    @property
    def change_date(self) -> str | None:
        if self.change_type == "new" or not self.marc_xml:
            return None
        return getattr(self.marc_xml.get("005"), "data", "")

    @property
    def change_type(self) -> str | None:
        if self.marc_xml:
            return self.STATUS[self.marc_xml.leader[5]]
        return None

    @property
    def current_heading(self) -> str | None:
        """
        Parse response from id.loc.gov and get current heading.
        """
        if not self.marc_xml:
            return None
        fields_1xx = [i for i in self.marc_xml.fields if i.tag.startswith("1")]
        return fields_1xx[0]["a"]

    @property
    def deprecated_date(self) -> str | None:
        if self.is_deprecated:
            return self.change_date
        return None

    @property
    def id_type(self) -> str:
        if self.id[:2] == "sh":
            return "subjects"
        elif self.id[:2] == "dg":
            return "demographicTerms"
        elif self.id[:1] == "n":
            return "names"
        else:
            raise ValueError("ID type not recognized.")

    @property
    def is_deprecated(self) -> bool:
        if self.change_type == "deprecated":
            return True
        return False

    @property
    def recent_change(self) -> bool:
        if self.change_type == "new" or not self.change_date:
            return False
        change_datetime = datetime.datetime.strptime(
            self.change_date, "%Y-%m-%dT%H:%M:%S"
        )
        today = datetime.datetime.now()
        if change_datetime >= (today - datetime.timedelta(days=31)):
            return True
        return False

    @property
    def revised_heading(self) -> bool:
        if not self.current_heading:
            return False
        elif str(self.current_heading).lower() != str(self.heading).lower():
            return True
        else:
            return False

    @classmethod
    def fromMarcFile(cls, record: Record) -> LCTerm:
        id = ""
        control_no = record["001"]
        control_no_str = getattr(control_no, "data", "")
        id = control_no_str.replace(" ", "")
        heading_fields = []
        for field in record.fields:
            if field.tag[0:1] == "1":
                heading_fields.append(field.tag)
        tag = str(heading_fields[0])
        heading = record[tag].value()
        return cls(id, heading)
