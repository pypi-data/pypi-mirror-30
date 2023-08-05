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
import sys
from pprint import pprint
from colors import color


def print_space_infos(space_required='', print_json=False):
    """Print infos of the given space

    Parameters:
    - space_required (space.Space): The space required by the user
    - print_json (bool): Print his json
    """
    if print_json:
        pprint(space_required.data)
        return

    # Print name and website
    print('')
    print(color(space_required.name, style='bold'))
    print(color('='*len(space_required.name), style='bold'))
    if space_required.website_url:
        print(color('Website:', style='bold'),
              space_required.website_url)
        print('')

    # Print status
    if space_required.status:
        status = space_required.status
        print(color('Status', style='bold+underline'))
        if status.is_open:
            open_message = (color('Open', 'green'))
        else:
            open_message = (color('Close', 'red'))
        print(color('The space is:', style='bold'),
              open_message)
        if status.message:
            print(color('Message:', style='bold'),
                  status.message)
        if status.last_change:
            print(color('Last change:', style='bold'),
                  status.last_change.strftime('%Y-%m-%d %a %H:%M'))
        if status.trigger_person:
            print(color('Changed by:', style='bold'),
                  status.trigger_person)
        print('')

    # Print location
    if space_required.location:
        location = space_required.location
        print(color('Location', style='bold+underline'))
        if location.address:
            print(color('Address:', style='bold'),
                  location.address)
        if location.longitude is not None or location.latitude is not None:
            latitude_hemishere = 'N' if location.latitude > 0 else 'S'
            longitude_hemisphere = 'E' if location.longitude > 0 else 'W'
            print(color('Geographic coord.:', style='bold'),
                  "lat. {0:.6f} {1}".format(
                      location.latitude,
                      latitude_hemishere
                  ),
                  '/',
                  "lon. {0:.6f} {1}".format(
                      location.longitude,
                      longitude_hemisphere
                  ))
        print('')


def print_spaces_list_names(spaces_list=''):
    """Print the list of spaces"""
    for space_name in spaces_list.keys():
        print(space_name)


def print_error(message=''):
    """Print error on the stderr"""
    sys.stderr.write(message+'\n')
