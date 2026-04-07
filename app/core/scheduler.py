from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime
import streamlit as st

# Use Streamlit's cache or singleton approach to ensure only one scheduler runs
@st.cache_resource
def get_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.start()
    return scheduler

def schedule_email_task(run_date, func, *args, **kwargs):
    """
    Schedules a function to run at a specific date and time.
    """
    scheduler = get_scheduler()
    job = scheduler.add_job(
        func,
        trigger=DateTrigger(run_date=run_date),
        args=args,
        kwargs=kwargs
    )
    return job.id

def cancel_scheduled_job(aps_job_id):
    """
    Cancels a job in APScheduler.
    """
    try:
        scheduler = get_scheduler()
        scheduler.remove_job(aps_job_id)
        return True
    except Exception as e:
        print(f"Error canceling job: {e}")
        return False
