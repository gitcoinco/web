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
        'activity',
        'stats'
    ],
    'definitions': {
        'profile': {
            'collection': False,
            'fields': {
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
        },
        'interests': {
            'collection': True,
            'key': '<provider>.<id>',
            'fields': {
            }
        },
        'tips': {
            'collection': True,
            'key': '<provider>.<id>',
            'fields': {
                'id': number(privacy=public),
                'expires': date(privacy=public),
                'created': date(privacy=public),
                'comments_private': string(privacy=private),
                'status': string(privacy=public),
                'comments_public': string(privacy=public),
                'recipient': string(privacy=private),
                'sender': string(privacy=private),
                'amount': number(privacy=private),
                'token': string(privacy=public),
                'token_address': string(privacy=public),
                'rewarded_for': url(privacy=public),
                'value_in_usdt': number(privacy=private),
            }
        },
        'acknowledgment': {
            'collection': True,
            'key': '<provider>.<id>',
            'fields': {
                'id': number(privacy=public),
                'cloned_from': string(privacy=public),
                'name': string(privacy=public),
                'description': string(privacy=public),
                'image': url(privacy=public),
                'rarity': string(privacy=public),
                'tags': array(elements=[string_type], privacy=public, desc='Tags related to kudos type'),
                'platform': string(privacy=public),
                'external_url': url(privacy=public),
                'background_color': string(privacy=public),
                'txid': number(privacy=public),
                'token_id':  number(privacy=public),
                'contract': string(privacy=public),
                'hidden': boolean(privacy=public),
                'created': date(privacy=public),
                'sender': string(privacy=public),
                'recipient': string(privacy=public),
            },
        },
        'preferences': {
            'collection': False,
            'fields': {
                'hide_profile': boolean(privacy=public),
                'preferred_payout_address': string(privacy=private),
                'preferred_acknowledgment_wallet': string(privacy=private),
                'preferred_lang': string(privacy=public)
            }
        },
        'activity': {
            'collection': True,
            'key': '<provider>.<id>',
            'fields': {
                'id': number(privacy=public),
                'type': string(privacy=public),
                'resource': choice(options=['tip', 'profile', 'kudos'], privacy=public),
                'url': url(privacy=public)
            }
        },
        'stats': {
            'collection': False,
            'fields': {
                'max_tip_amount_usdt_per_tx': number(privacy=private),
                'max_tip_amount_usdt_per_week': number(privacy=private),
                'longest_streak': number(privacy=public),
                'avg_hourly_rate': string(privacy=public),
                'success_rate': number(privacy=public),
                'reliability': string(privacy=public),
                'eth_collected': number(privacy=private),
                'eth_funded': number(privacy=private),
                'contributor_leaderboard': number(privacy=public),
                'funder_leaderboard': number(privacy=public),
                'bounties_completed': number(privacy=public),
                'funded_bounties': number(privacy=public),
                'no_times_been_removed': number(privacy=public),
                'kudos_sent': number(privacy=public),
                'kudos_received': number(privacy=public),
                'tips_sent': number(privacy=public),
                'tips_received': number(privacy=public),
                'earnings_total': number(privacy=public),
                'spent_total': number(privacy=private),
                'hackathons_participated_in': number(privacy=public),
                'hackathons_funded': number(privacy=public)
            }
        },
    }
}
