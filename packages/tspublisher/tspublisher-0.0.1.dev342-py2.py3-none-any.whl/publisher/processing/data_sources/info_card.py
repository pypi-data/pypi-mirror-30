import os.path

from publisher.exceptions import ContentMissingError
from publisher.processing.data_sources.utils import YamlObject
from publisher import settings


def get_more_info_data(info_id):
    yaml_dir = os.path.join(settings.ENCYCLOPEDIA_YAML_DIR, info_id)
    yaml_file = os.path.join(yaml_dir, info_id + ".yml")
    source_asset_dir = os.path.join(yaml_dir, "assets")

    if not os.path.isfile(yaml_file):
        raise ContentMissingError("Yaml infocard not found in {0}".format(yaml_file))

    return read_yaml_data(yaml_file), source_asset_dir


def read_yaml_data(yaml_file):
    yaml = YamlObject()

    with open(yaml_file, "r") as overview_file:
        overview_data = yaml.load(overview_file)
        return overview_data
