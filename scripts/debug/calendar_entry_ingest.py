# Grants Round 7 BrightID verification parities input
# https://docs.google.com/document/d/1wzPrlYu6K4R_lOcpYetU_52u4yrcozzBFVrEWjschnw/edit#heading=h.1el8e2wn7u87

from django.utils import timezone

import pytz
from marketing.models import UpcomingDate

# AirMeets
# Every day at 07:00-07:30 UTC 
# https://www.airmeet.com/e/7881f390-eb68-11ea-8616-b3016fb86143
# Every day at 21:00-21:30 UTC 
# https://www.airmeet.com/e/7881f390-eb68-11ea-8616-b3016fb86143


title = 'BrightID Verification Party'
img_url = 'https://p200.p0.n0.cdn.getcloudapp.com/items/Kour2p4k/Screen%20Shot%202020-09-14%20at%2010.57.37%20AM.png'
url = 'https://www.airmeet.com/e/7881f390-eb68-11ea-8616-b3016fb86143'
comment = 'https://docs.google.com/document/d/1wzPrlYu6K4R_lOcpYetU_52u4yrcozzBFVrEWjschnw/edit#heading=h.t8kppbpiu62'
context_tag = 'brightid'

iter_amount = 60 * 60 * 4 # 4 hours apart
og_timestamps = [1600066800, 1600066800 + iter_amount]
for og_timestamp in og_timestamps:
    for i in range(0, 15):
        timestamp = og_timestamp + (i * 24 * 60 * 60)
        date = timezone.datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)

        UpcomingDate.objects.create(
            title=title,
            date=date,
            img_url=img_url,
            url=url,
            comment=comment,
            context_tag=context_tag,
            )

# Zooms
# Thursdays at 15:30-16:30 UTC 
# https://us02web.zoom.us/meeting/register/tZIvcuChrTksHda3OvEt1USQXh9YRNiliAgr
# Fridays at 10:00-11:00 UTC https://zoom.us/meeting/register/tJcuduuhrjIuE9VKLh80vtiWAjofWRJIiBp4
# Fridays at 20:00-21:00 UTC https://zoom.us/meeting/register/tJYtcOGtqDItG9zry8riTg8G6rtfuKqgUXvw
title = 'BrightID Zoom Drop-in Calls'
iter_amount = 24 * 7 * 60 * 60
packages = [
    #start_ts, url
    (1600356600, "https://us02web.zoom.us/meeting/register/tZIvcuChrTksHda3OvEt1USQXh9YRNiliAgr"),
    (1600423200, "https://zoom.us/meeting/register/tJcuduuhrjIuE9VKLh80vtiWAjofWRJIiBp4"),
    (1600103570, "https://zoom.us/meeting/register/tJYtcOGtqDItG9zry8riTg8G6rtfuKqgUXvw"),
]
for package in packages:
    for i in range(0, 2):
        timestamp = package[0] + (iter_amount * i)
        date = timezone.datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
        print(date)
        UpcomingDate.objects.create(
            title=title,
            date=date,
            img_url=img_url,
            url=url,
            comment=comment,
            context_tag=context_tag,
            )
