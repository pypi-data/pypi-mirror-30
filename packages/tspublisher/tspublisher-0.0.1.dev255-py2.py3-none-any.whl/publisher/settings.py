import os
import platform
import tempfile

os_platform = platform.system().lower()

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "../../tests/sample_data")

PRODUCTION_INFO_DIR = os.path.join(SAMPLE_DATA_DIR, "production_info")
STUDIO_GIT_DIR = tempfile.mkdtemp()
CHANNELS_GIT_DIR = os.path.join(SAMPLE_DATA_DIR, "channels")

TS_ENCYCLOPEDIA_DIR = os.path.join(SAMPLE_DATA_DIR, "content", "tsencyclopedia")

# if platform.system() == "Windows":
#     TS_ENCYCLOPEDIA_DIR = os.path.join("C:\\", "Touchsurgery", "tsencyclopedia")
# else:
#     TS_ENCYCLOPEDIA_DIR = os.path.join("/Volumes", "content", "tsencyclopedia")

ENCYCLOPEDIA_YAML_DIR = os.path.join(TS_ENCYCLOPEDIA_DIR, "yaml", "moreInfo")
ENCYCLOPEDIA_OVERVIEW_YAML_DIR = os.path.join(TS_ENCYCLOPEDIA_DIR, "yaml", "overview")
ENCYCLOPEDIA_DEVICES_YAML_DIR = os.path.join(TS_ENCYCLOPEDIA_DIR, "yaml", "devices")
ENCYCLOPEDIA_EULA_DIR = os.path.join(TS_ENCYCLOPEDIA_DIR, "eula")
ENCYCLOPEDIA_THUMBNAILS_DIR = os.path.join(TS_ENCYCLOPEDIA_DIR, "thumbnails")

CONTENT_DB_DIR = os.path.join(SAMPLE_DATA_DIR, "contentdb", "contentdb.sqlite3")

# these are used to convert file paths from content db to current system format.
WINDOWS_CONTENT_READ_ROOT = "C:/TouchSurgery/assetdb/vault2"
MAC_CONTENT_READ_ROOT = SAMPLE_DATA_DIR
WINDOWS_CONTENT_READ_ROOT_OLD = "C:/TouchSurgery/assetdb"
MAC_CONTENT_READ_ROOT_OLD = SAMPLE_DATA_DIR

DELIVERY_ROOT = os.path.join(SAMPLE_DATA_DIR, "delivery")

# WINDOWS_CONTENT_READ_ROOT = "C:/TouchSurgery/assetdb/vault2"
# MAC_CONTENT_READ_ROOT = "/Volumes/content/assetdb/vault2"
# WINDOWS_CONTENT_READ_ROOT_OLD = "C:/TouchSurgery/assetdb"
# MAC_CONTENT_READ_ROOT_OLD = "/Volumes/content/assetdb"

# if os_platform == "Windows":
#     DELIVERY_ROOT = "C:/Touchsurgery/delivery/"
# else:
#     DELIVERY_ROOT = "/Volumes/content/delivery/"
