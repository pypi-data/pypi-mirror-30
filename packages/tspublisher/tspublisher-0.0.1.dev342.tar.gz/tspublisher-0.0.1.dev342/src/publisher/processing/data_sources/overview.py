import os

from publisher.exceptions import ContentMissingError
from publisher.processing.data_sources.utils import YamlObject, copy_assets
from publisher import settings


def get_overview_and_devices(phase, asset_directory):
    code = phase.released_as or phase.code

    yaml_overview_dir = os.path.join(settings.ENCYCLOPEDIA_OVERVIEW_YAML_DIR, code)
    yaml_overview_file = os.path.join(yaml_overview_dir, "overview.yml")
    yaml_overview_asset_dir = os.path.join(yaml_overview_dir, "assets")

    yaml_devices_dir = os.path.join(settings.ENCYCLOPEDIA_DEVICES_YAML_DIR, code)
    yaml_devices_file = os.path.join(yaml_devices_dir, "devices.yml")
    yaml_devices_asset_dir = os.path.join(yaml_devices_dir, "assets")

    # Overview
    if os.path.isfile(yaml_overview_file):
        print "Using current yaml file: %s" % yaml_overview_file
        overview_data = read_yaml_data(yaml_overview_file)
    else:
        raise ContentMissingError("Yaml overview not found in {0}".format(yaml_overview_file))

    # Key Instruments
    if os.path.isfile(yaml_devices_file):
        print "Found devices yaml file: %s" % yaml_devices_file
        devices_data = read_yaml_data(yaml_devices_file)
        copy_assets(yaml_devices_asset_dir, asset_directory)
    else:
        devices_data = []

    copy_assets(yaml_overview_asset_dir, asset_directory)

    return overview_data, devices_data


def read_yaml_data(overview_file):
    yaml = YamlObject()

    with open(overview_file, "r") as overview_file:
        overview_data = yaml.load(overview_file)
        return overview_data
