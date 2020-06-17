# -*- coding: utf-8 -*-
"""Define the GDPR reconsent command for EU users.

Copyright (C) 2020 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
import operator
import random
import time
import warnings
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Activity, Earning, Profile
from grants.models import *
from grants.models import CartActivity, Contribution, PhantomFunding
from grants.views import clr_round, next_round_start, round_end
from townsquare.models import Comment

text = ''

def pprint(_text, _text2=None):
    global text

    _text = str(_text)
    if _text2:
        _text += ", " + str(_text2)

    text += _text + "\n"
    print(_text)

warnings.filterwarnings("ignore", category=DeprecationWarning)

def do_post(text, comment=None):
    profile = Profile.objects.filter(handle='gitcoinbot').first()
    metadata = {
        'title': text,
    }
    activity = Activity.objects.create(profile=profile, activity_type='status_update', metadata=metadata)
    if comment:
        Comment.objects.create(
            profile=profile,
            activity=activity,
            comment=comment)

def quote():
    quotes = [
    [ ('Open source software has become a relevant part of the software industry and a number of software ecosystems. It has become an alternative to commercial software in various areas and is already included in many commercial software products.'), 'March 2017 Report by the EU' ],
    [ ('OSS can support the development of new software because companies can use existing software to create their software products. Therefore, it can be a catalyst for new software developments and the creation of new software companies.'), 'March 2017 Report by the EU' ],
    [ ('OSS can ... be considered as an important factor in the value creation of other software, even if it is difficult to quantify. Today, OSS often replaces the standard middleware platform provided by a third party. It limits costs and, more importantly, dependency to some extent.'), 'March 2017 Report by the EU' ],
    [ ('Software vendors that build new products can save costs if they reuse existing open source software components instead of developing software on their own or buying software components. As a result, open source software can foster the development of new software products as well as the creation of new software vendors.'), 'March 2017 Report by the EU' ],
    [ ('OSS allows companies to incorporate IT in their value chain in an easy way. Instead of buying commercial software that may involve the risk of a vendor lock-in, they just have to share value with the OSS community.'), 'March 2017 Report by the EU' ],
    [ ('The basic principle of open source software development is that a community of software experts contributes time and effort for coding, reviewing and testing to publicly available source code.'), 'March 2017 Report by the EU' ],
    [ ('Open source can ... be a key success factor for co-innovation as none of the participants will have the upper hand. OSS can create standards that are very important for the development of emerging technologies and that help lower the total cost of ownership.'), 'March 2017 Report by the EU' ],
    [ ('Future software must be easily developed from components and freely available software and its maintenance must be supported by a wide community. This includes a reuse and evolution of existing software and modules: rather than developing from scratch, existing software must become more easily retrievable, interoperable and usable.'), 'March 2017 Report by the EU' ],
    [ ('OSS is also a firm promoter of standards and interoperability. This openness lowers the risk of a vendor lock-in. OSS is based on communities that develop software in a collaborative way. Many enabling technologies for SMAC have strong OSS roots.'), 'March 2017 Report by the EU' ],
    [ ('Some commercial vendors offer open source software in order to create a large user community. They generate revenues from subscriptions to support and updates and/or professional services as well as from selling extensions or professional editions that are based on the open source software. Examples are the providers of the Linux distributions RedHat and Suse.'), 'March 2017 Report by the EU' ],
    [ ('Major commercial software vendors such as IBM and HP have made open source technology a part of their business by integrating it into their own products and by providing professional services for open source software.'), 'March 2017 Report by the EU' ],
    [ ('Many business applications already include open source software and this is going to increase. Some vendors may donate part of their products to an open source foundation in order to create a larger user community that will potentially become buyers of commercial add-ons or services. On the other hand, open source software that is free of charge can be an alternative to commercial application software.'), 'March 2017 Report by the EU' ],
    [ ('According to Carlo Daffara, a researcher in the field of IT economics who contributed to several European Commission research projects involving open source, the European economy saves around EUR114 billion per year by using open source software solutions. Apart from direct cost savings, other benefits of open source are reduced project failure and lower cost of code maintenance.'), 'March 2017 Report by the EU' ],
    [ ('Quoting several sources, [Carlo Daffara, researcher in IT economics] estimates that about 35 per cent of the software  used in the past five years was directly or indirectly derived from open source.'), 'March 2017 Report by the EU' ],
    [ ('Companies outsource activities that are less critical. For example, a car manufacturer will hardly outsource the in-house software development for its autonomous driving technology, as this is highly confidential and highly relevant for its competitiveness.'), 'March 2017 Report by the EU' ],
    [ ('Outsourcing can be an alternative to in-house software development and more and more companies take advantage of this. ... Two areas of potential outsourcing in the area of in-house software development are testing and maintenance.'), 'March 2017 Report by the EU' ],
    [ ('As demand for individual software development increases, companies evaluate ways to outsource such activities due to internal skill shortages and cost considerations.'), 'March 2017 Report by the EU' ],
    [ ("Victor Hugo once remarked: 'You can resist an invading army; you cannot resist an idea whose time has come'. The Drucker Forum will ask the question and deliver elements of response as to whether the time for a new entrepreneurial age has come."), 'Promotional site for the 2016 Drucker Forum' ],
    [ ('Digital technology has played an accelerating role in this transformation [to an entrepreneurial society] by dramatically lowering barriers to entry in many industries and by providing new tools for managing knowledge creation and sharing and by enabling new forms of continuous learning, all on a global canvas.'), 'Promotional site for the 2016 Drucker Forum' ],
    [ ('While the journey towards an entrepreneurial society is by no means a straight-line progression towards a well-defined destination, broad cultural changes have brought entrepreneurialism into the mainstream. An activity that was once regarded as peripheral, perhaps even a bit suspect, has become cool, celebrated by politicians and embraced by the new generations.'), 'Promotional site for the 2016 Drucker Forum' ],
    [ ('[T]he emergence of an entrepreneurial culture entails a broader transformation of the economic fabric of our society, as we see in the rapid proliferation of free agents in the form of contractors, freelancers and self-employed workers on on-demand platforms, for example.'), 'Promotional site for the 2016 Drucker Forum' ],
    [ ('[I]n a world of rapid change frequent job and career moves, switches between employed and independent roles become the rule rather than the exception.'), 'Promotional site for the 2016 Drucker Forum' ],
    [ ('Within large organizations a renewed focus on freeing up the creative and innovative potential of workers points in the same direction [as that of the entrepreneurial society] i.e. a new mindset of ownership, responsibility and autonomy.'), 'Promotional site for the 2016 Drucker Forum' ]
    ]
    quote = random.choice(quotes)
    quote = f"{quote[0]}\n\n{quote[1]}"
    pprint(f"Open Source Quote of the Day: {quote}")
    do_post(text)


def welcome():
    hours = 6 if not settings.DEBUG else 1000
    limit = 30
    prompts = [
        'How is everyone doing today?',
        'Whats everyone hacking on today?',
        'How did you find out about Gitcoin?',
        'What cool stuff are you working on?',
        'Whats on everyones mind? Why\'d you join gitcoin? Got any questions?',
        'What brings you here?',
        f'Happy {datetime.now().strftime("%a")}!',
        f'How is your {datetime.now().strftime("%a")}!?!',
    ]
    if datetime.now().weekday():
        prompts += [
            "Whats everyone working on this week?"
        ]
    else:
        prompts += [
            "How is everyones weekend?"
            "Whats good this weekend?"
            "Hacking on anything good this weekend?"
        ]

    prompt1 = random.choice(prompts)

    prompts = [
        'Lets perhaps get them started with a few tips / kudos? 💎',
        'Lets me sure they feel welcome 🚪',
        'Say hi everyone! 💬',
        "Lets start a tipping conga line.  🕺🕺🕺🕺💃💃💃💃 Tip the person above you. The person below you should tip you, and so on!",
        'Lets send a few kudos to them to get them started on the platform. 💎 ',
    ]
    prompt2 = random.choice(prompts)
    welcome_to = Profile.objects.filter(created_on__gt=timezone.now() - timezone.timedelta(hours=hours)).visible().order_by('?').values_list('handle', flat=True)[:limit]
    welcome_to = [f"@{ele}" for ele in welcome_to]

    if len(welcome_to) < 2:
        return

    welcome_to = ", ".join(welcome_to)
    pprint(f"Welcome to {welcome_to} - {prompt1}")
    pprint("")
    pprint(f"{prompt2}")
    do_post(text)

def results():
    from perftools.models import JSONStore
    js = JSONStore.objects.get(view='results', key='')
    data = js.data

    pprint("================================")
    pprint(f"== Network Stats Update {datetime.now().strftime('%m/%d/%Y')} 👇")
    pprint("================================")
    pprint('Lifetime:')
    pprint(f"- Transactions: {data['transactions']}")
    pprint(f"- Hours Worked: {data['hours']}")
    pprint(f"- Value Transfered: ${round(data['universe_total_usd'], 2)}")
    pprint('Last Month:')
    pprint(f"- Monthly Active Developers: {round(data['mau'])}")
    pprint(f"- Value Transfered Last Month: ${data['last_month_amount']}k (${round(data['last_month_amount_hourly_business_hours'])}/business-hour)")

    hours = 24 * 7 if not settings.DEBUG else 1000
    limit = 10
    earnings = Earning.objects.filter(created_on__gt=timezone.now()-timezone.timedelta(hours=hours))
    earnings = earnings.filter(network='mainnet')
    tx = earnings.count()
    earnings = sum(earnings.exclude(value_usd__isnull=True).values_list('value_usd', flat=True))
    pprint('Last Week:')
    pprint(f"- Transactions: {tx}")
    pprint(f"- Value Transfered: ${earnings}")

    hours = 24 if not settings.DEBUG else 1000
    limit = 10
    earnings = Earning.objects.filter(created_on__gt=timezone.now()-timezone.timedelta(hours=hours))
    earnings = earnings.filter(network='mainnet')
    tx = earnings.count()
    earnings = sum(earnings.exclude(value_usd__isnull=True).values_list('value_usd', flat=True))
    pprint('Yesterday:')
    pprint(f"- Transactions: {tx}")
    pprint(f"- Value Transfered: ${earnings}")

    pprint("=======================")
    pprint("More @ https://gitcoin.co/results/")
    pprint("=======================")

    do_post(text)



def earners():
    hours = 24 if not settings.DEBUG else 1000
    limit = 10

    earnings = Earning.objects.filter(created_on__gt=timezone.now()-timezone.timedelta(hours=hours))
    earnings = earnings.filter(network='mainnet')

    amounts = {}

    for earning in earnings:
        if not earning.to_profile:
            continue
        handle = earning.to_profile.handle
        if handle not in amounts.keys():
            amounts[handle] = 0
        if earning.value_usd:
            amounts[handle] += earning.value_usd
    amounts = sorted(amounts.items(), key=operator.itemgetter(1), reverse=True)

    pprint("================================")
    pprint("== Congrats to the Daily Top Earners 👇")
    pprint("================================")
    pprint("")
    counter = 0
    if len(amounts) < 2:
        return
    for amount in amounts[:limit]:
        counter += 1
        pprint(f"{counter}) @{amount[0]} - ${round(amount[1], 0)}")

    pprint("")
    pprint("=======================")
    pprint("Kudos for Growing Open Source! 🌳 ")
    pprint(" ( https://gitcoin.co/mission ) ")
    pprint("More Stats @ https://gitcoin.co/leaderboard/")
    pprint("=======================")

    do_post(text)

def grants():
    from grants.views import clr_active, clr_round
    if not clr_active:
        return

    ############################################################################3
    # total stats
    ############################################################################3

    start = next_round_start
    end = round_end
    day = (datetime.now() - start).days
    pprint("")
    pprint("================================")
    pprint(f"== BEEP BOOP BOP ⚡️          ")
    pprint(f"== Grants Round {clr_round} ({start.strftime('%m/%d/%Y')} ➡️ {end.strftime('%m/%d/%Y')})")
    pprint(f"== Day {day} Stats 💰🌲👇 ")
    pprint("================================")
    pprint("")

    must_be_successful = True

    contributions = Contribution.objects.filter(created_on__gt=start, created_on__lt=end)
    if must_be_successful:
        contributions = contributions.filter(success=True)
    pfs = PhantomFunding.objects.filter(created_on__gt=start, created_on__lt=end)
    total = contributions.count() + pfs.count()

    current_carts = CartActivity.objects.filter(latest=True)
    num_carts = 0
    amount_in_carts = {}
    for ca in current_carts:
        for item in ca.metadata:
            currency, amount = item['grant_donation_currency'], item['grant_donation_amount']
            if currency not in amount_in_carts.keys():
                amount_in_carts[currency] = 0
            if amount:
                amount_in_carts[currency] += float(amount)

    contributors = len(set(list(contributions.values_list('subscription__contributor_profile', flat=True)) + list(pfs.values_list('profile', flat=True))))
    amount = sum([float(contrib.subscription.amount_per_period_usdt) for contrib in contributions] + [float(pf.value) for pf in pfs])

    pprint(f"Contributions: {total}")
    pprint(f"Contributors: {contributors}")
    pprint(f'Amount Raised: ${round(amount, 2)}')
    pprint(f"In carts, but not yet checked out yet:")
    for key, val in amount_in_carts.items():
        pprint(f"- {round(val, 2)} {key}")

    ############################################################################3
    # top contributors
    ############################################################################3

    all_contributors_by_amount = {}
    all_contributors_by_num = {}
    for contrib in contributions:
        key = contrib.subscription.contributor_profile.handle
        if key not in all_contributors_by_amount.keys():
            all_contributors_by_amount[key] = 0
            all_contributors_by_num[key] = 0

        all_contributors_by_num[key] += 1
        all_contributors_by_amount[key] += contrib.subscription.amount_per_period_usdt

    all_contributors_by_num = sorted(all_contributors_by_num.items(), key=operator.itemgetter(1))
    all_contributors_by_amount = sorted(all_contributors_by_amount.items(), key=operator.itemgetter(1))
    all_contributors_by_num.reverse()
    all_contributors_by_amount.reverse()

    pprint("")
    pprint("=======================")
    pprint("")

    limit = 25
    pprint(f"Top Contributors by Num Contributions (Round {clr_round})")
    counter = 0
    for obj in all_contributors_by_num[0:limit]:
        counter += 1
        pprint(f"{counter} - {str(round(obj[1]))} by @{obj[0]}")

    pprint("")
    pprint("=======================")
    pprint("")

    counter = 0
    pprint(f"Top Contributors by Amount of Contributions (Round {clr_round})")
    for obj in all_contributors_by_amount[0:limit]:
        counter += 1
        pprint(f"{counter} - ${str(round(obj[1], 2))} by @{obj[0]}")



    ############################################################################3
    # new feature stats for round {clr_round} 
    ############################################################################3

    subs_stats = False
    if subs_stats:
        subs = Subscription.objects.filter(created_on__gt=timezone.now()-timezone.timedelta(hours=48))
        subs = subs.filter(subscription_contribution__success=True)
        pprint(subs.count())
        pprint(subs.filter(num_tx_approved__gt=1).count())
        pprint(subs.filter(is_postive_vote=False).count())


    ############################################################################3
    # all contributions export
    ############################################################################3

    start = next_round_start
    end = round_end
    export = False
    if export:
        contributions = Contribution.objects.filter(created_on__gt=start, created_on__lt=end, success=True, subscription__network='mainnet')[0:100]
        pprint("tx_id1, tx_id2, from address, amount, amount_minus_gitcoin, token_address")
        for contribution in contributions:
            pprint(contribution.tx_id, 
                contribution.split_tx_id,
                contribution.subscription.contributor_address,
                contribution.subscription.amount_per_period, 
                contribution.subscription.amount_per_period_minus_gas_price,
                contribution.subscription.token_address)

    pprint("")
    pprint("=======================")
    pprint("More @")
    pprint("⌗ https://gitcoin.co/grants/activity/")
    pprint("⌗ https://gitcoin.co/grants/stats/")
    pprint("=======================")

    global text
    do_post(text)
class Command(BaseCommand):

    help = 'puts grants stats on town suqare'

    def add_arguments(self, parser):
        parser.add_argument('what', 
            default='',
            type=str,
            help="what to post"
            )

    def handle(self, *args, **options):
        if options['what'] == 'results':
            results()
        elif options['what'] == 'quote':
            quote()
        elif options['what'] == 'earners':
            earners()
        elif options['what'] == 'grants':
            grants()
        elif options['what'] == 'welcome':
            welcome()
        else:
            print('option not found')
