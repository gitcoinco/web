import io
import os
import re
import subprocess
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'kills processes (other commandS) that have been running for 24h or longer'

    def add_arguments(self , parser):
        parser.add_argument('max_age', type=int, help='Max age of the process in seconds. Processes will be killed if max age has been reached.')
        parser.add_argument('proc_re', type=str, help='Regex to identify the process we are monitoring')
        
        parser.add_argument('--exec', action='store_true')

    def handle(self, *args, **options):
        do_exec = options["exec"]
        if not do_exec:
            print("""
****************************************************************************************
* This is a dry run, no processes will be killed
* In order to kill the processes re-run this command with the '--exec' option
****************************************************************************************
""")
        print(f"""Searching for processes with folowing criteria:
        Regex for the the command       : "{options["proc_re"]}"
        Process age greater or equal to : {options["max_age"]} seconds 
""")
        re_process = re.compile(options["proc_re"])
        max_age = options["max_age"]
        ps_cmd = ["ps", "-o", "pid,etimes,args", "-axf"]
        proc = subprocess.Popen(ps_cmd, stdout=subprocess.PIPE)
        output, _error = proc.communicate()
        # print(output.decode("utf-8"))

        for line in io.TextIOWrapper(io.BytesIO(output)).readlines():
            line = line.strip()
            r = re.findall(r"^ *(\d+) +(\d+) +(.*)$", line)
            if r:
                m = r[0]
                pid = int(m[0])
                age = int(m[1])
                process = m[2]

                match = re_process.match(process)

                if match:
                    print(f"Checking process: \n\tPID: {pid}\n\tAge (seconds): {age}\n\tCommand: '{process}'\n")
                    if age >= max_age:
                        print("\t ==> Process running longer than max allowed age => killing it")
                        if do_exec:
                            os.kill(pid, 9)
                        else:
                            print("\t   ***   This is s dry run, we will not actually kill the process   ***   ")
                        print("\t ==> Process has been killed")
