# -*- coding: utf-8 -*-
"""Define the Retail utility methods and general logic.

Copyright (C) 2018 Gitcoin Core

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
import cgi
import json
import re
import statistics
import time

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import pytz
from cacheops import CacheMiss, cache
from marketing.models import Alumni, EmailSubscriber, LeaderboardRank, Stat
from requests_oauthlib import OAuth2Session

programming_languages = ['css', 'solidity', 'python', 'javascript', 'ruby', 'rust', 'html', 'design', 'java']
programming_languages_full = ['A# .NET','A# (Axiom)','A-0 System','A+','A++','ABAP','ABC','ABC ALGOL','ABLE','ABSET','ABSYS','ACC','Accent','Ace DASL','ACL2','ACT-III','Action!','ActionScript','Ada','Adenine','Agda','Agilent VEE','Agora','AIMMS','Alef','ALF','ALGOL 58','ALGOL 60','ALGOL 68','ALGOL W','Alice','Alma-0','AmbientTalk','Amiga E','AMOS','AMPL','APL','App Inventor for Androids visual block language','AppleScript','Arc','ARexx','Argus','AspectJ','Assembly language','ATS','Ateji PX','AutoHotkey','Autocoder','AutoIt','AutoLISP / Visual LISP','Averest','AWK','Axum','B','Babbage','Bash','BASIC','bc','BCPL','BeanShell','Batch (Windows/Dos)','Bertrand','BETA','Bigwig','Bistro','BitC','BLISS','Blue','Bon','Boo','Boomerang','Bourne shell','bash','ksh','BREW','BPEL','C','C--','C++','C#','C/AL','CachÃ© ObjectScript','C Shell','Caml','Candle','Cayenne','CDuce','Cecil','Cel','Cesil','Ceylon','CFEngine','CFML','Cg','Ch','Chapel','CHAIN','Charity','Charm','Chef','CHILL','CHIP-8','chomski','ChucK','CICS','Cilk','CL','Claire','Clarion','Clean','Clipper','CLIST','Clojure','CLU','CMS-2','COBOL','Cobra','CODE','CoffeeScript','Cola','ColdC','ColdFusion','COMAL','Combined Programming Language','COMIT','Common Intermediate Language','Common Lisp','COMPASS','Component Pascal','Constraint Handling Rules','Converge','Cool','Coq','Coral 66','Corn','CorVision','COWSEL','CPL','csh','CSP','Csound','CUDA','Curl','Curry','Cyclone','Cython','D','DASL','DASL','Dart','DataFlex','Datalog','DATATRIEVE','dBase','dc','DCL','Deesel','Delphi','DCL','DinkC','DIBOL','Dog','Draco','DRAKON','Dylan','DYNAMO','E','E#','Ease','Easy PL/I','Easy Programming Language','EASYTRIEVE PLUS','ECMAScript','Edinburgh IMP','EGL','Eiffel','ELAN','Elixir','Elm','Emacs Lisp','Emerald','Epigram','EPL','Erlang','es','Escapade','Escher','ESPOL','Esterel','Etoys','Euclid','Euler','Euphoria','EusLisp Robot Programming Language','CMS EXEC','EXEC 2','Executable UML','F','F#','Factor','Falcon','Fancy','Fantom','FAUST','Felix','Ferite','FFP','FjÃ¶lnir','FL','Flavors','Flex','FLOW-MATIC','FOCAL','FOCUS','FOIL','FORMAC','@Formula','Forth','Fortran','Fortress','FoxBase','FoxPro','FP','FPr','Franz Lisp','F-Script','FSProg','G','Google Apps Script','Game Maker Language','GameMonkey Script','GAMS','GAP','G-code','Genie','GDL','Gibiane','GJ','GEORGE','GLSL','GNU E','GM','Go','Go!','GOAL','GÃ¶del','Godiva','GOM (Good Old Mad)','Goo','Gosu','GOTRAN','GPSS','GraphTalk','GRASS','Groovy','Hack (programming language)','HAL/S','Hamilton C shell','Harbour','Hartmann pipelines','Haskell','Haxe','High Level Assembly','HLSL','Hop','Hope','Hugo','Hume','HyperTalk','IBM Basic assembly language','IBM HAScript','IBM Informix-4GL','IBM RPG','ICI','Icon','Id','IDL','Idris','IMP','Inform','Io','Ioke','IPL','IPTSCRAE','ISLISP','ISPF','ISWIM','J','J#','J++','JADE','Jako','JAL','Janus','JASS','Java','JavaScript','JCL','JEAN','Join Java','JOSS','Joule','JOVIAL','Joy','JScript','JScript .NET','JavaFX Script','Julia','Jython','K','Kaleidoscope','Karel','Karel++','KEE','Kixtart','KIF','Kojo','Kotlin','KRC','KRL','KUKA','KRYPTON','ksh','L','L# .NET','LabVIEW','Ladder','Lagoona','LANSA','Lasso','LaTeX','Lava','LC-3','Leda','Legoscript','LIL','LilyPond','Limbo','Limnor','LINC','Lingo','Linoleum','LIS','LISA','Lisaac','Lisp','Lite-C','Lithe','Little b','Logo','Logtalk','LPC','LSE','LSL','LiveCode','LiveScript','Lua','Lucid','Lustre','LYaPAS','Lynx','M2001','M4','Machine code','MAD','MAD/I','Magik','Magma','make','Maple','MAPPER','MARK-IV','Mary','MASM Microsoft Assembly x86','Mathematica','MATLAB','Maxima','Macsyma','Max','MaxScript','Maya (MEL)','MDL','Mercury','Mesa','Metacard','Metafont','MetaL','Microcode','MicroScript','MIIS','MillScript','MIMIC','Mirah','Miranda','MIVA Script','ML','Moby','Model 204','Modelica','Modula','Modula-2','Modula-3','Mohol','MOO','Mortran','Mouse','MPD','CIL','MSL','MUMPS','NASM','NATURAL','Napier88','Neko','Nemerle','nesC','NESL','Net.Data','NetLogo','NetRexx','NewLISP','NEWP','Newspeak','NewtonScript','NGL','Nial','Nice','Nickle','NPL','Not eXactly C','Not Quite C','NSIS','Nu','NWScript','NXT-G','o:XML','Oak','Oberon','Obix','OBJ2','Object Lisp','ObjectLOGO','Object REXX','Object Pascal','Objective-C','Objective-J','Obliq','Obol','OCaml','occam','occam-Ï€','Octave','OmniMark','Onyx','Opa','Opal','OpenCL','OpenEdge ABL','OPL','OPS5','OptimJ','Orc','ORCA/Modula-2','Oriel','Orwell','Oxygene','Oz','P#','ParaSail (programming language)','PARI/GP','Pascal','Pawn','PCASTL','PCF','PEARL','PeopleCode','Perl','PDL','PHP','Phrogram','Pico','Picolisp','Pict','Pike','PIKT','PILOT','Pipelines','Pizza','PL-11','PL/0','PL/B','PL/C','PL/I','PL/M','PL/P','PL/SQL','PL360','PLANC','PlankalkÃ¼l','Planner','PLEX','PLEXIL','Plus','POP-11','PostScript','PortablE','Powerhouse','PowerBuilder','PowerShell','PPL','Processing','Processing.js','Prograph','PROIV','Prolog','PROMAL','Promela','PROSE modeling language','PROTEL','ProvideX','Pro*C','Pure','Python','Q (equational programming language)','Q (programming language from Kx Systems)','Qalb','Qi','QtScript','QuakeC','QPL','R','R++','Racket','RAPID','Rapira','Ratfiv','Ratfor','rc','REBOL','Red','Redcode','REFAL','Reia','Revolution','rex','REXX','Rlab','RobotC','ROOP','RPG','RPL','RSL','RTL/2','Ruby','RuneScript','Rust','S','S2','S3','S-Lang','S-PLUS','SA-C','SabreTalk','SAIL','SALSA','SAM76','SAS','SASL','Sather','Sawzall','SBL','Scala','Scheme','Scilab','Scratch','Script.NET','Sed','Seed7','Self','SenseTalk','SequenceL','SETL','Shift Script','SIMPOL','Shakespeare','SIGNAL','SiMPLE','SIMSCRIPT','Simula','Simulink','SISAL','SLIP','SMALL','Smalltalk','Small Basic','SML','Snap!','SNOBOL','SPITBOL','Snowball','SOL','Span','SPARK','SPIN','SP/k','SPS','Squeak','Squirrel','SR','S/SL','Stackless Python','Starlogo','Strand','Stata','Stateflow','Subtext','SuperCollider','SuperTalk','Swift (Apple programming language)','Swift (parallel scripting language)','SYMPL','SyncCharts','SystemVerilog','T','TACL','TACPOL','TADS','TAL','Tcl','Tea','TECO','TELCOMP','TeX','TEX','TIE','Timber','TMG','Tom','TOM','Topspeed','TPU','Trac','TTM','T-SQL','TTCN','Turing','TUTOR','TXL','TypeScript','Turbo C++','Ubercode','UCSD Pascal','Umple','Unicon','Uniface','UNITY','Unix shell','UnrealScript','Vala','VBA','VBScript','Verilog','VHDL','Visual Basic','Visual Basic .NET','Visual DataFlex','Visual DialogScript','Visual Fortran','Visual FoxPro','Visual J++','Visual J#','Visual Objects','Visual Prolog','VSXu','Vvvv','WATFIV, WATFOR','WebDNA','WebQL','Windows PowerShell','Winbatch','Wolfram','Wyvern','X++','X#','X10','XBL','XC','XMOS architecture','xHarbour','XL','Xojo','XOTcl','XPL','XPL0','XQuery','XSB','XSLT','XPath','Xtend','Yorick','YQL','Z notation','Zeno','ZOPL','ZPL']

class PerformanceProfiler:

    last_time = None
    start_time = None

    def profile_time(self, name):
        if not self.last_time:
            self.last_time = time.time()
            self.start_time = time.time()
            return

        self.end_time = time.time()
        this_time = self.end_time - self.last_time
        total_time = self.end_time - self.start_time
        print(f"pulled {name} in {round(this_time,2)} seconds (total: {round(total_time,2)} sec)")
        self.last_time = time.time()


def get_github_user_profile(token):
    github = OAuth2Session(
        settings.GITHUB_CLIENT_ID,
        token=token,
    )

    creds = github.get('https://api.github.com/user').json()
    print(creds)
    return creds


def strip_html(html):
    tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
    no_tags = tag_re.sub('', html)
    txt = cgi.escape(no_tags)

    return txt


def strip_double_chars(txt, char=' '):
    new_txt = txt.replace(char+char, char)
    if new_txt == txt:
        return new_txt
    return strip_double_chars(new_txt, char)


def get_bounty_history_row(label, date, keyword):
    bounties = get_bounty_history_at_date(['done'], date, keyword)
    ecosystem = get_ecosystem_history_at_date(date, keyword)
    codefund = get_codefund_history_at_date(date, keyword)
    tips = get_tip_history_at_date(date, keyword) - ecosystem
    core_platform = bounties + tips

    print(label, date, core_platform, keyword, bounties, tips, ecosystem)
    return [
        label,
        bounties,
        tips,
        get_grants_history_at_date(date, keyword),
        get_kudos_history_at_date(date, keyword),
        codefund,
        ecosystem,
    ]


def get_bounty_history_at_date(statuses, date, keyword):
    keyword_with_prefix = f"_{keyword}" if keyword else ""
    try:
        keys = [f'bounties_{status}{keyword_with_prefix}_value' for status in statuses]
        base_stats = Stat.objects.filter(
            key__in=keys,
            ).order_by('-pk')
        return base_stats.filter(created_on__lte=date).first().val
    except Exception as e:
        print(e)
        return 0


def get_grants_history_at_date(date, keyword):
    try:
        # TODO: keyword support for grants
        base_stats = Stat.objects.filter(
            key='grants',
            ).order_by('-pk')
        return base_stats.filter(created_on__lte=date).first().val
    except Exception as e:
        print(e)
        return 0


def get_kudos_history_at_date(date, keyword):
    return get_cryptoasset_history_at_date(date, keyword, 'kudos')


def get_ecosystem_history_at_date(date, keyword):
    date = date.replace(tzinfo=None)
    amount = 0
    if date > timezone.datetime(2018, 9, 23):
        amount += 17380
    if date > timezone.datetime(2018, 10, 23):
        amount += 8021
    if date > timezone.datetime(2018, 11, 23):
        amount += 16917
    if date > timezone.datetime(2019, 1, 23):
        amount += 184043 + 24033
    if date > timezone.datetime(2018, 12, 23):
        amount += 51087.23
    return amount


def get_codefund_history_at_date(date, keyword):
    date = date.replace(tzinfo=None)
    amount = 0
    # July => Feb 2019
    # $5,500.00 $4,400.00   $9,000.00   $8,500.00   $7,450.00   $6,150.00   $9,700.00 $6,258.31
    if date > timezone.datetime(2018, 7, 23):
        amount += 5500
    if date > timezone.datetime(2018, 8, 23):
        amount += 4400
    if date > timezone.datetime(2018, 9, 23):
        amount += 9000
    if date > timezone.datetime(2018, 10, 23):
        amount += 8500
    if date > timezone.datetime(2018, 11, 23):
        amount += 7450
    if date > timezone.datetime(2018, 12, 23):
        amount += 6150
    if date > timezone.datetime(2019, 1, 9):
        amount += 9700
    if date > timezone.datetime(2019, 2, 9):
        amount += 11272
    if date > timezone.datetime(2019, 3, 9):
        amount += 18726
    if date > timezone.datetime(2019, 4, 9):
        amount += 32802
    if date > timezone.datetime(2019, 5, 9):
        amount += 39304
    if date > timezone.datetime(2019, 6, 9):
        amount += 38287.22
    if date > timezone.datetime(2019, 7, 9):
        amount += 36230
    if date > timezone.datetime(2019, 8, 9):
        amount += 0
    return amount


def get_tip_history_at_date(date, keyword):
    return get_cryptoasset_history_at_date(date, keyword, 'tips')


def get_cryptoasset_history_at_date(date, keyword, key):
    if keyword:
        # TODO - attribute tips to specific keywords
        return 0
    try:
        base_stats = Stat.objects.filter(
            key=f'{key}_value',
            ).order_by('-pk')
        return base_stats.filter(created_on__lte=date).first().val
    except Exception as e:
        print(e)
        return 0


def get_history(base_stats, copy, num_months=6):
    today = base_stats.first().val if base_stats.exists() else 0

    # slack ticks
    increment = 1000
    ticks = json.dumps(list(x * increment for x in range(0, int(today/increment)+1)))
    history = [
        ['When', copy],
        ['Launch', 0],
    ]
    _range = list(range(1, num_months))
    _range.reverse()
    for i in _range:
        try:
            plural = 's' if i != 1 else ''
            before_then = (timezone.now() - timezone.timedelta(days=i*30))
            val = base_stats.filter(created_on__lt=before_then).order_by('-created_on').first().val
            history = history + [[f'{i} month{plural} ago', val], ]
        except Exception:
            pass

    history = history + [['Today', today], ]
    history = json.dumps(history)
    return history, ticks


def get_completion_rate(keyword):
    from dashboard.models import Bounty
    base_bounties = Bounty.objects.current().filter(network='mainnet', idx_status__in=['done', 'expired', 'cancelled'])
    if keyword:
        base_bounties = base_bounties.filter(raw_data__icontains=keyword)
    eligible_bounties = base_bounties.filter(created_on__gt=(timezone.now() - timezone.timedelta(days=60)))
    eligible_bounties = eligible_bounties.exclude(interested__isnull=True)
    completed_bounties = eligible_bounties.filter(idx_status__in=['done']).count()
    not_completed_bounties = eligible_bounties.filter(idx_status__in=['expired', 'cancelled']).count()
    total_bounties = completed_bounties + not_completed_bounties

    try:
        return ((completed_bounties * 1.0 / total_bounties)) * 100
    except ZeroDivisionError:
        return 0


def get_funder_receiver_stats(keyword):
    from dashboard.models import Bounty, BountyFulfillment, Tip
    base_bounties = Bounty.objects.current().filter(network='mainnet')
    if keyword:
        base_bounties = base_bounties.filter(raw_data__icontains=keyword)

    eligible_bounties = base_bounties
    eligible_bounty_fulfillments = BountyFulfillment.objects.filter(bounty__in=base_bounties)
    eligible_tips = Tip.objects.filter(network='mainnet')

    bounty_funders = list(eligible_bounties.values_list('bounty_owner_address', flat=True))
    tip_funders = list(eligible_tips.values_list('from_address', flat=True))
    tip_recipients = list(eligible_tips.values_list('receive_address', flat=True))
    bounty_recipients = list(eligible_bounty_fulfillments.values_list('fulfiller_address', flat=True))

    tip_values = [tip.value_in_usdt for tip in eligible_tips]
    bounty_values = [bounty.value_in_usdt for bounty in eligible_bounties]
    all_values = bounty_values + tip_values

    bounty_value = sum([float(ele) for ele in bounty_values if ele])
    tip_value = sum([float(ele) for ele in tip_values if ele])
    all_value = [float(ele) for ele in all_values if ele]

    num_funders = len(set(bounty_funders + tip_funders))
    num_recipients = len(set(bounty_recipients + tip_recipients))
    num_transactions = eligible_tips.count() + eligible_bounties.count()

    total_value = bounty_value + tip_value
    avg_value = round(total_value / num_transactions)
    median_value = statistics.median(all_value)

    return {
        'funders': num_funders,
        'recipients': num_recipients,
        'transactions': num_transactions,
        'avg_value': avg_value,
        'median_value': median_value,
    }


def get_base_done_bounties(keyword):
    from dashboard.models import Bounty
    base_bounties = Bounty.objects.current().filter(network='mainnet', idx_status__in=['done', 'expired', 'cancelled'])
    if keyword:
        base_bounties = base_bounties.filter(raw_data__icontains=keyword)
    return base_bounties


def is_valid_bounty_for_headline_hourly_rate(bounty):
    hourly_rate = bounty.hourly_rate
    if None is hourly_rate:
        return False

    # smaller bounties were skewing the results
    min_hours = 3
    min_value_usdt = 300
    if bounty.value_in_usdt < min_value_usdt:
        return False
    for ful in bounty.fulfillments.filter(accepted=True):
        if ful.fulfiller_hours_worked and ful.fulfiller_hours_worked < min_hours:
            return False

    return True


def get_hourly_rate_distribution(keyword, bounty_value_range=None, methodology=None):
    if not methodology:
        methodology = 'quartile' if not keyword else 'minmax'
    base_bounties = get_base_done_bounties(keyword)
    if bounty_value_range:
        base_bounties = base_bounties.filter(_val_usd_db__lt=bounty_value_range[1], _val_usd_db__gt=bounty_value_range[0])
        hourly_rates = [ele.hourly_rate for ele in base_bounties if ele.hourly_rate is not None]
        # print(bounty_value_range, len(hourly_rates))
    else:
        hourly_rates = [ele.hourly_rate for ele in base_bounties if is_valid_bounty_for_headline_hourly_rate(ele)]
    if len(hourly_rates) == 1:
        return f"${round(hourly_rates[0], 2)}"
    if len(hourly_rates) < 2:
        return ""
    if methodology == 'median_stdddev':
        stddev_divisor = 1
        median = int(statistics.median(hourly_rates))
        stddev = int(statistics.stdev(hourly_rates))
        min_hourly_rate = median - int(stddev/stddev_divisor)
        max_hourly_rate = median + int(stddev/stddev_divisor)
    elif methodology == 'quartile':
        hourly_rates.sort()
        num_quarters = 4
        first_quarter = int(len(hourly_rates)/num_quarters)
        third_quarter = first_quarter * (num_quarters-1)
        min_hourly_rate = int(hourly_rates[first_quarter])
        max_hourly_rate = int(hourly_rates[third_quarter])
    elif methodology == 'hardcode':
        min_hourly_rate = '15'
        max_hourly_rate = '120'
    else:
        min_hourly_rate = int(min(hourly_rates)) if len(hourly_rates) else 'n/a'
        max_hourly_rate = int(max(hourly_rates)) if len(hourly_rates) else 'n/a'
    return f'${min_hourly_rate} - ${max_hourly_rate}'


def get_bounty_median_turnaround_time(func='turnaround_time_started', keyword=None):
    base_bounties = get_base_done_bounties(keyword)
    eligible_bounties = base_bounties.exclude(idx_status='open') \
        .filter(created_on__gt=(timezone.now() - timezone.timedelta(days=60)))
    pickup_time_hours = []
    for bounty in eligible_bounties:
        tat = getattr(bounty, func)
        if tat:
            pickup_time_hours.append(tat / 60 / 60)

    pickup_time_hours.sort()
    try:
        return statistics.median(pickup_time_hours)
    except statistics.StatisticsError:
        return 0


def get_bounty_history(keyword=None, cumulative=True):
    bh = [
        ['', 'Bounties', 'Tips', 'Grants', 'Kudos', 'Ads', 'Ecosystem'],
    ]
    initial_stats = [
        ["December 2017", 5534, 2011, 0, 0, 0, 0],
        ["January 2018", 15930, 5093, 0, 0, 0, 0],
        ["February 2018", 16302, 7391, 0, 0, 0, 0],
        ["March 2018", 26390, 8302, 0, 0, 0, 0],
        ["April 2018", 37342, 10109, 0, 0, 0, 0],
    ]
    if not keyword:
        bh = bh + initial_stats
    for year in range(2018, 2025):
        months = range(1, 13)
        if year == 2018:
            months = range(6, 13)
        for month in months:
            day_of_month = 3 if year == 2018 and month < 7 else 1
            then = timezone.datetime(year, month, day_of_month).replace(tzinfo=pytz.UTC)
            if then < timezone.now():
                label = (then - timezone.timedelta(days=2)).strftime("%B %Y")
                row = get_bounty_history_row(label, then, keyword)
                bh.append(row)

    if timezone.now().day > 9:
        # get current month date to month
        label = timezone.now().strftime("%B %Y") + " (MTD)"
        row = get_bounty_history_row(label, timezone.now(), keyword)
        bh.append(row)

    # adjust monthly totals
    if not cumulative:
        import copy
        new_bh = copy.deepcopy(bh)
        for i in range(1, len(bh)):
            for k in range(1, len(bh[i])):
                try:
                    last_stat = int(bh[i-1][k])
                except:
                    last_stat = 0
                diff = bh[i][k] - last_stat
                new_bh[i][k] = diff
        return new_bh

    return bh


def build_stat_results(keyword=None):
    """Buidl the results page context.

    Args:
        keyword (str): The keyword to build statistic results.
    """
    from dashboard.models import Bounty, Tip
    context = {
        'active': 'results',
        'title': _('Results'),
        'card_desc': _('Gitcoin is transparent by design.  Here are some stats about our suite of OSS incentivization products.'),
    }
    pp = PerformanceProfiler()
    pp.profile_time('start')
    base_alumni = Alumni.objects.all().cache()
    base_bounties = Bounty.objects.current().filter(network='mainnet').cache()
    base_leaderboard = LeaderboardRank.objects.all().cache()

    pp.profile_time('filters')
    if keyword:
        base_email_subscribers = EmailSubscriber.objects.filter(keywords__icontains=keyword).cache()
        base_profiles = base_email_subscribers.select_related('profile')
        base_bounties = base_bounties.filter(raw_data__icontains=keyword).cache()
        profile_pks = base_profiles.values_list('profile', flat=True)
        profile_usernames = base_profiles.values_list('profile__handle', flat=True)
        profile_usernames = list(profile_usernames) + list([bounty.github_repo_name for bounty in base_bounties])
        base_alumni = base_alumni.filter(profile__in=profile_pks)
        base_leaderboard = base_leaderboard.filter(github_username__in=profile_usernames)

    context['alumni_count'] = base_alumni.count()
    pp.profile_time('alumni')
    context['count_open'] = base_bounties.filter(network='mainnet', idx_status__in=['open']).count()
    context['count_started'] = base_bounties.filter(
        network='mainnet', idx_status__in=['started', 'submitted']
    ).count()
    context['count_done'] = base_bounties.filter(network='mainnet', idx_status__in=['done']).count()

    total_count = context['count_started'] + context['count_open'] + context['count_done']
    context['pct_done'] = round(100 * context['count_done'] / total_count)
    context['pct_started'] = round(100 * context['count_started'] / total_count)
    context['pct_open'] = round(100 * context['count_open'] / total_count)

    pp.profile_time('count_*')

    # Leaderboard
    num_to_show = 30
    context['top_funders'] = base_leaderboard.filter(active=True, leaderboard='quarterly_payers') \
        .order_by('rank').values_list('github_username', flat=True)[0:num_to_show]
    pp.profile_time('funders')
    context['top_orgs'] = base_leaderboard.filter(active=True, leaderboard='quarterly_orgs') \
        .order_by('rank').values_list('github_username', flat=True)[0:num_to_show]
    pp.profile_time('orgs')
    context['top_coders'] = base_leaderboard.filter(active=True, leaderboard='quarterly_earners') \
        .order_by('rank').values_list('github_username', flat=True)[0:num_to_show]
    pp.profile_time('orgs')

    # community size
    _key = 'email_subscriberse' if not keyword else f"subscribers_with_skill_{keyword}"
    base_stats = Stat.objects.filter(key=_key).order_by('-pk').cache()
    context['members_history'], context['slack_ticks'] = get_history(base_stats, "Members")

    pp.profile_time('Stats1')

    # jdi history
    key = f'joe_dominance_index_30_{keyword}_value' if keyword else 'joe_dominance_index_30_value'
    base_stats = Stat.objects.filter(
        key=key,
        ).order_by('-pk').cache()
    num_months = int((timezone.now() - timezone.datetime(2017, 10, 1).replace(tzinfo=pytz.UTC)).days/30)
    context['jdi_history'], __ = get_history(base_stats, 'Percentage', num_months)

    pp.profile_time('Stats2')

    # bounties history
    cumulative = False
    bounty_history = get_bounty_history(keyword, cumulative)
    context['bounty_history'] = json.dumps(bounty_history)
    pp.profile_time('bounty_history')

    # Bounties
    completion_rate = get_completion_rate(keyword)
    funder_receiver_stats = get_funder_receiver_stats(keyword)
    context['funders'] = funder_receiver_stats['funders']
    context['avg_value'] = funder_receiver_stats['avg_value']
    context['median_value'] = funder_receiver_stats['median_value']
    context['transactions'] = funder_receiver_stats['transactions']
    context['recipients'] = funder_receiver_stats['recipients']
    context['audience'] = json.loads(context['members_history'])[-1][1]
    pp.profile_time('completion_rate')
    bounty_abandonment_rate = round(100 - completion_rate, 1)
    total_bounties_usd = sum(base_bounties.exclude(idx_status__in=['expired', 'cancelled', 'canceled', 'unknown']).values_list('_val_usd_db', flat=True))
    total_tips_usd = sum([
        tip.value_in_usdt
        for tip in Tip.objects.filter(network='mainnet').send_happy_path() if tip.value_in_usdt
    ])
    total_grants_usd = get_grants_history_at_date(timezone.now(), [])
    total_kudos_usd = get_kudos_history_at_date(timezone.now(), [])
    total_codefund_usd = get_codefund_history_at_date(timezone.now(), '')
    all_platforms = [
        float(total_bounties_usd),
        float(total_tips_usd),
        float(total_grants_usd),
        float(total_kudos_usd),
        float(total_codefund_usd)
        ]
    context['universe_total_usd'] = sum(all_platforms)
    pp.profile_time('universe_total_usd')
    context['max_bounty_history'] = float(context['universe_total_usd']) * .15
    context['bounty_abandonment_rate'] = bounty_abandonment_rate
    bounty_average_turnaround = round(get_bounty_median_turnaround_time('turnaround_time_submitted', keyword) / 24, 1)
    context['bounty_average_turnaround'] = f'{bounty_average_turnaround} days'
    pp.profile_time('bounty_average_turnaround')
    context['hourly_rate_distribution'] = get_hourly_rate_distribution(keyword)
    context['hourly_rate_distribution_by_range'] = {}
    usd_value_ranges = [[10, 50], [50, 150], [150, 500], [500, 1500], [1500, 5000], [5000, 50000]]
    for val_range in usd_value_ranges:
        low = val_range[0] if val_range[0] < 1000 else f"{round(val_range[0]/1000,1)}k"
        high = val_range[1] if val_range[1] < 1000 else f"{round(val_range[1]/1000,1)}k"
        key = f"${low} to ${high}"
        context['hourly_rate_distribution_by_range'][key] = get_hourly_rate_distribution(keyword, val_range, 'quartile')
    context['skill_rate_distribution_by_range'] = {}
    for programming_language in programming_languages:
        context['skill_rate_distribution_by_range'][programming_language] = get_hourly_rate_distribution(programming_language, None, 'quartile')

    context['bounty_claimed_completion_rate'] = completion_rate
    context['bounty_median_pickup_time'] = round(
        get_bounty_median_turnaround_time('turnaround_time_started', keyword), 1)
    pp.profile_time('bounty_median_pickup_time')
    from kudos.models import Token as KudosToken

    context['kudos_tokens'] = KudosToken.objects.filter(num_clones_in_wild__gt=0).order_by('-num_clones_in_wild')[0:25]
    pp.profile_time('kudos_tokens')
    pp.profile_time('final')
    context['keyword'] = keyword
    context['title'] = f"${round(context['universe_total_usd'] / 1000000, 1)}m in " + f"{keyword.capitalize() if keyword else ''} Results"
    context['programming_languages'] = ['All'] + programming_languages


    # last month data
    today = timezone.now()
    first = today.replace(day=1)
    lastMonth = first - timezone.timedelta(days=1)
    context['prev_month_name'] = lastMonth.strftime("%B %Y")
    context['prev_month_name_short'] = lastMonth.strftime("%B")
    bh = bounty_history[-1] if context['prev_month_name'] == bounty_history[-1][0] else bounty_history[-2]
    bh[0] = 0
    context['last_month_amount'] = round(sum(bh)/1000)
    context['last_month_amount_hourly'] = sum(bh) / 30 / 24
    context['last_month_amount_hourly_business_hours'] = context['last_month_amount_hourly'] / 0.222

    return context
