from __future__ import print_function

import argparse
import sys
from publisher import procedure_content
from publisher.processing import procedure


class PublisherCLI():

    def __init__(self, args):
        parser = argparse.ArgumentParser(
            description='Touch Surgery Publisher',
            usage='tspub <command> [<args>]'
        )
        subparsers = parser.add_subparsers(
            title='Available commands',
            description=(
                'These commands allow you to create and '
                'publish TS simulations'
            ),
            help='subparsers help'
        )
        cli_commands = [c for c in dir(self) if not c.startswith('_')]

        for command in cli_commands:
            sub_parser = subparsers.add_parser(
                command,
                help=getattr(self, command).__doc__
            )
            sub_parser.set_defaults(func=getattr(self, command))

        namespace = parser.parse_args(args[0:1])
        namespace.func(args[1:])

    def setup(self, args):
        """ Setup your machine, ready to create and edit simulations in 3 steps
                1. Check if git is installed
                2. Setup SSH
                3. Cloning the repo and git pull
        """
        procedure_content.setup_users_machine()

    def procedures(self, args):
        """ List all procedures in the git repository, each being a separate branch
        """
        procedure_content.list_procedures()

    def phases(self, args):
        """ List all procedures in the git repository, each being a separate branch
        """
        procedure_content.list_phases()

    def workon(self, args):
        """ Move to the branch containing the specified procedure so that it can be worked on
        """
        parser = argparse.ArgumentParser(
            description='Move to the branch containing the specified procedure',
            usage='''tspub workon <procedure_code>'''
        )
        parser.add_argument(
            'procedure',
            help='The procedure code'
        )

        self._clean_working_directory_state()

        args = parser.parse_args(args)
        procedure_content.change_procedure(args.procedure)

    def save(self, args):
        """ Commit and push current changes to the repo
        """
        parser = argparse.ArgumentParser(
            description='Commit and push current changes to the repo',
            usage='''tspub save <commit_message>'''
        )
        parser.add_argument(
            'commit_message',
            help='Describe what changes have been made'
        )
        args = parser.parse_args(args)
        procedure_content.save_working_changes(args.commit_message)

    def create(self, args):
        """Create a new branch with the name of the procedure_code param
        """
        parser = argparse.ArgumentParser(
            description='Command line interface for Touch Surgery',
            usage='''tspub create <procedure_code>'''
        )
        parser.add_argument('procedure_code', help='code of the procedure to be created')
        parser.add_argument('--init', action='store_true', help='Create a stub yaml file for the procedure')
        parser.add_argument('--graphics', action='store_true', help='Copy latest images (normal)')
        parser.add_argument('--pip_graphics', action='store_true', help='Copy latest pip images (normal)')
        parser.add_argument('--widget_graphics', action='store_true', help='Copy latest widget images (normal)')
        parser.add_argument('--thumbnails', action='store_true', help="Pull latest thumbnails (both)")
        parser.add_argument('--step_numbers', action='store_true', help='Prepend step number in step content')
        parser.add_argument('--info_step', action='store_true', help='Add build information')
        parser.add_argument('--country_restrict', default="",
                            help="Comma separated country restrictions (ISO Alpha-2) e.g. US, FR, ES")

        args = parser.parse_args(args)

        if args.procedure_code not in procedure_content.list_procedures(quiet=True):
            self._clean_working_directory_state()
            procedure_content.create_procedure_branch(args.procedure_code)
        else:
            raise Exception("The procedure {0} already exists and thus cannot be created".format(args.procedure_code))

        if args.init:
            procedure.create_procedure(args.procedure_code)
        else:
            procedure.build_procedure(args.procedure_code, graphics=args.graphics, pip_graphics=args.pip_graphics,
                                      widget_graphics=args.widget_graphics, thumbnails=args.thumbnails,
                                      step_numbers=args.step_numbers, info_step=args.info_step,
                                      country_restriction=args.country_restrict)

        procedure_content.save_working_changes("Initial commit", initial=True, procedure_code=args.procedure_code)

    def publish(self, args):
        """Publish procedure with the specified distribution group
        """
        parser = argparse.ArgumentParser(
            description='Publish procedure with the specified distribution group',
            usage='''tspub publish <distribution_group> <number>'''
        )
        parser.add_argument(
            'distgroup',
            help='Distribution group to be published to'
        )
        parser.add_argument(
            '--number',
            help='The number of previous commits to be shown',
            required=False
        )
        args = parser.parse_args(args)
        procedure_content.publish(args.distgroup, args.number)

    @staticmethod
    def _clean_working_directory_state():
        if procedure_content.has_unstaged_changes():
            user_choice = PublisherCLI._get_user_decision()

            if user_choice == 'y':
                commit_message = PublisherCLI._get_commit_message()
                procedure_content.save_working_changes(commit_message)
            else:
                procedure_content.delete_unstaged_changes()

    @staticmethod
    def _get_commit_message():
        """ Return the commit message from the user
        """
        return raw_input("Please enter a commit message")

    @staticmethod
    def _get_user_decision():
        """ Return the users y or n input
        """
        user_input = ""
        while user_input not in ['y', 'n']:
            print("You have unsaved changes. Would you save them now? If you do not save them they will be deleted")
            user_input = raw_input("> y or n:")
        return user_input.lower()


def main():
    PublisherCLI(sys.argv[1:])
