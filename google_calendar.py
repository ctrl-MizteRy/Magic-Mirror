import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from greeting import Start_Speaking

class Google_Cal:
    weekdays_map = ("Monday", "Tuesday", 
                   "Wednesday", "Thursday",
                   "Friday", "Saturday",
                   "Sunday")
    months_map = ("January", "Febuary", "March", "April", "May",
                  "June", "July", "August", "September",
                  "October", "November", "December")
    def __init__(self):
        try:
            SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
            self.creds = None
            if os.path.exists("token.json"):
                self.creds = Credentials.from_authorized_user_file("token.json", SCOPES)
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        "credentials.json", SCOPES
                    )
                    self.creds = flow.run_local_server(port=8888)
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())
            self.events = self.get_events()
            self.speak = Start_Speaking()
            self.today_events()
            self.next_7_days()
            self.tomorrow_events()
        except ConnectionError:
            os.remove('token.json')
            self.__init__()
    

    def get_events(self) -> list[dict]:
        while True:
            try:
                service = build("calendar", "v3", credentials=self.creds)
                now = datetime.datetime.now(datetime.timezone.utc).isoformat()
                events_result = (
                    service.events()
                    .list(
                        calendarId="primary",
                        timeMin=now,
                        maxResults=30,
                        singleEvents=True,
                        orderBy="startTime",
                    )
                    .execute()
                )
                events = events_result.get("items", [])
                
                if not events:
                    return [{}]
                return events
            except HttpError as error:
                print(f"Error happened during requesting calendar events: {error}")
            except ConnectionError:
                self.__init__()
    
    def today_events(self) -> None:
        self.today = datetime.datetime.now().strftime("%Y-%m-%d")
        right_now = (datetime.datetime.now().strftime("%H:%M")).split(":")
        schedule = ["Here are the schedules for today:\n"]
        for event in self.events:
            start = event["start"].get("dateTime")
            end = event["end"].get("dateTime")
            start_date, start_time = start.split("T")
            if start_date != self.today:
                break
            end_date, end_time = end.split("T")
            if int(end_time.split(":")[0]) <= int(right_now[0]): #If the event already ended
                if int(end_time.split(":")[0]) < int(right_now[0]) : continue
                elif int(end_time.split(":")[-1]) < int(right_now[1]): continue
            if start_date == end_date:
                schedule.append(f"At {start_time[0:5]} hours, you have an event called {event["summary"]}{" with the description of " + event["description"] if "description" in event.keys() else ""} "
                                f" until {end_time[0:5]} hours.\n")
            else:
                schedule.append(f"At {start_time[0:5]} hours, you have an event called {event["summary"]}{" with the description of " + event["description"] if "description" in event.keys() else ""} "
                                f" until {self.weekdays_map[datetime.datetime.weekday(end_date)]} of {self.months_map[int(self.today.split("-")[1]) - 1]} {self.today.split("-")[-1]} at {end_time} hours.\n")
            
            if len(schedule) < 2:
                self.speak.normal_speed("There is no events happening in the calendar today", "voice_records/today_schedule.mp3")
            else:
                text = "".join(schedule)
                self.speak.normal_speed(text, "voice_records/today_schedule.mp3")
    
    def next_7_days(self) -> None:
        date = ((datetime.datetime.now() + datetime.timedelta(7)).strftime("%y-%m-%d")).split("-")
        if not self.events:
            self.speak.normal_speed("There is no events happening for the next 7 days.", "voice_records/next_7_days_calendar.mp3")
        else:
            schedule = ["Here are the schedule for the next 7 days:\n"]
            for event in self.events:
                start = event["start"].get("dateTime")
                end = event["end"].get("dateTime")
                start_date, start_time = start.split("T")
                s_year, s_month, s_day = start_date.split("-")
                if start_date == self.today: continue
                if int(date[1]) <= int(s_month):
                    if int(date[1]) == int(s_month) and int(date[2]) < int(s_day): break
                end_date, end_time = end.split("T")
                e_year, e_month, e_day = end_date.split("-")
                if start_date == end_date:
                    schedule.append(f"On {self.weekdays_map[datetime.datetime.weekday(datetime.date(int(s_year), int(s_month), int(s_day)))]} at {start_time[0:5]}, you have an event called {event["summary"]}{" with the description of " + event["description"] if "description" in event.keys() else ""} "
                                f" until {end_time[0:5]} hours.\n")
                else:
                    schedule.append(f"On {self.weekdays_map[datetime.datetime.weekday(datetime.date(int(s_year), int(s_month), int(s_day)))]} at {start_time[0:5]} hours, you have an event called {event["summary"]}{" with the description of " + event["description"] if "description" in event.keys() else ""} "
                                    f" until {self.weekdays_map[datetime.datetime.weekday(datetime.date(int(e_year), int(e_month), int(e_day)))]} of {self.months_map[int(self.today.split("-")[1]) - 1]} {self.today.split("-")[-1]} at {end_time} hours.\n")
            
            text = "".join(schedule)
            self.speak.normal_speed(text, "voice_records/next_7_days_calendar.mp3")

    def tomorrow_events(self):
        tomorrow = (datetime.datetime.now() + datetime.timedelta(1)).strftime('%Y-%m-%d')
        schedule = ["Here are tomorrow schedule: \n"]
        for event in self.events:
            start = event["start"].get("dateTime")
            end = event["end"].get("dateTime")
            end_date, end_time = end.split("T")
            start_date, start_time = start.split("T")
            if start_date != tomorrow: continue
            else:
                if start_date == end_date:
                    schedule.append(f"At {start_time[0:5]} hours, you have an event called {event["summary"]}{" with the description of " + event["description"] if "description" in event.keys() else ""} "
                                    f" until {end_time[0:5]} hours.\n")
                else:
                    schedule.append(f"At {start_time[0:5]} hours, you have an event called {event["summary"]}{" with the description of " + event["description"] if "description" in event.keys() else ""} "
                                    f" until {self.weekdays_map[datetime.datetime.weekday(end_date)]} of {self.months_map[int(self.today.split("-")[1]) - 1]} {self.today.split("-")[-1]} at {end_time} hours.\n")
                
        if len(schedule) < 2:
            self.speak.normal_speed("There is no events happening in the calendar tomorrow", "voice_records/tomorrow_schedule.mp3")
        else:
            text = "".join(schedule)
            self.speak.normal_speed(text, "voice_records/tomorrow_schedule.mp3")

    def get_today_events(self):
        event_start, event_end, event_end_date, title = [], [] ,[], []
        for event in self.events:
            start = event["start"].get("dateTime")
            end = event["end"].get("dateTime")
            end_date, end_time = end.split("T")
            start_date, start_time = start.split("T")
            if start_date != self.today: break
            else:
                event_start.append((start_time.split("-"))[0][:5])
                event_end.append((end_time.split("-"))[0][:5])
                event_end_date.append(end_date if end_date != start_date else " ")
                title.append(event['summary'])
        return [event_start, event_end, event_end_date, title]
    