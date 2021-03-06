import discord
from discord.ext import commands
import os
import datetime
import json
from __main__ import send_cmd_help
from .utils.dataIO import fileIO

#-------Google Calendar Imports-------#
from apiclient import discovery
import httplib2
import oauth2client
from cogs.utils import checks
from cogs.utils.dataIO import fileIO
from oauth2client import client
from oauth2client import tools

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

#-----------------------------------Event Listing-----------------------------------#

	async def events_today(self):

		time_min = datetime.date.today()
		time_max = time_min
		await self.print_events(time_min, time_max)

	async def events_tomorrow(self):

		time_min = datetime.date.today() + datetime.timedelta(days=1)
		time_max = time_min
		await self.print_events(time_min, time_max)

	async def events_this_week(self):

		time_min = datetime.date.today() - datetime.timedelta(datetime.datetime.today().weekday())
		time_max = time_min + datetime.timedelta(days=6)
		await self.print_events(time_min, time_max)

	async def events_next_week(self):

		time_min = (datetime.date.today() - datetime.timedelta(datetime.datetime.today().weekday())) + datetime.timedelta(days=7)
		time_max = time_min + datetime.timedelta(days=6)
		await self.print_events(time_min, time_max)

	async def events_range(self, start_date, end_date):

		try:
			datetime.datetime.strptime(start_date, '%Y-%m-%d')
		except ValueError:
			await self.bot.say("Use the format YYYY-MM-DD.")
			return

		try:
			datetime.datetime.strptime(end_date, '%Y-%m-%d')
		except ValueError:
			await self.bot.say("Use the format YYYY-MM-DD.")
			return

		time_min = start_date
		time_max = end_date
		await self.print_events(time_min, time_max)

#-----------------------------------Admin Actions-----------------------------------#

	async def list_cals(self):

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
			await self.bot.say("```" + "\n" + "Use [p]gcalendat setcal 'Calendar ID' to change the active calendar." + "\n" +
							"You can also use [p]gcalendar setcal primary to use the default calendar" + "\n" + "```")
					
			page_token = calendar_list.get('nextPageToken')
			
			if not page_token:
				break

	async def set_cal(self, ctx, calendar_ID):

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
				calIDList.append('primary')
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
				await self.bot.say("No changes have been made to the active calendar.")
				return

			elif "yes" not in answer.content.lower():
				await self.bot.say("No changes have been made to the active calendar.")
				return
				
			self.settings['cal_id'] = calendar_ID
			fileIO("data/gcalendar/settings.json", "save", self.settings)

			await self.bot.say("Active calendar is now set to: " + self.settings['cal_id'])

#-----------------------------------Print Function-----------------------------------#

	async def print_events(self, time_min, time_max):

		if time_min > time_max:
			await self.bot.say("The start of your range must be ***BEFORE***  the end date.")
			return

		start = str(time_min) + "T00:00:00Z"
		end = str(time_max) + "T23:59:00Z"

		credentials = get_creds()
		http = credentials.authorize(httplib2.Http())
		service = discovery.build('calendar', 'v3', http=http)
		
		eventsResult = service.events().list(
			calendarId=self.settings['cal_id'], timeMin=start, timeMax=end, maxResults=37, singleEvents=True,
			orderBy='startTime').execute()
		events = eventsResult.get('items', [])
		eventList = []
		
		if not events:
			await self.bot.say("No upcoming events found.")
			
		elif events:	
				for event in events:
					start = event['start'].get('dateTime', event['start'].get('date'))
					ev_summary = event['summary']

					if len(ev_summary) > 31:
						ev_format = str(ev_summary[0:31]) + str("...")						
					
					elif len(ev_summary) < 31:
						ev_format = ev_summary

					if 'T' and '+' in start:
						startformat = start.replace('T', ' │ ').replace('+', ' │ +')
						ev_summary = event['summary']
						eventList.append("│ " +startformat + "  │ " + ev_format)
					
					elif 'T' and 'Z' in start:
						startformat = start.replace('T', ' │ ').replace('Z', ' │ ALL-DAY │ ')
						ev_summary = event['summary']
						eventList.append("│ " +startformat + ev_format)

					elif 'T' and '+' not in start:
						ev_summary = event['summary']
						eventList.append("│ " + start + " │ ALL-DAY  │ ALL-DAY │ " + ev_format)

				if ((len(str(eventList))) - len(eventList)) < 1950:
					await self.bot.say("```" + "\n" + "| Date       | Time     | UTC     | Event" + "\n" 
						+ "├────────────┼──────────┼─────────┼────────────────────────────────────"
						+ "\n" + "\n".join(eventList) + "\n" + "```")
					return

				elif ((len(str(eventList))) - len(eventList)) > 1950:
					await self.bot.say("Returned too many results please use a shorter range or try [p]gcalendar between.")

#-----------------------------------Sub Command Setup-----------------------------------#

	@commands.group(no_pm=True, pass_context=True)
	async def gcalendar(self, ctx):
		if ctx.invoked_subcommand is None:
			await send_cmd_help(ctx)
			return

#-----------------------------------Event Listing-----------------------------------#

	@gcalendar.command(pass_context=True, name="today")
	async def gcalendar_eventstoday(self):
		"""List events for today
		"""

		await self.events_today()

	@gcalendar.command(pass_context=True, name="tomorrow")
	async def gcalendars_eventstomorrow(self):
		"""List events for tomorrow
		"""

		await self.events_tomorrow()

	@gcalendar.command(pass_context=True, name="thisweek")
	async def gcalendar_eventsthisweek(self):
		"""Show events for this week
		"""

		await self.events_this_week()

	@gcalendar.command(pass_context=True, name="nextweek")
	async def gcalendar_eventsnextweek(self):
		"""Show events for next week
		"""

		await self.events_next_week()

	@gcalendar.command(pass_context=True, name="between")
	async def gcalendar_range(self, ctx, start_date, end_date):
		"""Show events between two dates.

		Date format: YYYY-MM-DD
		"""

		await self.events_range(start_date, end_date)

#-----------------------------------Admin Actions-----------------------------------#

	@checks.mod_or_permissions(manage_messages=True)
	@gcalendar.command(pass_context=True, name="listcals")
	async def gcalendar_listcals(self):
		"""List available calendars
		"""

		await self.list_cals()

	@checks.mod_or_permissions(manage_messages=True)
	@gcalendar.command(pass_context=True, no_pm=True, name="setcal")
	async def gcalendar_setcal(self, ctx, calendar_ID):
		"""Change the active calendar. 

		Get the ID from [p]gcalendar listcals
		"""

		await self.set_cal(ctx, calendar_ID)

#-----------------------------------Setup-----------------------------------#

def get_creds():
	"""Gets valid user credentials from storage.
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