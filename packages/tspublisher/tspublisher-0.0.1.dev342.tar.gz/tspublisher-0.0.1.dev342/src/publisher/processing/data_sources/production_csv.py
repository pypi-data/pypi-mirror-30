import os

from publisher import settings
from publisher.processing.data_sources.utils import read_csv_file


def get_procedure_details(procedure_code, production_data):

    procedure_row = next((r for r in production_data if is_procedure_row(procedure_code, r)), None)
    if not procedure_row:
        raise EOFError("Could not find Procedure: %s in production csv." % procedure_code)

    procedure_name = procedure_row["Procedure Name"] or "%s - UNKNOWN" % procedure_code
    specialties = procedure_row["Speciality"].split("~") if procedure_row["Speciality"] else []
    channel = procedure_row["Channel"]

    return procedure_name, specialties, channel


def get_procedure_phase_list(procedure_code, production_data):
    def get_phase_details(r):
        return {"phase_code": r["Name"], "released_as": r["Released As"], 'phase_name': r['Module Name']}

    return map(get_phase_details, filter(lambda r: is_procedure_row(procedure_code, r), production_data))


def is_procedure_row(procedure_code, r):
    return r["Procedure Group"] == procedure_code and r["Status"] != "RETIRED"


def get_production_csv_data():
    module_csv = os.path.join(settings.PRODUCTION_INFO_DIR, "module.csv")
    headers, rows = read_csv_file(module_csv, delimiter='|')
    return rows
