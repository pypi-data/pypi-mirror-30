import subprocess
import os.path
import sys
from shutil import copyfile
import json

from publisher.exceptions import ContentMissingError
from publisher.processing.data_sources.step import get_csv_info
from publisher.processing.data_sources.utils import delete_misc_files, copy_assets
from publisher import settings

ffmpegExe = 'ffmpeg'

ffmpegDefaults = [ffmpegExe,
                  # Input format
                  '-f', 'image2',
                  # Input framerate
                  '-r', '25',
                  # Insert position for input frames to be overwritten
                  'INPUT_SETTINGS',
                  # Video codec for the output
                  '-codec:v', 'libx264',
                  # Disables some advanced features but provides for better compatibility with iOS/Android
                  '-profile:v', 'baseline',
                  # Must set colorspace format compatible with x264
                  '-pix_fmt', 'yuv420p',
                  # H.264 level setting
                  '-level:v', '2.2',
                  # Disable CABAC
                  '-coder', '0',
                  # Video filter graph
                  '-vf', "scale='680:1024',setsar=1.13",
                  # Output framerate
                  '-r', '25',
                  # Frequency of keyframes
                  # '-g', '2',
                  # Logging level
                  '-loglevel', 'panic']


def is_ffmpeg_installed():
    p = subprocess.Popen([ffmpegExe, '-h'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()
    rt = p.poll()
    return rt == 0


def get_pip_dir(module_dir):
    return os.path.join(module_dir, "pipSource")


def get_widget_dir(module_dir):
    return os.path.join(module_dir, "WidgetGraphics")


def get_graphics_dir(module_dir):
    return os.path.join(module_dir, "Graphics")


def get_latest_version_directory(phase_code):
    dir_name = os.path.join(settings.DELIVERY_ROOT, phase_code)

    if not os.path.isdir(dir_name):
        raise ContentMissingError('Source frames not found for {0}'.format(phase_code))

    path, dirs, files = os.walk(dir_name).next()
    return os.path.join(path, dirs[-1], phase_code)


def convert_files(phase, phase_directory, update_graphics=True, update_pip_graphics=True, update_widget_graphics=True):
    if not is_ffmpeg_installed():
        print("Error: no ffmpeg executable found at: ", ffmpegExe)
        sys.exit(2)

    latest_phase_directory = get_latest_version_directory(phase.code)

    if update_graphics:
        graphics_dir = get_graphics_dir(latest_phase_directory)
        graphics_files = get_file_list(graphics_dir)

        if not graphics_files:
            raise ContentMissingError('Source frames not found for {0}'.format(phase.code))

        copy_graphics_files(phase.code, graphics_dir, phase_directory)

    pip_directory = get_pip_dir(latest_phase_directory)
    if update_pip_graphics and os.path.isdir(pip_directory):
        copy_pip_files(phase.code, pip_directory, phase_directory)

    widget_directory = get_widget_dir(latest_phase_directory)
    if update_widget_graphics and os.path.isdir(widget_directory):
        copy_widget_files(widget_directory, phase_directory)


def copy_graphics_files(phase_code, source_directory, dest_dir):
    file_list = get_file_list(source_directory)

    headers, rows = get_csv_info(phase_code)

    frame_numbers = []
    missing_frames = []
    prefix = "image"

    for row in rows:
        first_frame = int(row["firstImageId"])

        if row["lastImageId"]:
            last_frame = int(row["lastImageId"])
        else:
            last_frame = first_frame

        frame_numbers.append([first_frame, last_frame])

        for i in range(first_frame, last_frame + 1):
            image_name = "%s%04d.jpg" % (prefix, i)

            # Check for missing frames in step
            if image_name not in file_list:
                missing_frames.append(image_name)

        if row["testImage"]:
            test_frame = int(row["testImage"])

            frame_numbers.append([test_frame, test_frame])
            image_name = "%s%04d.jpg" % (prefix, test_frame)

            if image_name not in file_list:
                missing_frames.append(test_frame)

    # Error out if missing frames were found
    if missing_frames:
        raise EOFError("Missing frames: %s" % str(missing_frames))

    print "\n-- Converting image files --"
    copy_files(frame_numbers, source_directory, dest_dir, prefix)


def copy_pip_files(phase_code, source_directory, dest_directory):
    path, dirs, files = os.walk(source_directory).next()

    pip_folders = {}

    for pip_name in dirs:
        pip_folder = os.path.join(path, pip_name)
        file_list = get_file_list(pip_folder)

        pip_folders[pip_name] = {
            "folder": pip_folder,
            "files": file_list
        }

    headers, rows = get_csv_info(phase_code)

    if "pip_sim2dData" not in headers:
        return

    frame_numbers = {}
    missing_frames = {}

    for row in rows:

        pip_info = row["pip_sim2dData"]

        if pip_info and not pip_info == "{}":
            pip_load = json.loads(pip_info)
            pip_name = pip_load["view"]

            if pip_load["sequence"]:
                first_frame = int(row["firstImageId"])
                if row["lastImageId"]:
                    last_frame = int(row["lastImageId"])
                else:
                    last_frame = first_frame

                if pip_name not in frame_numbers:
                    frame_numbers[pip_name] = []

                frame_numbers[pip_name].append([first_frame, last_frame])

                for i in range(first_frame, last_frame):
                    image_name = "%s%04d.jpg" % (pip_name, i)

                    # Check for missing frames in step
                    if image_name not in pip_folders[pip_name]["files"]:
                        if pip_name not in missing_frames:
                            missing_frames[pip_name] = []

                        missing_frames[pip_name].append(image_name)

                # Error out if missing frames were found
                if missing_frames:
                    raise EOFError("Missing frames: %s" % str(missing_frames))

                print "\n-- Converting pip files --"
                for pip in frame_numbers:
                    copy_files(frame_numbers[pip], pip_folders[pip]["folder"], dest_directory, pip)

            else:
                image_name = "%s_image%s" % (pip_name, pip_load["ext"])
                pip_files = pip_folders[pip_name]["files"]

                if len(pip_files) > 1:
                    raise EOFError("Too many files for non sequence pip: %s" % str(pip_folders[pip_name]["folder"]))
                elif len(pip_files) < 1:
                    raise EOFError("Missing pip images in: %s" % str(pip_folders[pip_name]["folder"]))

                asset_dir = os.path.join(dest_directory, "assets")
                dest_file = os.path.join(asset_dir, image_name)
                source_file = os.path.join(pip_folders[pip_name]["folder"], pip_files[0])

                copyfile(source_file, dest_file)


def copy_widget_files(source_directory, dest_directory):
    asset_dir = os.path.join(dest_directory, "assets")
    copy_assets(source_directory, asset_dir)


def copy_files(frame_numbers, source_dir, dest_dir, prefix):
    asset_dir = os.path.join(dest_dir, "assets")

    for frames in frame_numbers:
        # Copy first and last image
        for frame in frames:
            frame_file = "%s%04d.jpg" % (prefix, frame)

            source_file = os.path.join(source_dir, frame_file)
            dest_file = os.path.join(asset_dir, frame_file)

            print "Copying image file: %s" % dest_file
            copyfile(source_file, dest_file)

        # Convert sequence to video file
        if not frames[1] == frames[0]:
            video_file_name = "video-%s%04d-%s%04d.mp4" % (prefix, frames[0], prefix, frames[1])
            input_name = prefix + "%04d.jpg"
            input_image_path = os.path.join(source_dir, input_name)
            output_video_path = os.path.join(asset_dir, video_file_name)
            frame_count = str(frames[1] - frames[0] + 1)

            ffmpeg_options = list(ffmpegDefaults)

            # Insert settings in list - FFMPEG requires a specific order to the arguments
            input_index = ffmpeg_options.index("INPUT_SETTINGS")
            ffmpeg_options[input_index:input_index + 1] = [
                # Set starting frame for image sequence
                "-start_number", str(frames[0]),
                # Force overwrite
                "-y",
                # Add input file range in image0000... format
                "-i", input_image_path,
                # Set frame count for video
                "-frames:v", frame_count]

            # Set output video location
            ffmpeg_options.append(output_video_path)

            print "Creating video file: %s" % output_video_path
            print " ".join([str(x) for x in ffmpeg_options]) + "\n"

            subprocess.call(ffmpeg_options)

            if not os.path.exists(output_video_path):
                raise Exception("Failed to create %s" % output_video_path)

        delete_misc_files(asset_dir)


def get_file_list(directory_name):
    path, dirs, files = os.walk(directory_name).next()

    # Remove thumbnail file from list
    if "Thumbs.db" in files:
        files.remove("Thumbs.db")

    return files
