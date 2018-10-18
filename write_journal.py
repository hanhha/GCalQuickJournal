#!/usr/bin/python
from __future__ import print_function
import httplib2
import sys, tempfile, os
from sys import platform
import os.path
from subprocess import call

import datetime
import re

if platform == "linux" or platform == "linux2":
	#Linux
	pass
elif platform == "darwin":
	#OS X
	EDITOR = '/Applications/FocusWriter.app/Contents/MacOS/FocusWriter'
	HOME = os.path.expanduser('~') 
elif platform == "win32" or platform == "cygwin":
	#Windows
	EDITOR = os.environ["ProgramFiles(x86)"] + '/FocusWriter/FocusWriter.exe'
	HOME = 'C:\Users\hha\Documents\MobaXterm\home' 

initial_message = ""

def extract_tags (filename):
	with open(filename) as f:
		tags = re.findall(r"#([\sA-Za-z0-9-]+)", f.read(), re.MULTILINE) #TODO: this counts "\n" as a character in a tag (#abc\ndef)<- fix this.
	return map (str.strip, tags)

def main():

	now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

	journalfile = 'tmpjournal.jn'
	journalfile_path = os.path.join(HOME, journalfile)
	
	print ('Creating temporary local file ' + journalfile_path)
	call(['touch', journalfile_path])
	
	print ('Calling ' + EDITOR)
	call([EDITOR, journalfile_path])

	filesize = os.stat(journalfile_path).st_size
	if filesize > 0:
		taglist = extract_tags(journalfile_path)
		print ('List of tags:')
		print (taglist)
		
	if os.path.isfile(journalfile_path):
		print ('Removing temporary local file ' + journalfile_path)
		call(['rm', '-f', journalfile_path])

if __name__ == '__main__':
	main()
