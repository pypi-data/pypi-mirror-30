import os
from shutil import copyfile

from publisher.exceptions import ContentMissingError
from publisher.processing.data_sources.utils import copy_assets
from publisher import settings


def update_thumbnails(procedure, asset_directory):
    source_asset_dir = _get_thumbnail(procedure.code)
    copy_assets(source_asset_dir, asset_directory)


def update_phase_thumbnails(phase, asset_directory):
    phase_icon = os.path.join(asset_directory, "icon.jpg")

    print "Getting updated icon for phase"
    thumbnail_directory = _get_thumbnail(phase.code)
    thumbnail = os.path.join(thumbnail_directory, "icon.jpg")
    copyfile(thumbnail, phase_icon)


def _get_thumbnail(item_code):
    thumbnail_dir = os.path.join(settings.ENCYCLOPEDIA_THUMBNAILS_DIR, item_code)

    if not os.path.isdir(thumbnail_dir):
        raise ContentMissingError('Expected thumbnail to exist for {0}'.format(item_code))

    return thumbnail_dir
