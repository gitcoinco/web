'''
    Copyright (C) 2017 Gitcoin Core 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.conf import settings

import twitter
import random
import sys
import time
import csv
from marketing.quotify.run import write_image, recommend_font_size, select_font, select_background_image
import random


class Command(BaseCommand):

    help = 'sends marketing quotes to twitter'

    def handle(self, *args, **options):
        

        intros = [ "Quote of the Day",
        "QOTD",
        "Software Dev QOTD",
        "Software Development Quote",
        ]
        intro = random.choice(intros)


        #setup
        api = twitter.Api(
            consumer_key=settings.TWITTER_CONSUMER_KEY, 
            consumer_secret=settings.TWITTER_CONSUMER_SECRET, 
            access_token_key=settings.TWITTER_ACCESS_TOKEN, 
            access_token_secret=settings.TWITTER_ACCESS_SECRET, 
        )

        quotes = []
        with open('marketing/assets/software_quotes.csv', 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter='"')
            for row in reader:
                quote = row[1]
                author = row[0]
                quotes.append((quote, author))


        random.shuffle(quotes)

        quote = quotes[0][0]
        author = quotes[0][1]

        tweet = "{} by {}: \"{}\"".format(intro, author, quote).replace("&amp;",'and')

        if len(tweet) >= 140:
            tweet = tweet[:136] + "..."

        print(tweet)

        # text
        text = quote
        output_filename = "marketing/quotify/output/{}.png".format(int(time.time()))
        text = text.strip().replace("'","").replace("\x92","'").replace("\x93","'").replace("\x94","'").encode("utf8").replace("\n","").replace('�','')
        print(text)
        if text.strip() == "" or len(text) < 5:
            return
        img = write_image(text, output_filename, background_img=select_background_image())

        #post!
        counter = 0
        #for tweet in tweets:
        if True:
            counter+= 1
            print(tweet)
            new_tweet = tweet.replace("\x92","'").replace("\x93","'").replace("\x94","'").encode("utf8").replace("\n","")
            print(new_tweet)
        #    if counter == len(tweets):
        #        status = api.PostUpdate(new_tweet, media=img)
        #    else:
        #        status = api.PostUpdate(new_tweet)
            status = api.PostUpdate(new_tweet, media=img)

