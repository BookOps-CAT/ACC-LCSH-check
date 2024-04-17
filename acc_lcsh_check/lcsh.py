import datetime
import requests
from pymarc import Record


class LCTerm:
    """
    A class that defines a LC subject heading.
    """

    def __init__(self, id: str, old_heading: str) -> None:
        self.id = id
        self.old_heading = old_heading
        self.format = ".skos.json"
        self.url = "https://id.loc.gov/authorities/"

        self._get_id_type()

        self.query = f"{self.url + self.id_type + '/' + self.id}"

        self._get_skos_json()
        if self.status_code == 200:
            self._get_current_heading()
            self._get_changes()
            self._compare_headings()
        else:
            self.skos_json = None
            self.current_heading = None
            self.changes = None
            self.recent_change = None
            self.is_deprecated = None
            self.deprecated_date = None
            self.revised_heading = None

    def _get_id_type(self):
        if self.id[:2] == "sh":
            self.id_type = "subjects"
        elif self.id[:2] == "dg":
            self.id_type = "demographicTerms"
        elif self.id[:1] == "n":
            self.id_type = "names"

    def _get_skos_json(self):
        """
        Send request to id.loc.gov and get the response in .skos.json format.
        """
        skos_json_response = requests.get(f"{self.query + self.format}")
        if skos_json_response.ok is True:
            self.skos_json = skos_json_response.json()
        self.status_code = skos_json_response.status_code

    def _get_current_heading(self):
        """
        Parse response from id.loc.gov and get current heading.
        """
        for item in self.skos_json:
            if "id.loc.gov/authorities/" in item["@id"]:
                if "http://www.w3.org/2004/02/skos/core#prefLabel" in item:
                    self.current_heading = item[
                        "http://www.w3.org/2004/02/skos/core#prefLabel"
                    ][0]["@value"]
                else:
                    self.current_heading = item[
                        "http://www.w3.org/2008/05/skos-xl#literalForm"
                    ][0]["@value"]

    def _get_changes(self):
        """
        Parse response from id.loc.gov and determine if record has been changed
        in last month or if it is deprecated.
        """
        today = datetime.datetime.now()
        self.changes = []
        for item in self.skos_json:
            if "http://purl.org/vocab/changeset/schema#ChangeSet" in item["@type"][0]:
                self.changes.append(
                    {
                        "change_reason": (
                            item["http://purl.org/vocab/changeset/schema#changeReason"][
                                0
                            ]["@value"]
                        ),
                        "change_date": (
                            item["http://purl.org/vocab/changeset/schema#createdDate"][
                                0
                            ]["@value"]
                        ),
                    }
                )
            revisions = [c for c in self.changes if c["change_reason"] != "new"]
            if revisions == []:
                self.recent_change = False
                self.is_deprecated = False
            for change in revisions:
                change_date = datetime.datetime.strptime(
                    change["change_date"], "%Y-%m-%dT%H:%M:%S"
                )
                if change_date >= today - datetime.timedelta(days=31):
                    self.recent_change = True
                else:
                    self.recent_change = False
                if "deprecated" in change["change_reason"]:
                    self.is_deprecated = True
                    self.deprecated_date = change_date
                else:
                    self.is_deprecated = False
                    self.deprecated_date = None

    def _compare_headings(self):
        """
        Sometimes headings are marked as revised in id.loc.gov without changing the
        heading. This function checks if the heading is the same as the ACC term.
        """
        if str(self.current_heading).lower() != str(self.old_heading).lower():
            self.revised_heading = True
        else:
            self.revised_heading = False

    @classmethod
    def fromMarcFile(cls, record: Record):
        control_no = record["001"].data
        id = control_no.replace(" ", "")
        heading_fields = []
        for field in record.fields:
            if field.tag[0:1] == "1":
                heading_fields.append(field.tag)
        if len(heading_fields) == 1:
            tag = str(heading_fields[0])
            old_heading = record[tag].value()
            return cls(id, old_heading)
