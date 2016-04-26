

import discord
from discord.ext import commands
import os
import datetime
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

class GCalender:
    """Connect your Google Calender with Discord!"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tenapps(self):
        """Get the next 10 appointments"""


        await self.bot.say("I can do stuff!")

	def get_creds():
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
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def setup(bot):
	get_creds()
	n = GCalendar(bot)
	bot.add_cog(n)