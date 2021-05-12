'''
    Copyright (C) 2019 Gitcoin Core

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

'''
import csv
import json
import logging
import os
import shutil
import warnings
import zipfile

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import F

import pdfrw
import sendgrid
from dashboard.models import Bounty, BountyFulfillment, Earning, Profile, Tip
from grants.models import Grant
from marketing.mails import tax_report
from python_http_client.exceptions import HTTPError, UnauthorizedError
from sendgrid.helpers.mail import Content, Email, Mail, Personalization
from sendgrid.helpers.stats import Category

logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Constant
CITY = 'city'
CODE = 'code'
COUNTER_PARTY_GITHUB_USERNAME = 'counter_party_github_username'
COUNTER_PARTY_LOCATION = 'counter_party_location'
COUNTER_PARTY_NAME = 'counter_party_name'
COUNTRY = 'country'
COUNTRY_CODE = 'country_code'
COUNTRY_NAME = 'country_name'
DATETIME = 'datetime'
LOCALITY = 'locality'
TOKEN_AMOUNT = 'token_amount'
TOKEN_NAME = 'token_name'
US = 'US'
USD_VALUE = 'usd_value'
WORKER_TYPE = 'worker_type'

# No info found
NO_AMOUNT = 'Amount not found'
NO_LOCATION = 'Location not found'
NO_NAME = 'Name not found'
NO_PROFILE = 'Profile not found'
NO_USERNAME = 'Username not found'

# Gitcoin info
BOUNTY = 'bounty'
GRANT = 'grant'
TAX_YEAR = 2019
TIP = 'tip'
WEB3_NETWORK = 'rinkeby'

# Path
MISC_1099_TEMPLATE_PATH = 'misc_1099_templates'
MISC_1099_COPY_1_TEMPLATE_PATH = os.path.join(MISC_1099_TEMPLATE_PATH, 'copy_1_template.pdf')
MISC_1099_COPY_2_TEMPLATE_PATH = os.path.join(MISC_1099_TEMPLATE_PATH, 'copy_2_template.pdf')
MISC_1099_COPY_B_TEMPLATE_PATH = os.path.join(MISC_1099_TEMPLATE_PATH, 'copy_b_template.pdf')
MISC_1099_COPY_C_TEMPLATE_PATH = os.path.join(MISC_1099_TEMPLATE_PATH, 'copy_c_template.pdf')
MISC_1099_TEMPLATES = [
                    (MISC_1099_COPY_1_TEMPLATE_PATH, 'misc_1099_copy_1.pdf'), 
                    (MISC_1099_COPY_2_TEMPLATE_PATH, 'misc_1099_copy_2.pdf'),
                    (MISC_1099_COPY_B_TEMPLATE_PATH, 'misc_1099_copy_b.pdf'),
                    (MISC_1099_COPY_C_TEMPLATE_PATH, 'misc_1099_copy_c.pdf')  
                    ]
MISC_1099_OUTPUT_PATH = 'misc_1099'
TAX_REPORT_PATH = 'tax_report'

# 1099 Fields
ADDRESS = 'address'
LOCATION = 'location'
NAME = 'name'
PAYER = 'payer'
RECIPIENT = 'recipient'

# PDF Form
ANNOT_FIELD_KEY = '/T'
ANNOT_KEY = '/Annots'
ANNOT_RECT_KEY = '/Rect'
ANNOT_VAL_KEY = '/V'
SUBTYPE_KEY = '/Subtype'
WIDGET_SUBTYPE_KEY = '/Widget'


def create_csv_record(profiles_obj, wt_obj, worker_type, us_workers, value_usd, b_ff=None):
    record = {DATETIME: wt_obj.created_on}
    counter_party_name = ''
    counter_party_gh_username = ''
    counter_party_location = ''

    if worker_type == BOUNTY:
        counter_party_gh_username = b_ff.fulfiller_github_username if b_ff.fulfiller_github_username else NO_USERNAME
    elif worker_type == TIP:
        counter_party_gh_username = wt_obj.username if wt_obj.username else NO_USERNAME
    elif worker_type == GRANT:
        counter_party = wt_obj.admin_profile
        if counter_party:
            counter_party_gh_username = counter_party.username if counter_party.username else NO_USERNAME
        else:
            counter_party = NO_PROFILE

    if counter_party_gh_username is not NO_USERNAME:
        profiles = profiles_obj.filter(handle__iexact=counter_party_gh_username)
        if profiles.exists():
            profile = profiles.first()
            counter_party_name = profile.name if profile.name else NO_NAME
            counter_party_location, us_worker = get_profile_location(profile)
            if us_worker:
                if counter_party_gh_username not in us_workers.keys():
                    us_workers[counter_party_gh_username] = 0
                if worker_type == BOUNTY:
                    us_workers[counter_party_gh_username] += value_usd
                elif worker_type == TIP:
                    us_workers[counter_party_gh_username] += value_usd
                elif worker_type == GRANT:
                    us_workers[counter_party_gh_username] += value_usd
        else:
            counter_party_name = NO_PROFILE

    if worker_type == BOUNTY:
        record[USD_VALUE] = value_usd
        record[TOKEN_AMOUNT] = wt_obj.value_in_token
        record[TOKEN_NAME] = wt_obj.token_name
    elif worker_type == TIP:
        record[USD_VALUE] = value_usd
        record[TOKEN_AMOUNT] = wt_obj.amount
        record[TOKEN_NAME] = wt_obj.tokenName
    elif worker_type == GRANT:
        record[USD_VALUE] = value_usd
        record[TOKEN_AMOUNT] = NO_AMOUNT
        record[TOKEN_NAME] = wt_obj.token_symbol

    record[COUNTER_PARTY_NAME] = counter_party_name
    record[COUNTER_PARTY_GITHUB_USERNAME] = counter_party_gh_username
    record[COUNTER_PARTY_LOCATION] = counter_party_location
    record[WORKER_TYPE] = worker_type

    return record, us_workers


def create_1099(form, recipient_path, template_path):
    data_dict = {
        'payer_details':form[PAYER][NAME] + '\n' + form[PAYER][ADDRESS] + '\n' + form[PAYER][LOCATION],
        'recipient_name':form[RECIPIENT][NAME],
        'street_address':form[RECIPIENT][ADDRESS],
        'location_details':form[RECIPIENT][LOCATION],
        'field_3':str(form[USD_VALUE]), # other income
        'field_18_a':'0', # state income a
        'field_18_b':'0' # statw income b
    } 
    template_pdf = pdfrw.PdfReader(template_path[0])
    annotations = template_pdf.pages[0][ANNOT_KEY]
    for annotation in annotations:
        if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
            if annotation[ANNOT_FIELD_KEY]:
                key = annotation[ANNOT_FIELD_KEY][1:-1]
                if key in data_dict.keys():
                    annotation.update(pdfrw.PdfDict(V='{}'.format(data_dict[key])))
    pdfrw.PdfWriter().write(os.path.join(recipient_path, template_path[1]) , template_pdf)


def get_profile_location(profile):
    us_worker = False
    location = NO_LOCATION
    location_temp = ''
    if profile.location:
        location_components = json.loads(profile.location)
        if LOCALITY in location_components:
            location_temp += location_components[LOCALITY] 
        if COUNTRY in location_components:
            country = location_components[COUNTRY]
            if location_temp:
                location_temp += ', ' + country
            else:
                location_temp += country
        if CODE in location_components:
            code = location_components[CODE]
            if location_temp:
                location_temp += ', ' + code
            else:
                location_temp += code
            # check if the worker is US based
            if code == US:
                us_worker = True
    elif profile.locations:
        location_components = profile.locations[-1] if len(profile.locations) > 0 else None
        if location_components:
            if CITY in location_components:
                location_temp += location_components[CITY]
            if COUNTRY_NAME in location_components:
                country_name = location_components[COUNTRY_NAME]
                if location_temp:
                    location_temp += ', ' + country_name
                else:
                    location_temp += country_name
            if COUNTRY_CODE in location_components:
                country_code = location_components[COUNTRY_CODE]
                if location_temp:
                    location_temp += ', ' + country_code
                else:
                    location_temp += country_code
                if location_components[COUNTRY_CODE] == US:
                    us_worker = True
    if location_temp:
        location = location_temp
    return location, us_worker


def zip_dir(username, username_path):
    zip_file_path = os.path.join(username_path, username) + '.zip'
    zipf = zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(username_path):
        for filename in files:
            if filename.endswith('.zip'):
                continue
            abs_path = os.path.join(root, filename)
            zipf.write(abs_path, abs_path.split('tax_report')[1])
    zipf.close()
    return zip_file_path


class Command(BaseCommand):

    help = 'the tax report for last year'

    def handle(self, *args, **options):
        to_emails = []
        zip_paths = []
        profiles_all = Profile.objects.all()
        tax_path = os.path.join(os.getcwd(), TAX_REPORT_PATH)
        if not tax_path:
            os.makedirs(tax_path)
        b_source_type = ContentType.objects.get(app_label='dashboard', model='bountyfulfillment')
        t_source_type = ContentType.objects.get(app_label='dashboard', model='tip')
        g_source_type = ContentType.objects.get(app_label='grants', model='contribution')
        # start new code
        total_earning = Earning.objects.filter(
                                            network=WEB3_NETWORK,
                                            created_on__year=TAX_YEAR,
                                            value_usd__gt=0
                                            ).exclude(from_profile=F('to_profile'))
        funders = {}
        for e in total_earning:
            funder = e.from_profile
            if funder == None:
                print('from_profile not defined for earning:')
                print(e)
                print('skip it')
                continue
            user = funder.handle
            if user == None:
                print('username not defined for this profile. skip this earning.')
                continue
            if user not in funders:
                funders[user] = {}
                funders[user]['csv_record'] = []
                funders[user]['us_workers'] = {}
                funders[user]['email'] = funder.email
                funders[user]['name'] = funder.name
                funders[user]['address'] = funder.address
                funders[user]['location'] = get_profile_location(funder)[0]
            # Bounty
            if e.source_type_id==b_source_type.id:
                try:
                    bf_obj = BountyFulfillment.objects.get(pk=e.source_id)
                except BountyFulfillment.DoesNotExist:
                    print("BountyFulfillment does not exist, skip this earning.")
                    continue
                try:
                    b_obj = Bounty.objects.get(pk=bf_obj.bounty_id)
                except Bounty.DoesNotExist:
                    print("Bounty does not exist, skip this earning.")
                    continue
                record, funders[user]['us_workers'] = create_csv_record(
                                                                        profiles_all, 
                                                                        b_obj, 
                                                                        BOUNTY, 
                                                                        funders[user]['us_workers'], 
                                                                        e.value_usd, 
                                                                        b_ff=bf_obj
                                                                        )
                funders[user]['csv_record'].append(record)
            # Tips
            elif e.source_type_id==t_source_type.id:
                try:
                    t_obj = Tip.objects.get(pk=e.source_id)
                except Tip.DoesNotExist:
                    print("Tip does not exist, skip this earning.")
                    continue
                record, funders[user]['us_workers'] = create_csv_record(
                                                                        profiles_all, 
                                                                        t_obj, 
                                                                        TIP, 
                                                                        funders[user]['us_workers'], 
                                                                        e.value_usd
                                                                        )
                funders[user]['csv_record'].append(record)
            # Grants
            elif e.source_type_id==g_source_type.id:
                try:
                    g_obj = Grant.objects.get(pk=e.source_id)
                except Grant.DoesNotExist:
                    print("Grant does not exist, skip this earning.")
                    continue
                record, funders[user]['us_workers'] = create_csv_record(
                                                                        profiles_all, 
                                                                        g_obj, 
                                                                        GRANT, 
                                                                        funders[user]['us_workers'], 
                                                                        e.value_usd
                                                                        )
                funders[user]['csv_record'].append(record)
            else:
                print('Source type id not valid')
                print(e.source_type_id)
        for username, info in funders.items():
            if len(info['csv_record']) > 0:
                # check for create 1099
                username_path = os.path.join(os.getcwd(), TAX_REPORT_PATH, username)
                if not os.path.isdir(username_path):
                    os.makedirs(username_path)
                misc_path = os.path.join(username_path, MISC_1099_OUTPUT_PATH)
                if not os.path.isdir(misc_path):
                    os.makedirs(misc_path)
                for us_w, usd_value in info['us_workers'].items():
                    recipient_profiles = profiles_all.filter(handle__iexact=us_w)
                    if recipient_profiles.exists():
                        recipient_profile = recipient_profiles.first()
                        # create 1099 only if total funded in usd is greater than 600$
                        if usd_value > 600:
                            recipient_path = os.path.join(misc_path, recipient_profile.username)
                            if not os.path.isdir(recipient_path):
                                os.makedirs(recipient_path)
                            form_data = {}
                            form_data[PAYER] = {}
                            form_data[PAYER][NAME] = info['name']
                            form_data[PAYER][LOCATION] = info['location']
                            form_data[PAYER][ADDRESS] = info['address']
                            form_data[RECIPIENT] = {}
                            form_data[RECIPIENT][NAME] = recipient_profile.name
                            form_data[RECIPIENT][LOCATION] = get_profile_location(recipient_profile)[0]
                            form_data[RECIPIENT][ADDRESS] = recipient_profile.address
                            form_data[USD_VALUE] = usd_value
                            for template in MISC_1099_TEMPLATES:
                                create_1099(form_data, recipient_path, template)
                # create csv
                csv_columns = [DATETIME, 
                            COUNTER_PARTY_NAME, 
                            COUNTER_PARTY_GITHUB_USERNAME, 
                            COUNTER_PARTY_LOCATION, 
                            TOKEN_AMOUNT, 
                            TOKEN_NAME, 
                            USD_VALUE, 
                            WORKER_TYPE]
                csv_file_path = os.path.join(username_path, username + '_report.csv')
                try:
                    with open(csv_file_path, 'w') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                        writer.writeheader()
                        for row in info['csv_record']:
                            writer.writerow(row)
                except IOError:
                    print("I/O error")
                if os.path.isfile(csv_file_path):
                    # zip username dir
                    zip_file_path = zip_dir(username, username_path)
                    zip_paths.append(zip_file_path)
                    to_emails.append(info['email'])

        # send emails to all funders
        tax_report(to_emails, zip_paths, TAX_YEAR)
