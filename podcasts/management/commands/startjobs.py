from django.core.management.base import BaseCommand

import feedparser as fp
from dateutil.parser import parse

from podcasts.models import Episode

# refactor to check current pc's to saved pc's
def save_new_episodes(feed):
    podcast_title = feed.channel.title
    podcast_image = feed.channel.image['href']

    for item in feed.entries():
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

class Command(BaseCommand):
    def handle(self, *args, **options):
        fetch_realpython_episodes()
        fetch_talkpython_episodes()