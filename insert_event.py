import datetime as dt
import os.path
import calStart

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def main(description = ''):
  """Shows basic usage of the Google Calendar API.
  Prints the start and summary of the events for the day.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:

    #### CONNECTION CREATION ####
    #creates the object which will be called upon to get events() as a list()
        service = build("calendar", "v3", credentials=creds)

    ##### DEFINE THE START AND END TIMES ####
    ## now + dt.timedelta adds one day so that the event will go into the next day
        now = dt.datetime.today() + dt.timedelta(days = 1) 
        start_of_day = dt.datetime.combine(now, dt.time(22,0)).isoformat() + ".00000Z"
        end_of_day = dt.datetime.combine(now, dt.time(23,0)).isoformat() + "Z"


        event = {
            'summary': 'Journaling Time',
            'location': 'Home',
            'description': description,
            'start': {
              'dateTime': start_of_day,
              'timeZone': 'America/Los_Angeles',
            },
            'end': {
              'dateTime': end_of_day,
            'timeZone': 'America/Los_Angeles',
            },
            'reminders': {
              'useDefault': False,
              'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
                    ],
                    },
                }

        event = service.events().insert(calendarId='primary', body=event).execute()
        #print 'Event created: %s' % (event.get('htmlLink'))

  except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
   main()
  #todays_description, nice_format, n_events = calStart.main()
  #print(todays_description)
  #main(description = nice_format)
