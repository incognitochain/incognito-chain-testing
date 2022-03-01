#!/usr/bin/python3
import re
import sys

try:
    log_file = sys.argv[1]
except IndexError:
    print("Please specify a log file")
    exit()
try:
    log_level = sys.argv[2]
except IndexError:
    print("Log level is not specified, use INFO instead")
    log_level = "INFO"

LOG_LVL = {'CRITICAL': 50,
           'FATAL': 50,
           'ERROR': 40,
           'WARNING': 30,
           'WARN': 30,
           'INFO': 20,
           'DEBUG': 10,
           'NOTSET': 0}


def get_log_level_of(line):
    regex = re.compile(r'^\d{2}:\d{2}:\d{2} ([A-Z]+)')
    match = re.match(regex, line)
    return LOG_LVL[match.group(1)] if match else -1


with open(log_file, "r") as file:
    line = 1
    still_print = False
    while line:
        line = file.readline()
        lvl = get_log_level_of(line)
        if lvl >= LOG_LVL[log_level]:
            still_print = True
            print(line, end="") if still_print else None
        elif lvl == -1:
            print(line, end="") if still_print else None
        else:
            still_print = False
