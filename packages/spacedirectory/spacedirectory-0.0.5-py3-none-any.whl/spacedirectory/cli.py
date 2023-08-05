#!/usr/bin/env python3
# Copyright (C) 2018  Sébastien Gendre

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import argparse

from spacedirectory import description, tools, views
from spacedirectory.models import directory, space


def show_list_spaces_names(args):
    """Show the list of spaces names"""
    spaces_list = directory.get_spaces_list()
    views.print_spaces_list_names(spaces_list)


def show_space_info(args):
    """Show informations of a given space"""
    if args.space_name:
        try:
            space_required = directory.get_space_from_name(
                args.space_name
            )
        except directory.SpaceNotExist as error:
            views.print_error(error.message)
            raise SystemExit(1)
        views.print_space_infos(space_required=space_required,
                                print_json=args.json)
    elif args.api_url:
        space_data = tools.get_json_data_from_url(args.api_url)
        space_required = space.Space(data=space_data)
        views.print_space_infos(space_required=space_required,
                                print_json=args.json)
    else:
        views.print_error('Please, specify a space')
        views.print_error("'spacedirectory info --help' for help")
        raise SystemExit(1)


def main():
    """Function called by the command line tool
    Parse the command line arguments and do what arguments request"""
    # Create an argument parser
    arguments_parser = argparse.ArgumentParser(
        description=description,
    )
    # Set the default function to be called if no commands
    arguments_parser.set_defaults(func=show_list_spaces_names)
    # Create a commands subparser
    arguments_subparsers = arguments_parser.add_subparsers(
        help='Commands you want')

    # Add the command 'list' parser
    parser_list = arguments_subparsers.add_parser(
        'list',
        help='Get only the list of spaces (default action)'
    )
    # Set the default function to be called for this command
    parser_list.set_defaults(func=show_list_spaces_names)

    # Add the command 'info' parser
    parser_info = arguments_subparsers.add_parser(
        'info',
        help='Get infos of a given space'
    )
    parser_info.add_argument(
        'space_name',
        nargs='?',
        default=None,
        help='A given space name',
    )
    parser_info.add_argument(
        '-a',
        '--api',
        dest="api_url",
        help='A given space api',
    )
    parser_info.add_argument(
        '-j',
        '--json',
        action="store_true",
        help='Get a dump of the asked space infos in JSON',
    )
    # Set the default function to be called for this command
    parser_info.set_defaults(func=show_space_info)

    # Parse the command line arguments
    arguments = arguments_parser.parse_args()
    # Call whatever command is called
    arguments.func(arguments)


if __name__ == '__main__':
    main()
