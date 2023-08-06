from __future__ import print_function

import os
import subprocess
import sys
import shutil


# Directories
HOME_DIRECTORY = os.path.expanduser("~/")
GIT_DIRECTORY = os.path.expanduser("~/git")
REPO_DIRECTORY = os.path.expanduser("~/git/content-production")
SSH_CONFIG_PATH = os.path.expanduser("~/.ssh/config")


class WorkingDirectory(object):
    """ Context manager for changing directory"""
    def __init__(self, new_dir):
        self.new_dir = new_dir
        self.old_dir = None

    def __enter__(self):
        self.old_dir = os.getcwd()
        os.chdir(self.new_dir)

    def __exit__(self, *_):
        os.chdir(self.old_dir)


def git_installed():
    try:
        subprocess.check_output(['git', '--version'])
    except OSError:
        print("Git not installed")
        return False
    return True


def call_command_and_print_exception(command, message):
    try:
        return subprocess.check_output(command)
    except Exception as e:
        print(message)
        raise e


def check_and_create_directory(path):
    try:
        if not os.path.exists(path):
            os.mkdir(path)
    except Exception:
        print("Could not find or create the directory")
        raise


def setup_users_machine():
    """
    User Setup for publish
        1. Check if git is installed
        2. Setup SSH
        3. Cloning the repo and git pull
    """
    if not git_installed():
        win_msg = ('Please install Github for windows from https://desktop.github.com/ before coming back and '
                   'continuing and running setup again.')
        mac_msg = ('Please install Git for Mac from https://git-scm.com/download/mac before running setup again.')

        print("%s" % win_msg if 'win' in sys.platform.lower() else mac_msg)
        sys.exit(1)

    if not has_private_key():
        raise RuntimeError("Unable to proceed without a key. Please contact Hansel before trying again")
        sys.exit(1)

    print("Configuring ssh config file")
    check_and_create_directory(SSH_CONFIG_PATH)
    configure_ssh_config(open(os.path.expanduser(SSH_CONFIG_PATH), "a+"))

    print("Installing and configuring git lfs")
    install_git_lfs()
    configure_git_lfs()

    print("Setting up the content repo")
    clone_content_repo()
    pull_content_repo()

    sys.exit(1)


def list_procedures():
    """ Lists all current branches of the repository
    """
    if os.path.exists(REPO_DIRECTORY):
        with WorkingDirectory(REPO_DIRECTORY):
            unwanted_branches = ['master', '*', '']
            subprocess.check_output(['git', 'fetch'])
            procedure_list = filter(lambda b: b not in unwanted_branches,
                                    subprocess.check_output(['git', 'branch']).split())
            print('\n'.join(procedure_list))
            return procedure_list

    else:
        print("You do not have the content-production repository, please run the setup command.")


def change_procedure(procedure):
    """Switches git branch to the procedure selected
    """
    try:
        with WorkingDirectory(REPO_DIRECTORY):
            subprocess.check_output(['git', 'checkout', procedure])
            subprocess.check_output(['git', 'fetch'])
    except Exception:
        print("Could not find the specified procedure. Make sure you have run setup and entered the correct procedure "
              "name")
        raise


def has_private_key():
    """Check whether the user has the correct private key
    """
    if not os.path.exists(os.path.expanduser("~/.ssh/touchsurgery-studio.pem")):
        return False


def configure_ssh_config(config_file):
    """Creates and sets up an ssh config file, or appends the necessary entry to an existing one
    """
    shutil.copyfile(os.path.expanduser("~/.ssh/config"), os.path.expanduser("~/.ssh/config.bak"))

    ssh_config_stanza = (
        'Host studio-git.touchsurgery.com\n'
        ' User ubuntu\n'
        ' IdentitiesOnly true\n'
        ' IdentityFile ~/.ssh/touchsurgery-studio.pem\n'
    )

    try:
        config_file.seek(0)  # Read from the start of the file
        current_config_text = config_file.read()
        if ssh_config_stanza not in current_config_text:
            config_file.write('\n' + '\n' + ssh_config_stanza)
    except Exception as e:
        print("Unable to configure the ssh config")
        raise e


def install_git_lfs():
    """Install git lfs
    """
    if 'darwin' in sys.platform.lower():
        call_command_and_print_exception(['brew', 'install', 'git-lfs'], "brew lfs install failure")

    call_command_and_print_exception(['git', 'lfs', 'install'], "lfs install failure")


def configure_git_lfs():
    """Set relevant  lfs settings
    """
    call_command_and_print_exception(['git', 'config', '--global', 'lfs.url',
                                      'https://live.touchsurgery.com/api/v3/lfs'], "lfs config failure")
    call_command_and_print_exception(['git', 'config', '--global', 'lfs.activitytimeout', '60'], "lfs config failure")


def clone_content_repo():
    """Clone the content repo
    """
    if not os.path.exists(REPO_DIRECTORY):
        try:
            check_and_create_directory(GIT_DIRECTORY)
            with WorkingDirectory(REPO_DIRECTORY):
                call_command_and_print_exception(['git', 'lfs', 'clone',
                                                  'studio-git.touchsurgery.com:/srv/git/content-repo',
                                                  'content-production'], "Clone repo failure")
        except Exception as e:
            print("Unable to clone the content repo")
            raise e


def pull_content_repo():
    """Run a git pull in the content repo
    """
    try:
        with WorkingDirectory(REPO_DIRECTORY):
            call_command_and_print_exception(['git', 'lfs', 'pull', 'origin', 'master'], "Git pull failure")
    except Exception as e:
        print("Unable to run a git pull in the content repo")
        raise e


def save_working_changes(message):
    """Commits and pushes with the current changes to the repo
    """
    try:
        # Git stage, commit with message and push
        with WorkingDirectory(REPO_DIRECTORY):
            subprocess.check_output(['git', 'stage', '.'])
            commit_output = subprocess.Popen(['git', 'commit', '-a', '-m', '"'+message+'"'], stdout=subprocess.PIPE)
            text_commit_output = commit_output.communicate()[0].decode('utf-8')

            if 'nothing to commit' in text_commit_output:
                print('No changes detected.')
                sys.exit(0)
            subprocess.check_output(['git', 'push'])

    except subprocess.CalledProcessError:
        print("Could not commit/push the changes.")
        raise


def publish(dist_group, number):
    """ Publishes the procedure with a git note containing the distribution group to the chosen commit
    """
    if not number:
        number = 10  # Default number of commits shown
    with WorkingDirectory(REPO_DIRECTORY):
        # Show the user the current module
        print("Current module:")
        print(subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']))

        # Get the user to choose from a list of commits which one they want to publish
        print("Which commit would you like to publish?" + "\n")
        commits, commit_objects = get_messages(number)
        for commit in commits:
            print(commit[0], commit[1], "\n", " " + (commit[2]), commit[3])
        print("\n" + "Enter the number of the version you want to publish here:")
        sys.stdout.flush()
        text = int(raw_input())
        commit_chosen_by_user = commit_objects[text - 1]

        # Update the distribution group and push changes
        try:
                edit_note(dist_group, commit_chosen_by_user)
                subprocess.check_output(['git', 'push', 'origin', 'refs/notes/*'])
                print("Commit", text, "has been published to the", dist_group, "group.")
        except Exception:
            print("Could not publish the procedure to the specified distribution group.")
            raise


def get_messages(number):
    """Get the previous notes and commits.
    """
    commit_list = []
    commit_object_list = []
    with WorkingDirectory(REPO_DIRECTORY):

        # Fetch all notes
        subprocess.check_output(['git', 'fetch', 'origin', 'refs/notes/*:refs/notes/*'])
        # Use git log to find comments and commits

        log_list = subprocess.check_output(['git', 'log', '--oneline']).split("\n")[:int(number)]
        for counter, log in enumerate(log_list):

            # Remove unwanted empty commit
            if log != "":
                single_commit = []
                note = ""
                commit_object = log.split()[0]
                comment = log.split(" ", 1)[1]

                # Get the notes for the previous commits
                try:
                    output = subprocess.Popen(['git', 'notes', 'show', commit_object], stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE)
                    no_note = output.communicate()[1]
                    if "no note found" in no_note:
                        note = "Not published"
                    else:
                        note = subprocess.check_output(['git', 'notes', 'show', commit_object]).split("\n")[0]
                except subprocess.CalledProcessError:
                    print("Error finding previous commits/distribution groups")

                # List of commit objects separate so user does not see them
                commit_object_list.append(commit_object)

                # Easily readable commit description for command line
                single_commit.append(str(counter + 1))
                single_commit.append("Comment: " + comment)
                single_commit.append("Current distribution group: " + note)
                single_commit.append("\n" + "----------------------------")

                # A list of lists containing the commits
                commit_list.append(single_commit)

    return commit_list, commit_object_list


def edit_note(dist_group, commit_object):
    """ Use the commit object obtained from the get notes command to overwrite a previous note
    """
    with WorkingDirectory(REPO_DIRECTORY):
        try:
            subprocess.check_output(['git', 'notes', 'add', '-f', '-m', dist_group, commit_object])
        except subprocess.CalledProcessError:
            print("Could not change the distribution group for the specified commit")


def delete_unstaged_changes():
    """Deletes all unstaged changes
    """
    try:
        with WorkingDirectory(REPO_DIRECTORY):
            subprocess.check_output(['git', 'checkout', '.'])
    except Exception:
        print("Could not delete local changes.")
        raise


def has_unstaged_changes():
    """Returns whether or not there are uncomitted changes
    """
    try:
        with WorkingDirectory(REPO_DIRECTORY):
            response = subprocess.check_output(['git', 'diff'])
            return True if len(response) else False
    except Exception:
        print("Could not retrieve the git diff. Please ensure the git repo is setup correctly")
        raise
