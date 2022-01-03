from Get_date import summary_date
from Event import *
from weather import *
from Get_time import *
import webbrowser
import requests
from vietnam_number import w2n
from googletrans import Translator
from typing import Any, Text, Dict, List, Optional
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, EventType, AllSlotsReset
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict

Service = get_service()


###                                     SEE EVENT ACTION
class ActionGetDate(Action):
    def name(self) -> Text:
        return "action_see_event"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        chatbot_msg = ''
        msg = tracker.latest_message.get('text')
        date = summary_date(msg)
        part_token = tokenize_2(msg,file='data/part_of_date.json')
        if len(date)>=7:
            msg = see_event_of_weekmonth(date,Service)
            dispatcher.utter_message(text=msg)
        elif not part_token:
            for day in date:
                chatbot_msg += see_event_all_day(day, Service) + '\n'
            dispatcher.utter_message(text=f"{chatbot_msg}")
        else:
            if len(date) == 1:
                if len(part_token) == 1:
                    chatbot_msg += f'Ngày {date[0]}: \n'
                    tok_key = list(part_token[0].keys())
                    chatbot_msg += see_event_of_part_day(tok_key[0], date[0], Service)
                else:
                    chatbot_msg = f'Ngày {date[0]}: \n'
                    for token in part_token:
                        tok_key = list(token.keys())
                        chatbot_msg += see_event_of_part_day(tok_key[0], date[0], Service)
                dispatcher.utter_message(text=chatbot_msg)
            else:
                tok_key = list(part_token[0].keys())
                for d in date:
                    chatbot_msg += see_event_of_part_day(tok_key, d, Service)
                dispatcher.utter_message(text=chatbot_msg)
        return []


###                                             ADD EVENT FORM

class ActionSubmit(Action):
    def name(self) -> Text:
        return "action_submit"

    async def run(
    self,
    dispatcher,
    tracker: Tracker,
    domain: "DomainDict" ):
            Date=tracker.get_slot("date")
            Summary=tracker.get_slot("summary")
            Start_time=tracker.get_slot('start_time')
            End_time=tracker.get_slot('end_time')
            Location=tracker.get_slot('location')
            dispatcher.utter_message(text=f'Bạn cần thêm hoạt động {Summary} vào ngày {Date} từ {Start_time} đến {End_time} tại {Location}' + '\n'
                                          + 'Đúng Không')


class ActionYesConfirm(Action):
    def name(self) -> Text:
        return "action_say_yes"

    async def run(
            self,
            dispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[EventType]:
        dispatcher.utter_message(text='Ok bạn đợi mình chút nha')
        Date = tracker.get_slot('date')
        Summary = tracker.get_slot('summary')
        Start_time = tracker.get_slot('start_time')
        End_time = tracker.get_slot('end_time')
        Location = tracker.get_slot('location')
        msg = add_event(Date, Start_time, End_time, Summary, Location, Service)
        dispatcher.utter_message(text=f"{msg}")
        return [AllSlotsReset()]


class ActionNoConfirm(Action):
    def name(self) -> Text:
        return "action_say_no"

    async def run(
            self,
            dispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[EventType]:
        dispatcher.utter_message(text='Cảm ơn bạn!')

        return [AllSlotsReset()]



class ValidateAddEventForm(FormValidationAction):
    def name(self):
        return "validate_add_event_form"

    async def required_slots(
            self,
            slots_mapped_in_domain: List[Text],
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict",
    ) -> Optional[List[Text]]:
        return slots_mapped_in_domain

    async def validate_date(self,
                            slot_value: Text,
                            dispatcher: CollectingDispatcher,
                            tracker: Tracker,
                            domain: DomainDict,
                            ) -> Dict[Text, Any]:
        date = tracker.get_slot('date')
        if date == '':
            dispatcher.utter_message(text='Ngày không để trống. Xin mời nhập lại:')
            return {'date': None}
        elif date is None:
            return {'date': None}
        else:
            dates = summary_date(date)
            if not dates:
                dispatcher.utter_message(text='Ngày không hợp lệ. Xin mời nhập lại')
                return {'date': None}
            else:
                for day in dates:
                    return {'date': day}

    async def validate_summary(self,
                               slot_value: Text,
                               dispatcher: CollectingDispatcher,
                               tracker: Tracker,
                               domain: DomainDict,
                               ) -> Dict[Text, Any]:
        if slot_value is not None:
            return {"summary": slot_value}
        else:
            dispatcher.utter_message(text='Hoạt động không thể để trống. Xin mời nhập hoạt động')
            return {"summary": None}

    async def validate_start_time(self,
                                  slot_value: Text,
                                  dispatcher: CollectingDispatcher,
                                  tracker: Tracker,
                                  domain: DomainDict,
                                  ) -> Dict[Text, Any]:
        time = tracker.get_slot('start_time')
        date = tracker.get_slot('date')
        if time is not None:
            if check_time(time) == False:
                try:
                    times = get_time(time)
                    if times == '':
                        dispatcher.utter_message(text='Thời gian không hợp lệ xin mời bạn nhập lại')
                        return {"start_time": None}
                    else:
                        if check_time(times) is False:
                            dispatcher.utter_message(text='Thời gian không hợp lệ xin mời bạn nhập lại')
                            return {"start_time": None}
                        else:
                            end = (datetime.datetime.strptime(times, "%H:%M %p") + datetime.timedelta(hours=1)).strftime("%H:%M %p")
                            starttime = get_datetime(date,times)
                            endtime = get_datetime(date,end)
                            if check_exist(starttime,endtime,Service) is False:
                                dispatcher.utter_message(text='Đã có tồn tại sự kiện trong khoảng thời gian này, bạn hãy chọn lại thời gian khác')
                                return {"start_time": None}
                            else:
                                return {"start_time": times,"end_time":endtime.strftime("%I:%M %p")}
                except ValueError:
                    dispatcher.utter_message(text='Thời gian không hợp lệ xin mời bạn nhập lại')
                    return {"start_time": None}
            else:
                end = (datetime.datetime.strptime(time, "%I:%M %p") + datetime.timedelta(hours=1)).strftime("%I:%M %p")
                starttime = get_datetime(date, time)
                endtime = get_datetime(date, end)
                if check_exist(starttime, endtime, Service) is False:
                    dispatcher.utter_message(text='Đã có tồn tại sự kiện trong khoảng thời gian này, bạn hãy chọn lại thời gian khác')
                    return {"start_time":None}
                else:
                    return {"start_time":time,"end_time":end}
        else:
            dispatcher.utter_message(text='Thời gian bắt đầu không thể để trống. Xin mời bạn nhập lại')
            return {"start_time": None}

    # def validate_end_time(self,
    #                       slot_value: Text,
    #                       dispatcher: CollectingDispatcher,
    #                       tracker: Tracker,
    #                       domain: DomainDict,
    #                       ) -> Dict[Text, Any]:
    #     starttime = tracker.get_slot('start_time')
    #     # date = tracker.get_slot('date')
    #     # endtime = tracker.get_slot('end_time')
    #     end = datetime.datetime.strptime(starttime,"%H:%M %p") + datetime.timedelta(hours=1)
    #     print(end)
    #     return {"end_time": end.strftime("%H:%M %p")}
    #     # if endtime is not None:
    #     #     if check_time(endtime) == False:
    #     #         try:
    #     #             time = get_time(endtime)
    #     #             if time == '':
    #     #                 dispatcher.utter_message(text='Thời gian không hợp lệ xin mời bạn nhập lại')
    #     #                 return {"end_time": None}
    #     #             else:
    #     #                 if check_time(time) == False:
    #     #                     dispatcher.utter_message(text='Thời gian không hợp lệ xin mời bạn nhập lại')
    #     #                     return {"end_time": None}
    #     #                 else:
    #     #                     endtime = time
    #     #         except ValueError:
    #     #             dispatcher.utter_message(text='Thời gian không hợp lệ xin mời bạn nhập lại')
    #     #             return {"end_time": None}
    #     #     if date is None:
    #     #         now = (datetime.datetime.now()).strftime("%d-%m-%Y")
    #     #         end = get_datetime(now, endtime)
    #     #         start = get_datetime(now, starttime)
    #     #     else:
    #     #         end = get_datetime(date, endtime)
    #     #         start = get_datetime(date, starttime)
    #     #     if compare_time(starttime,endtime) is False:
    #     #         dispatcher.utter_message(text='Thời gian kết thúc phải lớn hơn thời gian bắt đầu. Xin mời bạn nhập lại')
    #     #         return {"end_time": None}
    #     #     else:
    #     #         if check_exist(start, end, Service) == False:
    #     #             dispatcher.utter_message(text='Đã trùng lịch. xin mời bạn chọn lại thời gian khác')
    #     #             return {"start_time": None, "end_time": None}
    #     #         else:
    #     #             return {"end_time": endtime}
    #     # else:
    #     #     dispatcher.utter_message(text='Không có thời gian kết thúc. Xin mời bạn nhập lại')
    #     #     return {"end_time": None}

    def validate_location(self,
    slot_value: Text,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: DomainDict,
    ) -> Dict[Text, Any]:
        location = tracker.get_slot('location')
        if location is None:
            dispatcher.utter_message(text='Không có địa điểm hoạt động. Xin mời bạn nhập vào')
            return {'location': None}
        else:
            return {'location': location}


### UPDATE EVENT FORM
class ValidateUpdateEventForm(FormValidationAction):
    def name(self):
        return "validate_update_event_form"

    async def required_slots(
            self,
            slots_mapped_in_domain: List[Text],
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict",
    ) -> Optional[List[Text]]:
        return slots_mapped_in_domain

    async def validate_date(self,
                                   slot_value: Text,
                                   dispatcher: CollectingDispatcher,
                                   tracker: Tracker,
                                   domain: DomainDict,
                                   ) -> Dict[Text, Any]:
        date = tracker.get_slot('date')
        if date == '':
            dispatcher.utter_message(text='Ngày không để trống. Xin mời bạn nhập lại')
            return {'date': None}
        elif date is None:
            return {'date': None}
        else:
            dates = summary_date(date)
            events = []
            for day in dates:
                events += list_event(day, Service)
                if not events:
                    dispatcher.utter_message(
                        text=f'Ngày này không có hoạt động nào cả. Bạn hãy nhập lại ')
                    return {'date': None}
                else:
                    msg = see_event_all_day(day, Service)
                    dispatcher.utter_message(text=msg)
                    if len(events) == 1:
                        eventid = events[0]['id']
                        details = get_all_of_event(eventid, Service)
                        return {'num_of_event': 1, 'eventid': eventid,'date': day,'summary': details[0], 'start_time': details[1],
                        'end_time': details[2], 'location': details[3],'datenew':details[4]}
                    else:
                        return {'date': day,'datenew':day}
    async def validate_datenew(self,
            slot_value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        datenew = tracker.get_slot('datenew')
        if datenew == '':
            dispatcher.utter_message(text='Ngày không để trống. Bạn nhập lại')
            return {'datenew': None}
        elif datenew is None:
            dispatcher.utter_message(text='Ngày không để trống. Bạn nhập lại')
            return {'datenew': None}
        else:
            days = summary_date(datenew)
            if not days:
                dispatcher.utter_message(text='Ngày không hợp lệ. Bạn nhập lại')
                return {'datenew': None}
            else:
                date = tracker.get_slot('date')
                if days != date:
                    start = tracker.get_slot('start_time')
                    end = tracker.get_slot('end_time')
                    start = get_datetime(days[0],start)
                    end = get_datetime(days[0],end)
                    if check_exist(start,end,Service) is True:
                        return {'datenew': days[0]}
                    else:
                        dispatcher.utter_message(text='Đã trùng lịch. Bạn hãy nhập lại ')
                        return {'datenew':None}
                else:
                    dispatcher.utter_message(text='Ngày đã bị trùng. Bạn hãy nhập lại')
                    return {'datenew':None}


    async def validate_num_of_event(self,
                                    slot_value: Text,
                                    dispatcher: CollectingDispatcher,
                                    tracker: Tracker,
                                    domain: DomainDict,
                                    ) -> Dict[Text, Any]:
        num_of_event = tracker.get_slot('num_of_event')
        date = tracker.get_slot('date')
        events = []
        events += list_event(date, Service)
        if num_of_event is None:
            dispatcher.utter_message(text='Do có nhiều hoạt động trong ngày nên bạn phải chọn hoạt động')
            return {'num_of_event': None}
        else:
            if num_of_event.isdigit() is False:
                try:
                    number = w2n(num_of_event)
                    dispatcher.utter_message(text=f'Bạn chọn hoạt động số {number}')
                    eventid = events[int(number) - 1]['id']
                    details= get_all_of_event(eventid, Service)
                    return {'num_of_event': number, 'summary': details[0], 'start_time': details[1],
                            'end_time': details[2], 'location': details[3], 'eventid': eventid,'datenew':details[4]}
                except ValueError:
                    dispatcher.utter_message(text="Không hợp lệ, bạn hãy chọn lại")
                    return {'num_of_event':None}
            else:
                eventid = events[int(num_of_event) - 1]['id']
                details = get_all_of_event(eventid, Service)
                return {'num_of_event': num_of_event, 'summary': details[0], 'start_time': details[1],
                        'end_time': details[2], 'location': details[3], 'eventid': eventid, 'datenew': details[4]}
    async def validate_what_change(self,
                                   slot_value: Text,
                                   dispatcher: CollectingDispatcher,
                                   tracker: Tracker,
                                   domain: DomainDict,
                                   ) -> Dict[Text, Any]:
        what_change = tracker.get_slot('what_change')
        what_change = what_change.lower()
        token = get_change_token(what_change)
        if 'all' in token:
            return {'summary': None, 'start_time': None, 'end_time': None,
                         'location': None,'datenew':None}
        elif 'no' in token:
            return {'what_change': what_change}
        else:
            dict = {'what_change':what_change}
            for x in token:
                dict[x] = None
            return dict

    async def validate_summary(self,
                                   slot_value: Text,
                                   dispatcher: CollectingDispatcher,
                                   tracker: Tracker,
                                   domain: DomainDict,
                                   ) -> Dict[Text, Any]:
        summary = tracker.get_slot('summary')
        details = get_all_of_event(tracker.get_slot('eventid'), Service)
        old_summary = details[0]
        if summary == '':
            dispatcher.utter_message(text='Tên hoạt động không thể để trống. Xin mời nhập lại!')
            return {'summary': None}
        else:
            if summary != old_summary:
                return {'summary': summary}
            else:
                dispatcher.utter_message(text='Thông tin mới phải khác thông tin cũ. Bạn hãy nhập lại!')
                return {'summary': None}

    async def validate_start_time(self,
                                      slot_value: Text,
                                      dispatcher: CollectingDispatcher,
                                      tracker: Tracker,
                                      domain: DomainDict,
                                      ) -> Dict[Text, Any]:
        time = tracker.get_slot('start_time')
        details = get_all_of_event(tracker.get_slot('eventid'), Service)
        start = details[1]
        end = tracker.get_slot('end_time')
        if time is not None :
            if time != '':
                if check_time(time) == False:
                    try:
                        times = get_time(time)
                        if times == '':
                            dispatcher.utter_message(text='Thời gian không hợp lệ xin mời bạn nhập lại')
                            return {"start_time": None}
                        else:
                            if check_time(times) == False:
                                dispatcher.utter_message(text='Thời gian không hợp lệ xin mời bạn nhập lại')
                                return {"start_time": None}
                            else:
                                if times != start:
                                    if end is not None:
                                        if compare_time(time,end) is False:
                                            dispatcher.utter_message(
                                                text='Thời gian bắt đầu mới đã lớn hơn thời gian kết thúc cũ. Bạn hãy nhập thời gian kết thúc mới')
                                            return {'start_time': times, 'end_time': None}
                                        else:
                                            return {'start_time': times}
                                    else:
                                        return {'start_time': times}
                                else:
                                    dispatcher.utter_message(text='Thời gian mới phải khác thời gian cũ. Mời bạn nhập lại')
                                    return {"start_time": None}
                    except ValueError:
                        dispatcher.utter_message(text='Thời gian không hợp lệ xin mời bạn nhập lại')
                        return {"start_time": None}
                else:
                    if time != start:
                        if end is not None:
                            if compare_time(time,end) is False:
                                dispatcher.utter_message(
                                    text='Thời gian bắt đầu mới đã lớn hơn thời gian kết thúc cũ. Bạn hãy nhập lại thời gian kết thúc mới')
                                return {'start_time': time, 'end_time': None}
                            else:
                                return {'start_time': time}
                        else:
                            return {'start_time': time}
                    else:
                        dispatcher.utter_message(text='Thời gian mới phải khác thời gian cũ. Mời bạn nhập lại')
                        return {'start_time': None}
            else:
                dispatcher.utter_message(text='Thời gian bắt đầu không thể để trống. Xin mời bạn nhập lại')
                return {"start_time": None}
        else:
            dispatcher.utter_message(text='Thời gian bắt đầu không thể để trống. Xin mời bạn nhập lại')
            return {"start_time": None}

    async def validate_end_time(self,
                                    slot_value: Text,
                                    dispatcher: CollectingDispatcher,
                                    tracker: Tracker,
                                    domain: DomainDict,
                                    ) -> Dict[Text, Any]:
        new_endtime = tracker.get_slot('end_time')
        start_time = tracker.get_slot('start_time')
        details = get_all_of_event(tracker.get_slot('eventid'), Service)
        end = details[2]
        date = tracker.get_slot('datenew')
        if new_endtime is not None:
            if new_endtime != '':
                if check_time(new_endtime) == False:
                    try:
                        times = get_time(new_endtime)
                        if times == '':
                            dispatcher.utter_message(text='Thời gian không hợp lệ xin mời bạn nhập lại')
                            return {"end_time": None}
                        else:
                            if check_time(new_endtime) == False:
                                dispatcher.utter_message(text='Thời gian không hợp lệ xin mời bạn nhập lại')
                                return {"end_time": None}
                            else:
                                if times != end:
                                    if compare_time(start_time,times) is False:
                                        dispatcher.utter_message(
                                            text='Thời gian kết thúc phải lớn hơn thời gian bắt đầu. Bạn hãy nhập lại')
                                        return {'end_time': None}
                                    else:
                                        # timestart = get_datetime(date,start_time)
                                        # timeend = get_datetime(date,times)
                                        # # if check_exist(timestart,timeend,Service) is False:
                                        # #     dispatcher.utter_message(text='Đã có tồn tại sự kiện trong khoảng thời gian này, bạn hãy chọn lại thời gian khác')
                                        # #     return {'end_time':None}
                                        # # else:
                                            return {'end_time':times}
                                else:
                                    dispatcher.utter_message(text='Thời gian mới phải khác thời gian cũ')
                                    return {'end_time':times}
                    except ValueError:
                        dispatcher.utter_message(text='Thời gian không hợp lệ xin mời bạn nhập lại')
                        return {"end_time": None}
                else:
                    if new_endtime != end:
                        if compare_time(start_time,new_endtime) is False:
                            dispatcher.utter_message(
                                text='Thời gian kết thúc phải lớn hơn thời gian bắt đầu. Bạn hãy nhập lại')
                            return {'end_time': None}
                        else:
                            # timestart = get_datetime(date,start_time)
                            # timeend = get_datetime(date,new_endtime)
                            # if check_exist(timestart,timeend,Service) is False:
                            #    dispatcher.utter_message(text='Đã có tồn tại sự kiện trong khoảng thời gian này, bạn hãy chọn lại thời gian khác')
                            #    return {'end_time':None}
                            # else:
                               return {'end_time':new_endtime}
                    else:
                        dispatcher.utter_message(text='Thời gian mới phải khác thời gian cũ')
                        return {'end_time': None}
            else:
                dispatcher.utter_message(text='Thời gian kết thúc không thể để trống. Xin mời bạn nhập lại')
                return {"end_time": None}
        else:
            dispatcher.utter_message(text='Thời gian kết thúc không thể để trống. Xin mời bạn nhập lại')
            return {"end_time": None}

    async def validate_location(self,
                                    slot_value: Text,
                                    dispatcher: CollectingDispatcher,
                                    tracker: Tracker,
                                    domain: DomainDict,
                                    ) -> Dict[Text, Any]:
        new_location = tracker.get_slot('location')
        details = get_all_of_event(tracker.get_slot('eventid'), Service)
        old_location = details[3]
        if new_location == '':
            dispatcher.utter_message(text='Không có địa điểm hoạt động. Xin mời bạn nhập vào')
            return {'location': None}
        else:
            if new_location != old_location:
                return {'location': new_location}
            else:
                dispatcher.utter_message(text='Thông tin mới phải khác thông tin cũ. Bạn hãy nhập lại')
                return {'location': None}

class ActionUpdateSubmit(Action):
    def name(self) -> Text:
        return "action_submit_update"

    async def run(
            self,
            dispatcher,
            tracker: Tracker,
            domain: "DomainDict", ):
        eventid = tracker.get_slot('eventid')
        newdate = tracker.get_slot('datenew')
        new_summary = tracker.get_slot('summary')
        new_start = tracker.get_slot('start_time')
        new_end = tracker.get_slot('end_time')
        new_location = tracker.get_slot('location')
        details = get_all_of_event(eventid, Service)
        old_details = {'summary': details[0], 'start': details[1], 'end': details[2], 'location':details[3],'datenew':details[4]}
        new_details = {'summary': new_summary, 'start': new_start, 'end': new_end, 'location': new_location,'datenew':newdate}
        text = {'summary': 'Tên hoạt động', 'start': 'Thời gian bắt đầu', 'end': 'Thời gian kết thúc',
                'location': 'Địa điểm','datenew':'Ngày'}
        diff = compare(old_details,new_details)
        if not diff:
            dispatcher.utter_message(text='Bạn không có sự thay đổi nào')
            return AllSlotsReset()
        else:
            msg = f'Bạn cần thay đổi thông tin sự kiện vào ngày {old_details["datenew"]} với các thông tin mới là: \n'
            for i in diff:
                msg += f'- {text[i]} từ {old_details[i]} sang {new_details[i]} \n'
            dispatcher.utter_message(text=msg + 'Đúng không?')

class ActionYesUpdateConfirm(Action):
    def name(self) -> Text:
        return "action_update_yes"

    async def run(
            self,
            dispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[EventType]:
        Date = tracker.get_slot('datenew')
        Summary = tracker.get_slot('summary')
        Start_time = tracker.get_slot('start_time')
        End_time = tracker.get_slot('end_time')
        Location = tracker.get_slot('location')
        eventid = tracker.get_slot('eventid')
        msg = update_event(Date,Start_time,End_time,Summary,Location,eventid,Service)
        dispatcher.utter_message(text=f"{msg}")
        return [AllSlotsReset()]

class ActionNoUpdateConfirm(Action):
    def name(self) -> Text:
        return "action_update_no"

    async def run(
            self,
            dispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[EventType]:
        dispatcher.utter_message(text='Cảm ơn bạn!')
        return [AllSlotsReset()]

###                         DELETE FORM
class ValidateDelEventForm(FormValidationAction):
    def name(self):
        return "validate_delete_form"

    async def required_slots(self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
        ) -> Optional[List[Text]]:
        return slots_mapped_in_domain

    async def validate_date(self,
        slot_value : Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
        ) -> Dict[Text, Any]:
        date = tracker.get_slot('date')
        if slot_value == '':
            dispatcher.utter_message(text='Ngày không thể để trống. Xin mời bạn nhập lại')
            return {'date':None}
        else:
            dates = summary_date(date)
            events = []
            for day in dates:
                events += list_event(day, Service)
                if not events:
                    dispatcher.utter_message(
                        text=f'Không có hoạt động trong thời gian này. Xin mời bạn chọn lại thời gian khác ')
                    return {'date': None}
                else:
                    msg = see_event_all_day(day, Service)
                    dispatcher.utter_message(text=msg)
                    if len(events) == 1:
                        eventid = events[0]['id']
                        return {'date':day,'num_of_event': 1, 'eventid': eventid}
                    else:
                        return {'date': day,'num_of_event': None }

    async def validate_num_of_event(self,
        slot_value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Dict[Text, Any]:
        choose = tracker.get_slot('num_of_event')
        token = get_change_token(choose)
        date = tracker.get_slot('date')
        events = []
        events += list_event(date, Service)
        if choose == '':
            dispatcher.utter_message(text='Do có nhiều hoạt động trong ngày nên bạn phải chọn hoạt động')
            return {'num_of_event': None}
        elif 'all' in token:
            return {'num_of_event':token[0] ,'eventid':'all'}
        else:
            if choose.isdigit() is False:
                try:
                    number = w2n(choose)
                    dispatcher.utter_message(text=f'Bạn chọn hoạt động số {number}')
                    eventid = events[int(number) - 1]['id']
                    return {'num_of_event': number,'eventid':eventid}
                except ValueError:
                    dispatcher.utter_message(text="Không hợp lệ, bạn hãy chọn lại")
            else:
                dispatcher.utter_message(text='Không hợp lệ. Xin mời bạn chọn lại')
                return {'num_of_event': None}

class ActionDelSubmit(Action):
    def name(self) -> Text:
        return "action_submit_del"
    async def run(self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict", ):
        slot = tracker.get_slot('num_of_event')
        if isinstance(slot,int):
            dispatcher.utter_message(text=f'Bạn có chắc muốn xóa hoạt động này không?')
        else:
            dispatcher.utter_message(text='Bạn có chắc muốn xóa tất cả hoạt động này không?')

class ActionYesDelConfirm(Action):
    def name(self) -> Text:
        return "action_del_yes"
    async def run(
            self,
            dispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[EventType]:
        Date = tracker.get_slot('date')
        choose = tracker.get_slot('num_of_event')
        eventid = tracker.get_slot('eventid')
        events = list_event(Date,Service)
        if isinstance(choose,int):
            del_event(eventid, Service)
            dispatcher.utter_message(text='Hoạt động của bạn đã bị xóa')
            return [AllSlotsReset()]
        else:
            for event in events:
                del_event(event['id'],Service)
            dispatcher.utter_message(text='Tất cả các hoạt động của bạn đã bị xóa')
            return [AllSlotsReset()]

class ActionNoDeleteConfirm(Action):
    def name(self) -> Text:
        return "action_del_no"

    async def run(
            self,
            dispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[EventType]:
        dispatcher.utter_message(text='Cảm ơn bạn!')
        return [AllSlotsReset()]


### Total Covid VN

class ActionTotalCovid(Action):
    def name(self) -> Text:
        return "action_total_covid"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        case = tracker.get_slot('case')
        with open("data/Covid.json", encoding='utf-8') as jsonFile:
            data = json.load(jsonFile)
        date  = (datetime.datetime.now() + datetime.timedelta(days=(-1))).strftime("%d-%m-%Y")
        reponse = requests.get(
            'https://api.apify.com/v2/key-value-stores/EaCBL1JNntjR3EakU/records/LATEST?disableRedirect=true.').json()
        if tracker.get_slot('case') is None:
            dispatcher.utter_message(text=f'Tình hình dịch bệnh Covid-19 ở Việt Nam tính đến ngày {date}: \n'
                                          f'Số ca mắc mới: +{(reponse["infectedToday"]):,} ca \n'
                                          f'- Tổng số số ca nhiễm: {(reponse["infected"]):,} ca \n'
                                          f'- Tổng số ca đang điều trị: {(reponse["treated"]):,} ca \n'
                                          f'- Tổng số ca được điều trị khỏi: {(reponse["recovered"]):,} ca \n'
                                          f'- Tổng số ca tử vong: {(reponse["died"]):,} ca')
            return [SlotSet('case',None)]
        elif data[case.lower()] == 'infected': # So nguoi mac
            dispatcher.utter_message(text=f"Tổng số ca nhiễm tính đến hôm nay là {(reponse['infected']):,} ca")
            return [SlotSet('case',None)]
        elif data[case.lower()] == 'cured':
            dispatcher.utter_message(text=f'Tổng số ca chữa khỏi là {(reponse["recovered"]):,} ca')
            return [SlotSet('case', None)]
        elif data[case.lower()] == 'treatment':
            dispatcher.utter_message(text=f'Tổng số ca đang điều trị là {(reponse["treated"]):,} ca')
            return [SlotSet('case', None)]
        elif data[case.lower()] == 'die':
            dispatcher.utter_message(text=f'Số người chết vì Covid ở Việt Nam là {(reponse["died"]):,} ca')
            return [SlotSet('case', None)]


### Covid City
class ActionCovidCity(Action):
    def name(self) -> Text:
        return "action_covid_city"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        city = tracker.get_slot('location')
        date = (datetime.datetime.now() + datetime.timedelta(days=(-1))).strftime("%d-%m-%Y")
        reponse = requests.get(
            'https://api.apify.com/v2/key-value-stores/EaCBL1JNntjR3EakU/records/LATEST?disableRedirect=true.').json()
        locations = reponse['locations']
        if city is not None:
            for location in locations:
                if city == location['name']:
                    dispatcher.utter_message(text=f'Tình hình dịch bệnh ở {city} tính đến ngày {date}: \n'
                                                  f'Số ca mắc mới trong ngày: +{(location["casesToday"]):,} ca \n'
                                                  f'- Tổng số ca nhiễm: {(location["cases"]):,} ca\n'
                                                  f'- Tổng số ca tử vong: {(location["death"]):,} ca')
                    return [SlotSet('city',None)]


### Weather
class ActionWeatherCity(Action):
    def name(self) -> Text:
        return "action_weather_city"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        city  = tracker.get_slot('location')
        msg  = weather(city)
        dispatcher.utter_message(text=msg)
        return [SlotSet('city',None)]


### Time
class ActionWhattime(Action):
    def name(self) -> Text:
        return "action_whattime"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        now  = datetime.datetime.now()
        dispatcher.utter_message(text=f"Bây giờ là {now.strftime('%H:%M')} ")

### Open App
class ActionOpenApp(Action):
    def name(self) -> Text:
        return "action_openapp"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        app = tracker.latest_message['entities'][0]['value']
        app_dict = {"word":"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Word 2016",
                    "excel":"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Excel 2016",
                    "trình duyệt":"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Microsoft Edge",
                    "powerpoint":"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\PowerPoint 2016",
                    "pycharm":"C:\Program Files\JetBrains\PyCharm Community Edition 2020.3.3\bin\pycharm64"}
        dispatcher.utter_message(text=f'Đang mở {app} ')
        os.startfile(app_dict[app.lower()])
        return []


## Open Web
class ActionOpenWeb(Action):
    def name(self) -> Text:
        return "action_openweb"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        web = tracker.latest_message['entities'][0]['value']
        edge_path = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
        webbrowser.register('edge',None,webbrowser.BackgroundBrowser(edge_path))
        web_dict = {"youtube":"Youtube.com",
                    "drive":"drive.google.com",
                    "google":"google.com",
                    "calendar":"calendar.google.com",
                    "đại học Cần Thơ":"ctu.edu.vn",
                    "báo":"vnexpress.net",
                    "zing":"zing.vn","nhạc":"mp3.zing.vn","album":"https://www.youtube.com/watch?v=WtCIuvFD0nM"}
        dispatcher.utter_message(text=f'Đang mở {web}')
        webbrowser.get('edge').open(web_dict[web.lower()])
        return []

### Covid Info
class ActionCovidInfo(Action):
    def name(self) -> Text:
        return "action_covid_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text='Vi rút Corona là một họ vi rút lớn được tìm thấy ở cả động vật và người. Một số vi rút có thể gây bệnh cho người từ cảm lạnh thông thường đến các bệnh nghiêm trọng hơn như Hội chứng hô hấp Trung Đông (MERS) và Hội chứng hô hấp cấp tính nặng (SARS).'
                                      'Vi rút Corona mới là một chủng mới của vi rút Corona chưa từng xác định được ở người trước đây. Vi rút mới này hiện gọi là 2019-nCoV, chưa từng được phát hiện trước khi dịch bệnh được báo cáo tại Vũ Hán, Trung Quốc vào tháng 12 năm 2019. Đây là một loại vi rút đường hô hấp mới gây bệnh viêm đường hô hấp cấp ở người và cho thấy có sự lây lan từ người sang người.'
                                      'Vi rút mới này cùng họ với vi rút gây Hội chứng hô hấp cấp tính nặng (SARS-CoV) nhưng không phải là cùng một vi rút.')
