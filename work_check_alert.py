import os
from tabnanny import verbose
import schedule
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

def job():
    today = datetime.now().date()

    response = requests.get(
        f'http://xdn.hanbiro.net/ngw/timecard/org/status/?status=&start_date={today}&group_no=&user_no=&page=1',
        headers={
         'Cookie': os.getenv('MY_HEADER'),
         'Accept': 'application/json, text/plain, */*'
        }
    )
    print(response.status_code)
    print(response.json()['rows'][0]['uname'])
    print(response.json()['rows'][0]['data'][0]['status_name'])
    timestamp = int(response.json()['rows'][0]['data'][0]['regdate'])
    print(datetime.fromtimestamp(timestamp))


at_time = "23:06"
schedule.every().monday.at(at_time).do(job)
schedule.every().tuesday.at(at_time).do(job)
schedule.every().wednesday.at(at_time).do(job)
schedule.every().thursday.at(at_time).do(job)
schedule.every().friday.at(at_time).do(job)

schedule.every().sunday.at(at_time).do(job)

load_dotenv(verbose = True)

job()
while True:
    schedule.run_pending()
    time.sleep(1)