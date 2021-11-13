# refactoring to add in logging and apscheduling

# Standard Lib - don't need to add to req's.txt
import logging

# Django
from django.conf import settings
from django.core.management.base import BaseCommand

# Third party
import feedparser as fp
from dateutil.parser import parse
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

# Custom models
from podcasts.models import Episode

# instantiate the logger
logger = logging.getLogger(__name__)

# refactor to check current pc's to saved pc's
def save_new_episodes(feed):
    podcast_title = feed.channel.title
    podcast_image = feed.channel.image['href']

    for item in feed.entries:
        if not Episode.objects.filter(guid=item.guid).exists():
            episode = Episode(
                title = item.title,
                description = item.description,
                pub_date = parse(item.published),
                link = item.link,
                image = podcast_image,
                podcast_name = podcast_title,
                guid = item.guid,
            )
            episode.save()

def fetch_realpython_episodes():
    _feed = fp.parse('https://realpython.com/podcasts/rpp/feed')
    save_new_episodes(_feed)

def fetch_talkpython_episodes():
    _feed = fp.parse("https://talkpython.fm/episodes/rss")
    save_new_episodes(_feed)

# delete old records from the DB via the schedule job
# set to run every 24 hours or 86,400 seconds
def delete_old_job_executions(max_age=86_400):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

class Command(BaseCommand):
    help = 'Runs ap-scheduler'

    def handle(self, *args, **options):
        # create your job store and scheduler instance in the custom command’s .handle() function
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), 'default')

        # Job 1: fetch the Real Python Podcast
        scheduler.add_job(
            fetch_realpython_episodes,
            trigger='interval',
            minutes=2,
            id='The Real Python Podcast',
            max_instances=1,
            replace_existing=True,
        )
        logger.info('Added job: The Real Python Podcast')

        # Job 2: fetch the Talk Python Podcast
        scheduler.add_job(
            fetch_talkpython_episodes,
            trigger='interval',
            minutes=2,
            id='Talk Python Feed',
            max_instances=1,
            replace_existing=True,
        )
        logger.info('Added job: Talk Python Feed')

        # Job 3: Clean up old records
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week='sun', hour='00', minute='00'
            ),  # Midnight on Sunday
            id="Delete Old Job Executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: Delete Old Job Executions.")

        # Logging section; error handle if interrupted
        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")