import requests
import datetime
def weather(city):
    url = "http://api.openweathermap.org/data/2.5/weather?"
    api_key = 'f3960ee54312ed5835ab2978957c1c44'
    call_url = url + "appid=" + api_key + "&q=" + city + "&units=metric" + "&lang=vi"
    response = requests.get(call_url)
    data = response.json()
    date = datetime.datetime.now()

    msg = f'Thời tiết ở {city} ngày {date.strftime("%d-%m-%Y")}: \n' \
          f'- Dự báo có {data["weather"][0]["description"]} \n' \
          f'- Nhiệt độ trung bình: {int(data["main"]["temp"])}℃ \n' \
          f'- Độ ẩm trung bình: {data["main"]["humidity"]}% \n'
    return msg

# city = city.replace(" ", "+")
    # res = requests.get(
    #     f'https://www.google.com/search?q={city}&oq={city}&aqs=chrome.0.35i39l2j0l4j46j69i60.6128j1j7&sourceid=chrome&ie=UTF-8',
    #     headers=headers)
    # print("Searching...\n")
    # soup = BeautifulSoup(res.text, 'html.parser')
    # #print(soup)
    # city = city.replace("+"," ")
    # time = soup.select('#wob_dts')[0].getText().strip()
    # info = soup.select('#wob_dc')[0].getText().strip()
    # temp = soup.select('#wob_tm')[0].getText().strip()
    # hm = soup.select('#wob_hm')[0].getText().strip()
    # rain = soup.select('#wob_pp')[0].getText().strip()
    # mydivs = soup.select('.wtsRwe')
    # msg = f'Thời tiết vào hôm nay ở {city.replace("weather","")}: \n' \
    #       f'Vào lúc {time} \n' \
    #       f'Dự báo {info} \n' \
    #       f'Nhiệt độ trung bình {temp} \n' \
    #       f'Độ ẩm trung bình: {hm} \n' \
    #       f'Khả năng có mưa: {rain}'
    # print(msg)
