#!/usr/bin/python
from __future__ import print_function
import httplib2
import sys, tempfile, os
from sys import platform
import os.path
from subprocess import call

from apiclient import discovery
from apiclient.http import MediaFileUpload

import oauth2client
from oauth2client import client
from oauth2client import tools

import datetime
import re

try:
	import argparse
	flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
	flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'GCalQuickJournal'

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

def get_credentials():
	"""Gets valid user credentials from storage.

	If nothing has been stored, or if the stored credentials are invalid,
	the OAuth2 flow is completed to obtain the new credentials.

	Returns:
	Credentials, the obtained credential.
	"""
	home_dir = os.path.expanduser('~')
	credential_dir = os.path.join(home_dir, '.credentials')
	if not os.path.exists(credential_dir):
		os.makedirs(credential_dir)
	credential_path = os.path.join(credential_dir,'journal-python.json')
	store = oauth2client.file.Storage(credential_path)
	credential = store.get()
	if not credential or credential.invalid:
		flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
		flow.user_agent = APPLICATION_NAME
		if flags:
			credential = tools.run_flow(flow, store, flags)
		else: # Needed only for compatibility with Python 2.6
			credential = tools.run(flow, store)
		print ('Storing credentials to ' + credential_path)
	return credential

def upload_media (drv_service, title, filepath, mime_type, resumable=False, description=""):
	media_body = MediaFileUpload(filepath, mimetype=mime_type, resumable=resumable)
	body = {
		'title' : title,
		'description': description,
		'mimeType' : mime_type,
	}
	fileup = drv_service.files().insert(body=body, media_body=media_body).execute()
	return fileup

def add_event (cal_service, cal_id, summary, start_time, end_time, timezone='Etc/GMT-7', has_attachment=True, attachment_url="", description=""):
	event = {
		'summary': summary,
		'description': description,
		'start': {
			'dateTime': start_time,
			'timeZone': timezone,
		},
		'end': {
			'dateTime': end_time,
			'timeZone': timezone,
		},
		'attachments': [
			{'fileUrl':attachment_url},
		],
	}
	event = cal_service.events().insert(calendarId=cal_id, supportsAttachments=has_attachment, body=event).execute()
	return event

def extract_tags (filename):
    with open(filename) as f:
        tags = re.findall(r"#([\sA-Za-z0-9-]+)", f.read(), re.MULTILINE)
	return map (str.strip, tags)

def main():
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	cal_service = discovery.build('calendar', 'v3', http=http)
	drv_service = discovery.build('drive', 'v2', http=http)

	# Uncomment to list all calendars avaiable
	#page_token = None
	#while True:
	#	calendar_list = service.calendarList().list(pageToken=page_token).execute()
	#	for calendar_list_entry in calendar_list['items']:
	#		print (calendar_list_entry['summary'] + ' - ' + calendar_list_entry['id'])
	#	page_token = calendar_list.get('nextPageToken')
	#	if not page_token:
	#		break

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
		
		print ('Uploading to Drive')
		fileup = upload_media (drv_service, title='Journal at ' + now, description='Journal at ' + now, filepath = journalfile_path, mime_type = "text/plain", resumable=False)
		alt_filelink = fileup['alternateLink']
		print ('File uploaded to ' + alt_filelink)
		
		print ('Creating entry ' + now)
		event = add_event (cal_service,
				cal_id='e4unln1q7f9d3gjomqtmca94pc@group.calendar.google.com',
				summary = 'Entry ' + now, description = ' '.join(taglist), start_time=now, end_time=now, has_attachment=True, attachment_url=alt_filelink)
		print ('Entry created.')
	else: print ('No entry created.')

	if os.path.isfile(journalfile_path):
		print ('Removing temporary local file ' + journalfile_path)
		call(['rm', '-f', journalfile_path])

if __name__ == '__main__':
	main()
