import os

import shutil

from publisher import settings


def copy_eula_to_procedure(procedure_code, asset_directory):
    eula_file_name = "{0}_eula".format(procedure_code)
    source_file_path = os.path.join(settings.ENCYCLOPEDIA_EULA_DIR, eula_file_name + ".txt")
    dest_file_path = os.path.join(asset_directory, eula_file_name + ".txt")

    for _, _, eula_files in os.walk(settings.ENCYCLOPEDIA_EULA_DIR):
        for eula_file in eula_files:
            if procedure_code in eula_file:
                shutil.copyfile(source_file_path, dest_file_path)
                return eula_file_name

    return ""
