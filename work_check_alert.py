import os
from tabnanny import verbose
import schedule, time
import requests, json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Final

def is_take_off(status):
    for case in take_off_status:
        if status == case:
            return True
    
    return False

def get_today():
    return datetime.now().date()

def get_response(today):
    response = requests.get(
        f'http://xdn.hanbiro.net/ngw/timecard/org/status/?status=&start_date={today}&group_no=&user_no=&page=1',
        headers={
         'Cookie': os.getenv('GROUPWARE_COOKIE'),
         'Accept': 'application/json, text/plain, */*'
        }
    )
    return response.json()['rows']

def send_message(message):
    request = requests.post(
        'https://hooks.slack.com/services/' + os.getenv('SLACK_URI'),
        headers = {
            'Content-type': 'application/json'
        },
        data = json.dumps(message)
    )
    return request

def get_yesterday_message(response):
    yesterday = get_today() + timedelta(days = -1)
    if yesterday.weekday() >= 5:
        return response[0]['data'][0]['title']

    result = ''
    for i in range(len(response)):
        if is_take_off(response[i]["data"][0]["status_name"]):
            result += next_line
            continue

        result += f'{response[i]["uname"]}: {response[i]["data"][1]["time"]}{next_line} '

    return result

def get_today_message(response):
    result = ''
    print(response[0])
    for i in range(len(response)):
        result += f'{response[i]["uname"]}: {response[i]["data"][0]["status_name"]} '

        if is_take_off(response[i]["data"][0]["status_name"]):
            result += next_line
            continue
        print()
        result += f'{response[i]["data"][0]["time"]}{next_line}' 

    return result

def job():
    today = get_today()
    yesterday = today + timedelta(days = -1)

    yesterday_data = get_response(yesterday)
    today_data = get_response(today)

    message = {'text': f'{today}{next_line}{yesterday_message}{next_line} {get_yesterday_message(yesterday_data)}'}
    message['text'] += f'{next_line}{today_message}{next_line} {get_today_message(today_data)}'
    
    request = send_message(message)
    print('request status:', request.status_code)

if __name__ == '__main__':
    at_time: Final = '09:00'
    take_off_status: Final = ['연차 - 종일', '휴무']

    next_line: Final = '\n'
    today_message: Final = '========== 오늘 출근시간 =========='
    yesterday_message: Final = '========== 어제 퇴근시간 =========='

    schedule.every().monday.at(at_time).do(job)
    schedule.every().tuesday.at(at_time).do(job)
    schedule.every().wednesday.at(at_time).do(job)
    schedule.every().thursday.at(at_time).do(job)
    schedule.every().friday.at(at_time).do(job)

    load_dotenv(verbose = True)

    job()
    while True:
        schedule.run_pending()
        time.sleep(1)