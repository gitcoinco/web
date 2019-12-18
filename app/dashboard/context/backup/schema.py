# Visibility
private = 'private'
public = 'public'

# Type
string_type = 'string'
numeric_type = 'number'
array_type = 'array'
boolean_type = 'boolean'

# Format
url_format = 'url'
date_format = 'ISO 8601'


# partials

def number(privacy, title='', desc=''):
    return {
        'visibility': privacy,
        'type': {'base': numeric_type, 'composed': False},
        'title': title,
        'desc': desc
    }


def string(privacy, title='', desc=''):
    return {
        'visibility': privacy,
        'type': {'base': string_type, 'composed': False},
        'title': title,
        'desc': desc
    }


def url(privacy, title='', desc=''):
    return {
        'visibility': privacy,
        'type': {'base': string_type, 'composed': False, 'format': url_format},
        'title': title,
        'desc': desc
    }


def array(elements, privacy, title='', desc=''):
    return {
       'visibility': privacy,
       'type': {'base': array_type, 'composed': True, 'elements': elements},
       'title': title,
       'desc': desc
    }


def boolean(privacy, title='', desc=''):
    return {
        'visibility': privacy,
        'type': {'base': boolean_type, 'composed': False},
        'title': title,
        'desc': desc
    }

def choice(options, privacy, title='', desc=''):
    return {
        'visibility': privacy,
        'type': {'base': string_type, 'composed': False, 'format': url_format, 'choices': options},
        'title': title,
        'desc': desc
    }


def date(privacy, title='', desc=''):
    return {
        'visibility': privacy,
        'type': {'base': string_type, 'composed': False, 'format': date_format},
        'title': title,
        'desc': desc
    }


schema = {
    'version': 0.1,
    'availableSpaces': [
        'profile',
        'interests',
        'bounties',
        'tips',
        'acknowledgment',
        'preferences',
        'activities'
    ],
    'definitions': {
        'profile': {
            'collection': False,
            'fields':{
                'name': string(privacy=public, desc='Fullname on the platform'),
                'handle': string(privacy=public, desc='Identifier on the gitcoin platform'),
                'tagline': string(privacy=public),
                'keywords': array(elements=[string_type], privacy=public, desc='Tags related to the users'),
                'avatar': url(privacy=public, desc='URL to the avatar used on the gitcoin profle'),
                'wallpaper': url(privacy=public, desc='URL to the background used on the gitcoin profle'),
                'funder': boolean(privacy=public, desc='Determine if the user is funder'),
                'hunter': boolean(privacy=public, desc='Determine if the user is hunter'),
                'gitcoin.last_login': date(privacy=private, title='Last login', desc='Last login on the gitcoin platform'),
                'gitcoin.date_joined': date(privacy=private, title='Date joined', desc='Date joined on the gitcoin platform'),
            }
        },
        'bounties': {
            'collection': True,
            'key': '<provider>.<id>',
            'fields': {
                'id': number(privacy=public),
                'state': choice(options=[], privacy=public),
                'title': string(privacy=public),
                'created': date(privacy=public),
                'token_name': string(privacy=public),
                'token_address': string(privacy=public),
                'bounty_type': choice(options=[], privacy=public),
                'project_length': string(privacy=public),
                'estimated_hours': string(privacy=public),
                'experience_level': choice(options=[], privacy=public),
                'provider': choice(options=['gitcoin'], privacy=public),
                'issue_provider': choice(options=['github', 'bitbucket', 'gitlab'], privacy=public),
                'reserved_for_user': boolean(privacy=public),
                'is_open': boolean(privacy=public),
                'expires_date': date(privacy=public),
                'funding_organisation': string(privacy=public),
                'standard_bounties_id': number(privacy=public),
                'accepted': boolean(privacy=public),
                'fulfillment_accepted_on': boolean(privacy=public),
                'fulfillment_submitted_on': boolean(privacy=public),
                'fulfillment_started_on': boolean(privacy=public),
                'canceled_on': boolean(privacy=public),
                'canceled_bounty_reason': string(privacy=public),
                'project_type': choice(options=[], privacy=public),
                'bounty_categories': array(elements=[string_type], privacy=public),
                'canonical_url': url(privacy=public),
                'value_in_token': number(privacy=private),
                'value_in_usdt': number(privacy=private),
                'issue_url': url(privacy=private),
                'submissions_comment': string(privacy=private)
            }
        }
    }
}
