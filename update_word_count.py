from datetime import date, timedelta
from os import listdir
from os.path import isfile, join
import json
import re
import subprocess
import sys

WORDCOUNT_FILE_NAME = 'wordcounts.json'
COUNT = 'count'
DATE = 'date'
ORDINAL = 'ordinal'
SRC_DIR = 'src'
WC_RESULT_PATTERN = re.compile('\W*(\d*)\W*\w*')

GOAL_COUNT = 50000
FINAL_DATE = date(2014,11,30)

if len(sys.argv) > 1:
   for arg in sys.argv:
      if arg.startswith('--path'):
         SRC_DIR = arg[7:]

def isvalidfile(filename):
   return filename[-1] != '~'

def getfiles(path):
   files = []
   for f in listdir(path):
      filename = join(path, f)
      if isfile(filename):
         if isvalidfile(filename):
            files.append(filename)
      else:
         files.extend(getfiles(filename))
   return files

def getcount():
   print "Counting words..."
   files = getfiles(SRC_DIR)
   if len(files) == 0:
      return 0

   args = ['wc', '-w']
   args.extend(files)
   output = subprocess.check_output(args)
   print output
   lines = output.splitlines()
   return int(WC_RESULT_PATTERN.match(lines[-1]).group(1))

def appendcurrentcount(wordcounts, currentcount):
   print "Adding a new word count entry for today..."
   today = date.today()
   wordcounts.append({DATE:today.isoformat(), ORDINAL:today.toordinal(), COUNT:currentcount})

if (isfile(WORDCOUNT_FILE_NAME)):
   with open(WORDCOUNT_FILE_NAME, 'r') as f:
      print "Reading previous word counts..."
      wordcounts = json.load(f)
else:
   print 'The file {} does not exist. I\'ll create it.'.format(WORDCOUNT_FILE_NAME)
   wordcounts = []

lastcount = 0
currentcount = getcount()

if len(wordcounts) > 0:
   lastentry = wordcounts[-1]
   lastdate = date.fromordinal(lastentry[ORDINAL])
   if (date.today() == lastdate):
      print "You've already logged a word count today. Updating today's count..."
      lastentry[COUNT] = currentcount
      if (len(wordcounts) > 1):
         lastcount = wordcounts[-2][COUNT]
   else:
      lastcount = lastentry[COUNT]
      appendcurrentcount(wordcounts, currentcount)
else:
   appendcurrentcount(wordcounts, currentcount)

print "Saving word count..."
with open(WORDCOUNT_FILE_NAME, 'w') as f:
   json.dump(wordcounts, f, indent=3)
print "Done.\n"

writtentoday = currentcount - lastcount
wordsleft = GOAL_COUNT - currentcount
daysleft = (FINAL_DATE - date.today()).days + 1
if daysleft > 0:
   perdaytoreachgoal = wordsleft / daysleft
else:
   perdaytoreachgoal = wordsleft

print "   Words written today: " + repr(writtentoday)
print "Words written in total: " + repr(currentcount)
print "      Total words left: " + repr(wordsleft)
print "             Days left: " + repr(daysleft)
print "  Words per day needed: " + repr(perdaytoreachgoal)


