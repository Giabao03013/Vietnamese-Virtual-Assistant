from __future__ import print_function

from dateutil.parser import parse as dtparse
import os.path
import isodate

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from Get_date import *
SCOPES = ['https://www.googleapis.com/auth/calendar.events']


def get_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('calendar', 'v3', credentials=creds)
    return service
def see_event_of_weekmonth(dates,service):
    msg = ''
    list_event = []
    for day in dates:
        day = datetime.datetime.strptime(day, '%d-%m-%Y')
        date = datetime.datetime.combine(day, datetime.datetime.min.time())
        end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
        utc = pytz.UTC
        date = date.astimezone(utc)
        end_date = end_date.astimezone(utc)
        events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(),
                                              timeMax=end_date.isoformat(),
                                              singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items',[])

        if events:
            for event in events:
                list_event.append(event)

    if not list_event:
        msg += 'Lịch của bạn hoàn toàn trống'
    else:
        msg += f'Lịch của bạn như sau:' + '\n'
        for event in list_event:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['start'].get('date'))
            date = datetime.datetime.strftime(dtparse(start), format='%Y-%m-%d')
            date = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d-%m-%Y')
            start = isodate.parse_datetime(start)
            end = isodate.parse_datetime(end)

            if 'location' not in event:
                msg += f'Ngày {date}, {event["summary"]} bắt đầu từ {start.strftime("%I:%M %p")} đến {end.strftime("%I:%M %p")} ' + '\n'
            else:
                msg += f'Ngày {date}, {event["summary"]} bắt đầu từ {start.strftime("%I:%M %p")} đến {end.strftime("%I:%M %p")} tại {event["location"]}' + '\n'
    return msg

def see_event_all_day(day,service):
    day  = datetime.datetime.strptime(day,'%d-%m-%Y')
    date = datetime.datetime.combine(day,datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day,datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)
    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax = end_date.isoformat(),
                                        singleEvents=True,orderBy='startTime').execute()
    events = events_result.get('items', [])
    if not events:
        msg = f'Lịch của bạn vào ngày {day.strftime("%d-%m-%Y")} hoàn toàn trống'
    else :
        msg = f'Lịch của bạn trong ngày {day.strftime("%d-%m-%Y")} như sau:' + '\n'
        i = 1
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['start'].get('date'))
            start = isodate.parse_datetime(start)
            end = isodate.parse_datetime(end)
            if 'location' not in event:
                msg += f'{i}. {event["summary"]} bắt đầu từ {start.strftime("%I:%M %p")} đến {end.strftime("%I:%M %p")} '+ '\n'
            else:
                msg += f'{i}. {event["summary"]} bắt đầu từ {start.strftime("%I:%M %p")} đến {end.strftime("%I:%M %p")} tại {event["location"]}' + '\n'
            i += 1
    return msg
def see_event_of_part_day(token,day,service):
    utc = pytz.UTC
    msg = ''
    part ={'morning':'Buổi sáng','afternoon':'Buổi trưa','evening':'Buổi chiều','night':'Buổi tối'}
    if token == 'morning':
        date = datetime.datetime.strptime(day, '%d-%m-%Y')
        start = (date + datetime.timedelta(hours=6, minutes=00))
        end = (date + datetime.timedelta(hours=11, minutes=59))
        start = start.astimezone(utc)
        end = end.astimezone(utc)
        events_result = service.events().list(calendarId='primary', timeMin=start.isoformat(), timeMax=end.isoformat(),
                                         singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            msg += f'{part[token]} hoàn toàn trống \n'
        else:
            msg += f'{part[token]} có các hoạt động sau:' + '\n'
            i = 1
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['start'].get('date'))
                start = isodate.parse_datetime(start)
                end = isodate.parse_datetime(end)
                msg += f'{i}. {event["summary"]} bắt đầu từ {start.strftime("%I:%M %p")} đến {end.strftime("%I:%M %p")} \n'
                i += 1
    if token == 'afternoon':
        date = datetime.datetime.strptime(day, '%d-%m-%Y')
        start = (date + datetime.timedelta(hours=12, minutes=00))
        end = (date + datetime.timedelta(hours=16, minutes=59))
        start = start.astimezone(utc)
        end = end.astimezone(utc)
        events_result = service.events().list(calendarId='primary', timeMin=start.isoformat(), timeMax=end.isoformat(),
                                              singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            msg += f'{part[token]} hoàn toàn trống \n'
        else:
            msg += f'{part[token]} có các hoạt động sau:' + '\n'
            i = 1
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['start'].get('date'))
                start = isodate.parse_datetime(start)
                end = isodate.parse_datetime(end)
                msg += f'{i}. {event["summary"]} bắt đầu từ {start.strftime("%I:%M %p")} đến {end.strftime("%I:%M %p")} \n'
                i += 1
    if token == 'evening':
        date = datetime.datetime.strptime(day, '%d-%m-%Y')
        start = (date + datetime.timedelta(hours=17, minutes=00))
        end = (date + datetime.timedelta(hours=19, minutes=59))
        start = start.astimezone(utc)
        end = end.astimezone(utc)
        events_result = service.events().list(calendarId='primary', timeMin=start.isoformat(), timeMax=end.isoformat(),
                                              singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            msg += f'{part[token]} hoàn toàn trống \n'
        else:
            msg += f'{part[token]} có các hoạt động sau:' + '\n'
            i = 1
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['start'].get('date'))
                start = isodate.parse_datetime(start)
                end = isodate.parse_datetime(end)
                msg += f'{i}. {event["summary"]} bắt đầu từ {start.strftime("%I:%M %p")} đến {end.strftime("%I:%M %p")} \n'
                i += 1
    if token =='night':
        date = datetime.datetime.strptime(day, '%d-%m-%Y')
        start = (date + datetime.timedelta(hours=20, minutes=00))
        end = (date + datetime.timedelta(hours=23, minutes=59))
        start = start.astimezone(utc)
        end = end.astimezone(utc)
        events_result = service.events().list(calendarId='primary', timeMin=start.isoformat(), timeMax=end.isoformat(),
                                              singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            msg += f'{part[token]} hoàn toàn trống \n'
        else:
            msg += f'{part[token]} có các hoạt động sau:' + '\n'
            i = 1
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['start'].get('date'))
                start = isodate.parse_datetime(start)
                end = isodate.parse_datetime(end)
                msg += f'{i}. {event["summary"]} bắt đầu từ {start.strftime("%I:%M %p")} đến {end.strftime("%I:%M %p")}' + '\n'
                i += 1
    return msg


def list_event(day,service):
    day = datetime.datetime.strptime(day, '%d-%m-%Y')
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)
    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                          singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events

def get_all_of_event(eventid,service):
    event = service.events().get(calendarId='primary', eventId=eventid).execute()
    summary = event['summary']
    start = event['start'].get('dateTime', event['start'].get('date'))
    end = event['end'].get('dateTime', event['start'].get('date'))
    date  = datetime.datetime.strftime(dtparse(start),format='%Y-%m-%d')
    date = datetime.datetime.strptime(date,'%Y-%m-%d').strftime('%d-%m-%Y')
    start = isodate.parse_datetime(start).strftime("%I:%M %p")
    end = isodate.parse_datetime(end).strftime("%I:%M %p")
    location = event['location']
    list = [summary,start,end,location,date]
    return list

def add_event(date,time_start,time_end,summary,location,service):
    time_start = get_datetime(date,time_start)
    time_end = get_datetime(date,time_end)
    time_start = time_start.isoformat()
    time_end = time_end.isoformat()
    event = {
        'summary': summary,
        'location': location,
        'description': '',
        'start': {
            'dateTime': time_start,
            'timeZone': 'Asia/Ho_Chi_Minh',
        },
        'end': {
            'dateTime': time_end,
            'timeZone': 'Asia/Ho_Chi_Minh',
        },
        'recurrence': [
            'RRULE:FREQ=DAILY;COUNT=1'
        ],
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    msg = 'Lịch làm việc của bạn đã được thêm vào'
    return msg

def check_time(input):
    try:
        datetime.datetime.strptime(input, '%I:%M %p')
        return True
    except ValueError:
        return False

Service = get_service()

def get_datetime(date,time):
    date = datetime.datetime.strptime(date,'%d-%m-%Y')
    time = datetime.datetime.strptime(time,'%I:%M %p')
    date = date + datetime.timedelta(hours=time.hour,minutes= time.minute)
    return date


def check_exist(timestart,timeend,service):
    utc = pytz.UTC
    date = timestart.astimezone(utc)
    end_date = timeend.astimezone(utc)
    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(),
                                          timeMax=end_date.isoformat(),
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    if not events:
        return True
    else:
        return False


def update_event(date,time_start,time_end,summary,location,eventid,service):
    time_start = get_datetime(date, time_start)
    time_end = get_datetime(date, time_end)
    time_start = time_start.isoformat()
    time_end = time_end.isoformat()
    event = service.events().get(calendarId='primary', eventId=eventid).execute()
    event['summary'] = summary
    event['start']['dateTime']= time_start
    event['end']['dateTime'] = time_end
    event['location'] = location
    update = service.events().update(calendarId='primary',eventId=eventid, body=event).execute()
    msg = 'Sự kiện của bạn đã được thay đổi'
    return msg


def compare(first, second):
    sharedKeys = set(first.keys()).intersection(second.keys())
    diff = []
    for key in sharedKeys:
        if first[key] != second[key]:
            diff.append(key)
    return diff

def del_event(eventid,service):
    service.events().delete(calendarId='primary', eventId=eventid).execute()

