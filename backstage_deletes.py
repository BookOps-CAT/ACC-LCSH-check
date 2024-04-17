from pymarc import MARCReader
from acc_lcsh_check.lcsh import LCTerm
from acc_lcsh_check.sheet import write_delete_sheet

if __name__ in "__main__":
    file_list = [
        "SUBJ-Q-230627DEL.MRC",
        "NAME-DEL-Q-230926.MRC",
        "NAME-Q-230627DEL.MRC",
    ]
    id_list = []
    for file in file_list:
        print(file)
        with open(f"data/backstage/{file}", "rb") as fh:
            reader = MARCReader(fh)
            for record in reader:
                control_no = record["001"].data
                record_id = control_no.replace(" ", "")
                heading_fields = []
                for field in record.fields:
                    if field.tag[0:1] == "1":
                        heading_fields.append(field.tag)
                if len(heading_fields) == 1:
                    tag = str(heading_fields[0])
                    record_heading = record[tag].value()
                id_list.append(
                    (
                        record_id,
                        record_heading,
                        file,
                    )
                )
    with open("data/backstage_out.csv", "a") as outfile:
        for item in id_list:
            outfile.write(f"{item[0]}\n")
    print(len(id_list))
    for item in id_list:
        term = LCTerm(item[0], item[1])
        out_data = [
            [
                item[2],
                term.id,
                term.old_heading,
                term.is_deprecated,
                term.status_code,
                term.current_heading,
            ]
        ]
        print(out_data)
        write_delete_sheet(
            "1ljT9VxzdhuKHuYp9MhfOLcPxqfF6VgstKMSQgRELm-M",
            "Headings!A1:D100000",
            "USER_ENTERED",
            "INSERT_ROWS",
            out_data,
        )
