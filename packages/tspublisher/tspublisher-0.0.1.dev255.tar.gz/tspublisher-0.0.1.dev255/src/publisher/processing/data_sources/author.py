import os

from publisher.processing.data_sources.utils import read_csv_file


def get_author_from_db(procedure_code):
    author_csv = os.path.join(os.path.dirname(__file__), "data", "authorList.csv")

    headers, rows = read_csv_file(author_csv, delimiter='|')

    authors = ""

    for row in rows:
        if row["procCode"] == procedure_code:
            authors = row["authors"].replace("~", ", ")

    if not authors:
        print "Procedure %s either has no author or is not in Authors List" % procedure_code

    return authors
