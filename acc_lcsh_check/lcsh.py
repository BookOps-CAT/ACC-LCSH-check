import datetime
import requests


class LCTerm:
    def __init__(self, id: str, old_heading: str, id_type: str):
        self.id = id
        self.old_heading = old_heading
        self.id_type = id_type
        self.format = ".skos.json"
        self.url = "https://id.loc.gov/authorities/"

        self.query = f"{self.url + self.id_type + '/' + self.id}"
        self._get_skos_json()
        self._get_current_heading()
        self._get_changes()
        self._compare_headings()

    def _get_skos_json(self):
        skos_json_response = requests.get(f"{self.query + self.format}")
        self.skos_json = skos_json_response.json()
        return self.skos_json

    def _get_current_heading(self):
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
                if change_date >= today - datetime.timedelta(days=30):
                    self.recent_change = True
                else:
                    self.recent_change = False
                if "deprecated" in change["change_reason"]:
                    self.is_deprecated = True
                else:
                    self.is_deprecated = False

    def _compare_headings(self):
        if str(self.current_heading).lower() != str(self.old_heading).lower():
            self.check_heading = True
        else:
            self.check_heading = False
