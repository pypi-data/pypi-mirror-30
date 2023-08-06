import sqlite3
from platform import platform

from publisher import settings
from publisher.settings import WINDOWS_CONTENT_READ_ROOT, MAC_CONTENT_READ_ROOT, WINDOWS_CONTENT_READ_ROOT_OLD, \
    MAC_CONTENT_READ_ROOT_OLD


def get_csv_steps_file(phase_code):
    c = sqlite3.connect(settings.CONTENT_DB_DIR)
    cursor = c.execute("""
        SELECT f.file_path FROM assetdb_asset a
        INNER JOIN assetdb_assetversion v ON a.id = v.asset_id
        INNER JOIN assetdb_assetfile f ON v.id = f.asset_version_id
        WHERE
            a.category = 'Admin' AND
            a."name" = 'Main' AND
            a."level_of_detail" = 'default' AND
            a."variant" = 'default' AND
            a."module" = ? AND
            a."asset_type" = 'csvSteps' AND
            a."department" = 'default' AND
            a."operation" IS NULL AND
            a."institution" = 'TouchSurgeryContent' AND
            a."stage" = 'default' AND
            NOT a.deprecated AND
            NOT v."pending" AND
            NOT v."deprecated" AND
            NOT f."pending" AND
            NOT f."deprecated" AND
            f."name" = 'default'
        ORDER BY v."version" DESC LIMIT 1;""", (phase_code,))

    row = cursor.fetchone()
    c.close()

    return _get_platform_specific_path(row[0].strip()) if row else None


def _get_platform_specific_path(file_path):
    if "windows" not in platform().lower():
        if WINDOWS_CONTENT_READ_ROOT in file_path:
            return file_path.replace("\\", "/").replace(WINDOWS_CONTENT_READ_ROOT, MAC_CONTENT_READ_ROOT, 1)
        else:
            return file_path.replace("\\", "/").replace(WINDOWS_CONTENT_READ_ROOT_OLD, MAC_CONTENT_READ_ROOT_OLD, 1)
    return file_path.replace("\\", "/")
