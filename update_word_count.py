from argparse import ArgumentParser
from datetime import date
from os import listdir
from os.path import isfile, join
import json
import re
import subprocess

import dateutil.parser

from date_utils import get_end_of_month, get_start_of_month

WORDCOUNT_FILE_NAME = 'wordcounts.json'
COUNT = 'count'
DATE = 'date'
ORDINAL = 'ordinal'
SRC_DIR = 'src'
WC_RESULT_PATTERN = re.compile('\W*(\d*)\W*\w*')

GOAL_COUNT = 50000

TODAY = date.today()
DEFAULT_START_DATE = get_start_of_month(TODAY)
DEFAULT_END_DATE = get_end_of_month(TODAY)


def create_parser():
    parser = ArgumentParser()
    parser.add_argument("-p", "--path", help="The directory or file to scan.", type=str,
                        default='src')
    parser.add_argument("-e", "--end-date",
                        help="The last day of the challenge. Defaults to the end of the month.",
                        type=str, default=DEFAULT_END_DATE.isoformat())
    parser.add_argument("-s", "--start-date",
                        help="The first day of the challenge. Defaults to the start of the month.",
                        type=str, default=DEFAULT_START_DATE.isoformat())
    return parser


def is_valid_file(filename):
    return filename[-1] != '~'


def getfiles(path):
    files = []
    if isfile(path):
        if is_valid_file(path):
            files.append(path)
    else:
        for f in listdir(path):
            filename = join(path, f)
            files.extend(getfiles(filename))
    return files


def getcount(path):
    print "Counting words..."
    files = getfiles(path)
    if len(files) == 0:
        return 0

    args = ['wc', '-w']
    args.extend(files)
    output = subprocess.check_output(args)
    print output
    lines = output.splitlines()
    return int(WC_RESULT_PATTERN.match(lines[-1]).group(1))


def append_current_count(wordcounts, currentcount):
    print "Adding a new word count entry for today..."
    today = date.today()
    wordcounts.append({DATE: today.isoformat(), ORDINAL: today.toordinal(), COUNT: currentcount})


parser = create_parser()
args = parser.parse_args()

START_DATE = dateutil.parser.parse(args.start_date).date()
END_DATE = dateutil.parser.parse(args.end_date).date()

if isfile(WORDCOUNT_FILE_NAME):
    with open(WORDCOUNT_FILE_NAME, 'r') as f:
        print "Reading previous word counts..."
        wordcounts = json.load(f)
else:
    print 'The file {} does not exist. I\'ll create it.'.format(WORDCOUNT_FILE_NAME)
    wordcounts = []

lastcount = 0
currentcount = getcount(args.path)

if len(wordcounts) > 0:
    lastentry = wordcounts[-1]
    lastdate = date.fromordinal(lastentry[ORDINAL])
    if date.today() == lastdate:
        print "You've already logged a word count today. Updating today's count..."
        lastentry[COUNT] = currentcount
        if len(wordcounts) > 1:
            lastcount = wordcounts[-2][COUNT]
    else:
        lastcount = lastentry[COUNT]
        append_current_count(wordcounts, currentcount)
else:
    append_current_count(wordcounts, currentcount)

print "Saving word count..."
with open(WORDCOUNT_FILE_NAME, 'w') as f:
    json.dump(wordcounts, f, indent=3)
print "Done.\n"

writtentoday = currentcount - lastcount
wordsleft = GOAL_COUNT - currentcount
daysleft = (END_DATE - TODAY).days + 1
if daysleft > 0:
    per_day_to_reach_goal = wordsleft / daysleft
else:
    per_day_to_reach_goal = wordsleft

print "Competition time frame: {} - {}".format(START_DATE, END_DATE)
print "   Words written today: " + repr(writtentoday)
print "Words written in total: " + repr(currentcount)
print "      Total words left: " + repr(wordsleft)
print "             Days left: " + repr(daysleft)
print "  Words per day needed: " + repr(per_day_to_reach_goal)
