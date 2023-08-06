import os
import platform

GIT_DIRECTORY = os.path.expanduser("~/git")
PROCEDURE_CHECKOUT_DIRECTORY = os.path.expanduser("~/git/content-procedures")
CHANNELS_CHECKOUT_DIRECTORY = os.path.expanduser("~/git/content-channels")
PROCEDURE_REPOSITORY = 'studio-git.touchsurgery.com:/srv/git/procedure-repo'
CHANNELS_REPOSITORY = 'studio-git.touchsurgery.com:/srv/git/channel-repo'
SSH_CONFIG_PATH = os.path.expanduser("~/.ssh/config")

if platform.system() == "Windows":
    BASE_DATA_DIR = os.path.join("C:\\", "Touchsurgery")
else:
    BASE_DATA_DIR = os.path.join("/Volumes", "content")

PRODUCTION_INFO_DIR = os.path.join(BASE_DATA_DIR, "productionInfo")
TS_ENCYCLOPEDIA_DIR = os.path.join(BASE_DATA_DIR, "tsencyclopedia")
ENCYCLOPEDIA_YAML_DIR = os.path.join(TS_ENCYCLOPEDIA_DIR, "yaml", "moreInfo")
ENCYCLOPEDIA_OVERVIEW_YAML_DIR = os.path.join(TS_ENCYCLOPEDIA_DIR, "yaml", "overview")
ENCYCLOPEDIA_DEVICES_YAML_DIR = os.path.join(TS_ENCYCLOPEDIA_DIR, "yaml", "devices")
ENCYCLOPEDIA_EULA_DIR = os.path.join(TS_ENCYCLOPEDIA_DIR, "eula")
ENCYCLOPEDIA_THUMBNAILS_DIR = os.path.join(TS_ENCYCLOPEDIA_DIR, "thumbnails")

CONTENT_DB_DIR = os.path.join(BASE_DATA_DIR, "assetdb", ".db", "contentdb.sqlite3")

ORIGINAL_CONTENT_ROOT = "C:/TouchSurgery/assetdb/vault2"
ORIGINAL_CONTENT_ROOT_OLD = "C:/TouchSurgery/assetdb"
if platform.system() == "Windows":
    REPLACEMENT_CONTENT_ROOT = "C:/TouchSurgery/assetdb/vault2"
    REPLACEMENT_CONTENT_ROOT_OLD = "C:/TouchSurgery/assetdb"
else:
    REPLACEMENT_CONTENT_ROOT = "/Volumes/content/assetdb/vault2"
    REPLACEMENT_CONTENT_ROOT_OLD = "/Volumes/content/assetdb"

DELIVERY_ROOT = os.path.join(BASE_DATA_DIR, "delivery")
