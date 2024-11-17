import datetime as dt
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def main():
  """Shows basic usage of the Google Calendar API.
  Prints the start and summary of the events for the day.
  """

  #### CREDENTIAL CHECKING ###
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
    now = dt.datetime.today() 
    start_of_day = dt.datetime.combine(now, dt.time.min).isoformat() + ".00000Z"
    end_of_day = dt.datetime.combine(now, dt.time.max).isoformat() + "Z"
    #print(start_of_day)
    #print(end_of_day)


    #### ACTUAL CALENDAR PULL: CALENDAR LIST ####
    #print("Getting the events of the day")

    #Get list of all calendars for the user
    calendars = service.calendarList().list().execute()
    
    #get the items from the calendar pull
    calendars_list = calendars.get("items", [])
    calendar_ids = [calendars_list[i]['id'] for i in range(len(calendars_list))]

    #### ACTUAL CALENDAR PULL: CALENDAR EVENTS ####
    all_events = {'start': [],
                  'summary':[]}
    num_events = 0

    #loop through calendars and get the events from each calendar 
    for id in calendar_ids:
      events_result = (
        service.events()
        .list(
          calendarId=id,
          timeMin=start_of_day,
          timeMax=end_of_day,
          singleEvents=True,
          orderBy="startTime",
          )
          .execute()
          )
      events = events_result.get("items", [])
      #print(len(events))
      if not events:
        continue
      else:
        for e in events:
          start = e["start"].get("dateTime", e["start"].get("date"))
          if start < str(dt.datetime.today()):
            continue
          all_events['start'].append(start)
          summary = e["summary"]
          all_events['summary'].append(summary)
          num_events += 1 

    ### MAKE THE FORMAT NICE ###
    #Format 1:
    #formatted_events = ""
    #for st, sum in zip(all_events['start'], all_events['summary']):
    #  formatted_events += f"{st} : {sum}\n,"
    #
    #if num_events == 0:
    #  formatted_events = 'No events today'

    #Format 2: 
    formatted_events = ''
    for summary_item in all_events['summary']:
      formatted_events += f'{summary_item}, '
    

    return all_events, formatted_events[:-2], num_events

    
    

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  today, format, n = main()
  #print(format, n)


