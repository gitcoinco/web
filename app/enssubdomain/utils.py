# -*- coding: utf-8 -*-
"""Define the ENS subdomain utilities and miscellaneous logic.

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

"""
import binascii


def convert_txn(b_txn):
    """Convert a b'' represented string to 0x.

    Args:
        b_txn (str): The txn to be converted.
            Example: "b'7bce7e4bcd2fea4d26f3d254bb8cf52b9ee8dd7353b19bfbc86803c27d9bbf39'"

    Usage:
        convert_txn("b'7bce7e4bcd2fea4d26f3d254bb8cf52b9ee8dd7353b19bfbc86803c27d9bbf39'")
        "0x7bce7e4bcd2fea4d26f3d254bb8cf52b9ee8dd7353b19bfbc86803c27d9bbf39"

    Returns:
        str: The '0x0 representation of the txn.

    """
    return f"0x{binascii.b2a_hex(b_txn).decode('utf-8')}"
