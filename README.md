# snapshot-final
This repo contains the files to run Snapshot. Note that the files themselves will not run without generating your own Oauth credentials, but the function of each of these is listed below.  

**Snapshot.py**: all the code for generating the dashboard (including user inputs and displays), calling calStart for calendar information and calling insert_event for putting an event in the calendar for the next day. 

**calStart.py**: handles the API Google Calendar pull. Loops through each of the user's calendars and lists all events from the day. Returns the events as a list, the events as a string, and the number of events. 

**insert_event.py**: handles API Google Calendar event creation. Uses argument "description" with string from calStart to create an event for the next day with that description. 

**snapshot_logo_2.png**: logo for the dashboard
