import discord
from discord.ext import commands
import os
import datetime
from apiclient import discovery
import httplib2
import oauth2client
import json
from cogs.utils import checks
from cogs.utils.dataIO import fileIO
from oauth2client import client
from oauth2client import tools
from .utils.dataIO import fileIO

try:
	import argparse
	flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
	flags = None

"""If modifying these scopes, delete your previously saved credentials"""
"""at ~/.credentials/calendar-python-quickstart.json"""

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'data/gcalendar/client_secret.json'

class gcalender:
	"""Connect your Google Calender with Discord!"""

	def __init__(self, bot):
		self.bot = bot
		self.settings = fileIO("data/gcalendar/settings.json", "load")

	async def _ten_apps(self):
		"""List events for today
		"""

		credentials = get_creds()
		http = credentials.authorize(httplib2.Http())
		service = discovery.build('calendar', 'v3', http=http)
		now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
		
		eventsResult = service.events().list(
			calendarId=self.settings['cal_id'], timeMin=now, maxResults=10, singleEvents=True,
			orderBy='startTime').execute()
		events = eventsResult.get('items', [])
		eventList = []
		
		if not events:
			self.bot.say("No upcoming events found.")
			
		for event in events:
			start = event['start'].get('dateTime', event['start'].get('date'))
			ev_summary = event['summary']
			eventList.append(start + " " + ev_summary)

	@commands.group(no_pm=True, pass_context=True)
	@checks.mod_or_permissions(manage_messages=True)
	async def gcalendar(self, ctx):
		if ctx.invoked_subcommand is None:
			await self.bot.say("Error")
			return

	@gcalendar.command(pass_context=True, name="tenapps")
	async def _gcalendar_tenapps(self):

		await self.bot._ten_apps(self)
		await self.bot.say("```" + "\n" + "\n".join(eventList) + "\n" + "```")

	@commands.command()
	async def tenapps2(self):
		"""List events for today
		"""

		credentials = get_creds()
		http = credentials.authorize(httplib2.Http())
		service = discovery.build('calendar', 'v3', http=http)
		now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
		
		eventsResult = service.events().list(
			calendarId=self.settings['cal_id'], timeMin=now, maxResults=10, singleEvents=True,
			orderBy='startTime').execute()
		events = eventsResult.get('items', [])
		eventList = []
		
		if not events:
			self.bot.say("No upcoming events found.")
			
		for event in events:
			start = event['start'].get('dateTime', event['start'].get('date'))
			ev_summary = event['summary']
			eventList.append(start + " " + ev_summary)

		await self.bot.say("```" + "\n" + "\n".join(eventList) + "\n" + "```")
						
	@commands.command()
	async def eventstoday(self):
		"""List events for today
		"""

		todaydate = datetime.date.today()
		today0h = str(todaydate) + "T00:00:00Z"
		today23h = str(todaydate) +  "T23:59:59Z"
		credentials = get_creds()
		http = credentials.authorize(httplib2.Http())
		service = discovery.build('calendar', 'v3', http=http)

		eventsResult = service.events().list(
			calendarId=self.settings['cal_id'], timeMin=today0h, timeMax=today23h, maxResults=20, singleEvents=True,
			orderBy='startTime').execute()
		events = eventsResult.get('items', [])
		eventList = []
		
		if not events:
			await self.bot.say("No events found for today.")

		for event in events:
			start = event['start'].get('dateTime', event['start'].get('date'))
			ev_summary = event['summary']
			eventList.append(start + " " + ev_summary)

		await self.bot.say("```" + "\n" + "\n".join(eventList) + "\n" + "```")
			
	@commands.command()
	async def eventstomorrow(self):
		"""List events for tomorrow
		"""

		tomorrowdate = datetime.date.today() + datetime.timedelta(days=1)
		tomorrow0h = str(tomorrowdate) + "T00:00:00Z"
		tomorrow23h = str(tomorrowdate) +  "T23:59:59Z"
		credentials = get_creds()
		http = credentials.authorize(httplib2.Http())
		service = discovery.build('calendar', 'v3', http=http)

		eventsResult = service.events().list(
			calendarId=self.settings['cal_id'], timeMin=tomorrow0h, timeMax=tomorrow23h, maxResults=10, singleEvents=True,
			orderBy='startTime').execute()
		events = eventsResult.get('items', [])
		eventList = []
		
		if not events:
			await self.bot.say("No events found for tomorrow.")

		for event in events:
			start = event['start'].get('dateTime', event['start'].get('date'))
			ev_summary = event['summary']
			eventList.append(start + " " + ev_summary)

		await self.bot.say("```" + "\n" + "\n".join(eventList) + "\n" + "```")

	@commands.command()
	async def listcals(self):
		"""Show active calendar and available calendars
		"""

		await self.bot.say("The active calendar is: " + self.settings['cal_id'] + ".")
		await self.bot.say("Printing list of available calendars and thier IDs...")		
		page_token = None

		while True:
			credentials = get_creds()
			http = credentials.authorize(httplib2.Http())
			service = discovery.build('calendar', 'v3', http=http)
			calendar_list = service.calendarList().list(pageToken=page_token).execute()
			calList = []
			calIDList = []
			for calendar_list_entry in calendar_list['items']:
				cal_names = calendar_list_entry['summary']
				cal_ids = calendar_list_entry['id']
				cal_perms = calendar_list_entry['accessRole']
				calList.append("Calendar Name: " + str(cal_names) + "\n" + 
					"Calendar ID: " + str(cal_ids) + "\n" + "Permission Level: " + str(cal_perms) + "\n")
				calIDList.append(str(cal_ids))
				
			await self.bot.say("```" + "\n" + "\n".join(calList) + "\n" + "```")
			await self.bot.say("```" + "\n" + "Use [p]setcal 'Calendar ID' to change the active calendar." + "\n" + "```")
					
			page_token = calendar_list.get('nextPageToken')
			if not page_token:
				break

	@commands.command(pass_context=True, no_pm=True)
	async def setcal(self, ctx, calendar_ID):
		"""Change the active calendar. Get the ID from [p]listcals
		"""

		page_token = None

		while True:
			credentials = get_creds()
			http = credentials.authorize(httplib2.Http())
			service = discovery.build('calendar', 'v3', http=http)
			calendar_list = service.calendarList().list(pageToken=page_token).execute()
			calIDList = []

			for calendar_list_entry in calendar_list['items']:
				cal_ids = calendar_list_entry['id']
				calIDList.append(str(cal_ids))
			page_token = calendar_list.get('nextPageToken')
			if not page_token:
				break
		
		if calendar_ID not in calIDList:
			await self.bot.say("That ID doesn't match any you have access to.")
			return

		elif calendar_ID in calIDList:
			await self.bot.say("Do you want to change the active calendar to '" + str(calendar_ID) + "'? (yes/no)")
			answer = await self.bot.wait_for_message(timeout=15, author=ctx.message.author)
			
			if answer is None:
				await self.bot.say("No changes made to active calendar.")
				return

			elif "yes" not in answer.content.lower():
				await self.bot.say("No changes made to active calendar.")
				return
				
			self.settings['cal_id'] = calendar_ID
			fileIO("data/gcalendar/settings.json", "save", self.settings)
			await self.bot.say("Active calendar is now set to: " + self.settings['cal_id'])

def get_creds():
	"""Gets valid user credentials from storage.

	If nothing has been stored, or if the stored credentials are invalid,
	the OAuth2 flow is completed to obtain the new credentials.

	Returns:
		Credentials, the obtained credential.
	"""

	credential_dir = os.path.join('data/GCalendar/creds', '.credentials')
	if not os.path.exists(credential_dir):
		os.makedirs(credential_dir)
	credential_path = os.path.join(credential_dir,
								   'calendar-python-quickstart.json')

	store = oauth2client.file.Storage(credential_path)
	credentials = store.get()
	if not credentials or credentials.invalid:
		flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
		flow.user_agent = self.settings['app_name']
		if flags:
			credentials = tools.run_flow(flow, store, flags)
		else: # Needed only for compatibility with Python 2.6
			credentials = tools.run(flow, store)
		print('Storing credentials to ' + credential_path)
	return credentials

def check_folders():
	if not os.path.exists("data/GCalendar"):
		print("Creating data/GCalendar folder...")
		os.makedirs("data/GCalendar")

def check_settings():
	settings = {"app_name" : "Put your application name here!", "cal_id" : "primary"}

	f = "data/GCalendar/settings.json"
	if not fileIO(f, "check"):
		print("Creating settings.json")
		print("Setup Google API and Application")
		fileIO(f, "save", settings)

def check_client():
	if not os.path.isfile('data/gcalendar/client_secret.json'):
		print("You need to get an API key from: https://console.developers.google.com/start/api?id=calendar")
		print("Then follow step 1 on this page and save client_secret in 'data/gcalender'")

def setup(bot):
	check_folders()
	check_settings()
	get_creds()
	n = gcalender(bot)
	bot.add_cog(n)