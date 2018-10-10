#!/usr/bin/env python3
"""Define the Django main entry.

Copyright (C) 2018 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

Attributes:
    is_debug (bool): Whether or not the environment is running in debug mode.
    debugger_port (int): The VSCode remote debugging port. Defaults to: 3000.
    debugger_interface (str): The VSCode remote debugging interface address.
        Defaults to:  0.0.0.0.

"""
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise

    is_debug = os.environ.get('DEBUG')
    if is_debug and is_debug == 'off':
        is_debug = False

    # Handle remote debugging
    if is_debug and os.environ.get('VSCODE_DEBUGGER_ENABLED', False):
        if os.environ.get('RUN_MAIN') or os.environ.get('WERKZEUG_RUN_MAIN'):
            import ptvsd
            debugger_port = int(os.environ.get('VSCODE_DEBUGGER_PORT', 3030))
            debugger_interface = os.environ.get('VSCODE_DEBUGGER_INTERFACE', '0.0.0.0')
            ptvsd.enable_attach(address=(debugger_interface, debugger_port))

    execute_from_command_line(sys.argv)
