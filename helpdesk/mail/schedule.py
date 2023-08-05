from apscheduler.schedulers.background import BackgroundScheduler
from .listener import process_received_mail

def start_schedule():
    schedule = BackgroundScheduler()
    schedule.add_job(process_received_mail, 'interval', seconds=5)
    schedule.start()