import schedule
import time
import os


def job():
    os.system('python main.py')

# Schedule the job every day at 11:50 PM
schedule.every().day.at("23:50").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
