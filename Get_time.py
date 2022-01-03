from vietnam_number import w2n
import datetime
from Get_date import tokenize_2
def get_time_from_string(msg):
    word1 = 'kém'
    if word1 in msg:
        h_m = msg.split(word1)
        hour = str(h_m[0]).strip()
        min = str(h_m[1]).strip()
        if extract_number(hour) is True:
            hour = int(hour.split('giờ')[0]) - 1
        else:
            hour = int(w2n(hour)) - 1
        if extract_number(min) is True:
            min = min.split('phút')[0]
            min = 60 - int(min)
        else:
            min = w2n(min.split('phút')[0])
            min = 60 - int(min)
        time = str(datetime.timedelta(hours=int(hour), minutes=int(min)))
        time = datetime.datetime.strptime(time,'%I:%M:%S')
        return time
    else:
        h_m = msg.split('giờ')
        hour = str(h_m[0]).strip()
        min = str(h_m[1]).strip()
        if extract_number(hour) is True:
            hour = int(hour.split('giờ')[0])
        else:
            hour = int(w2n(hour))
        if extract_number(min) is True:
            min = min.split('phút')[0]
            if min == 'rưỡi':
                min = 30
            elif min == '':
                min = 00
            else:
                min = min
        else:
            min = min.split('phút')[0]
            if min == 'rưỡi':
                min = 30
            elif min == '':
                min = 00
            else:
                min = w2n(min)
        time = str(datetime.timedelta(hours=int(hour), minutes=int(min)))
        time = datetime.datetime.strptime(time,"%H:%M:%S")
        return time

def extract_number(msg):
    return any(char.isdigit() for char in msg)

def get_time(msg):
    if msg.count('sáng') > 0:
        msg = msg.replace('sáng','')
        time = get_time_from_string(msg)
        return time.strftime('%H:%M %p')
    elif msg.count('trưa') >0:
        msg = msg.replace('trưa','')
        time = get_time_from_string(msg)
        return time.strftime('%H:%M %p')
    elif msg.count('chiều') > 0 :
        msg = msg.replace('chiều','')
        time = (get_time_from_string(msg)).strftime("%H:%M")
        time = time + ' PM'
        time = datetime.datetime.strptime(time,'%I:%M %p')
        return  time.strftime('%I:%M %p')
    elif msg.count('tối') > 0:
        msg = msg.replace('tối','')
        time = (get_time_from_string(msg)).strftime("%H:%M")
        time = time + ' PM'
        time = datetime.datetime.strptime(time, '%I:%M %p')
        return  time.strftime('%I:%M %p')
    else:
        time = get_time_from_string(msg)
        return time.strftime('%H:%M %p')

def compare_time(start,end):
    end = datetime.datetime.strptime(end, "%I:%M %p").time()
    start = datetime.datetime.strptime(start, "%I:%M %p").time()
    if start >= end:
        return False
    else:
        return True

