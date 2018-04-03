import logging

from django.conf import settings
from django.core.management.base import BaseCommand

import requests
from retail.models import Idea

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
class Command(BaseCommand):

    help = 'syncs ideas with disqus'

    @staticmethod
    def process_threads(threads):
        for thread in threads:
                if thread.get('identifiers'):
                    if len(thread.get('identifiers')[0].split('-')) == 2:
                        idea_id = thread.get('identifiers')[0].split('-')[1]
                        print(thread)
                        Idea.objects.filter(id=idea_id).update(posts = thread.get("posts"), likes = thread.get("likes"))

    @staticmethod
    def query_threads(payload):
        return requests.get('https://disqus.com/api/3.0/forums/listThreads.json', params = payload)

    @staticmethod
    def has_next(response):
        return response.json().get('cursor').get('hasNext')

    @staticmethod
    def get_threads(response):
        return response.json().get('response')

    def handle(self, *args, **options):
        #config
        public_key = settings.DISQUS_PUBLIC_KEY
        forum = settings.DISQUS_FORUM_NAME
        limit = 100
        payload = {'api_key': public_key, 'forum': forum, 'limit': limit}

        r = Command.query_threads(payload)
        threads = Command.get_threads(r)
        has_next = Command.has_next(r)
        Command.process_threads(threads)
        while True:
            if not has_next:
                break            
            payload = {'api_key': public_key, 'cursor': r.json().get('cursor').get('next'), 'forum': forum, 'limit': limit}
            r = Command.query_threads(payload)
            threads = Command.get_threads(r)
            Command.process_threads(threads)
            has_next = Command.has_next(r)
