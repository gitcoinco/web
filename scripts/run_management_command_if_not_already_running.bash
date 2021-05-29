#!/bin/bash

: <<'END'
Copyright (C) 2021 Gitcoin Core

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
END

IS_ALREADY_RUNNING=$(ps -aux | grep -e "$1" | grep -c python)
if [ "$2" != "" ]; then
    IS_ALREADY_RUNNING=$(ps -aux | grep -e "$1 $2" | grep -c python)
fi
if [ "$3" != "" ]; then
    #echo "ps -aux | grep -e \"$1 $2 $3\" | grep -c python"
    IS_ALREADY_RUNNING=$(ps -aux | grep -e "$1 $2 $3" | grep -c python)
fi
if [ "$4" != "" ]; then
    #echo "ps -aux | grep -e \"$1 $2 $3\" | grep -c python"
    IS_ALREADY_RUNNING=$(ps -aux | grep -e "$1 $2 $3 $4" | grep -c python)
fi

if [ "$5" != "" ]; then
    #echo "ps -aux | grep -e \"$1 $2 $3\" | grep -c python"
    IS_ALREADY_RUNNING=$(ps -aux | grep -e "$1 $2 $3 $4 $5" | grep -c python)
fi

if [ "$IS_ALREADY_RUNNING" -eq "0" ]; then
    bash scripts/run_management_command.bash $1 $2 $3 $4 $5 $6 $7 $8 $9
fi
