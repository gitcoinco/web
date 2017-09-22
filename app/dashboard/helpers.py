from bs4 import BeautifulSoup
import datetime
from dashboard.models import Bounty, BountySyncRequest
from django.http import JsonResponse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.db import transaction
from ratelimit.decorators import ratelimit
import json
import requests

# gets title of remote html doc (github issue)
@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
def title(request):
    response = {}

    url = request.GET.get('url')
    urlVal = URLValidator()
    try:
        urlVal(url)
    except ValidationError, e:
        response['message'] = 'invalid arguments'
        return JsonResponse(response)
    try:
        html_response = requests.get(url)
    except ValidationError, e:
        response['message'] = 'could not pull back remote response'
        return JsonResponse(response)

    title = None
    try:
        soup = BeautifulSoup(html_response.text, 'html.parser')

        eles = soup.findAll("span", { "class" : "js-issue-title" })
        if len(eles):
            title = eles[0].text

        if not title and soup.title:
            title = soup.title.text

        if not title:
            for link in soup.find_all('h1'):
                print(link.text)

    except ValidationError, e:
        response['message'] = 'could not parse html'
        return JsonResponse(response)

    try:
        response['title'] = title.replace('\n', '').strip()
    except Exception as e:
        print(e)
        response['message'] = 'could not find a title'

    return JsonResponse(response)


# gets keywords of remote issue (github issue)
@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
def keywords(request):
    response = {}
    keywords = []

    url = request.GET.get('url')
    urlVal = URLValidator()
    try:
        urlVal(url)
    except ValidationError, e:
        response['message'] = 'invalid arguments'
        return JsonResponse(response)
    try:
        repo_url = None
        if '/pull' in url:
            repo_url = url.split('/pull')[0]
        if '/issue' in url:
            repo_url = url.split('/issue')[0]
        split_repo_url = repo_url.split('/')
        keywords.append(split_repo_url[-1])
        keywords.append(split_repo_url[-2])

        html_response = requests.get(repo_url)
    except ValidationError, e:
        response['message'] = 'could not pull back remote response'
        return JsonResponse(response)

    try:
        soup = BeautifulSoup(html_response.text, 'html.parser')

        eles = soup.findAll("span", {"class" : "lang"})
        for ele in eles:
            keywords.append(ele.text)

    except ValidationError, e:
        response['message'] = 'could not parse html'
        return JsonResponse(response)

    try:
        response['keywords'] = keywords
    except Exception as e:
        print(e)
        response['message'] = 'could not find a title'

    return JsonResponse(response)

def normalizeURL(url):
    if url[-1] == '/':
        url = url[0:-1]
    return url

#returns didChange if bounty has changed since last sync
# then old_bounty
# then new_bounty
def syncBountywithWeb3(bountyContract, url):
    #setup
    bountydetails = bountyContract.call().bountydetails(url)
    url = normalizeURL(url)

    #extract json
    metadata = None
    claimee_metadata = None
    try:
        metadata = json.loads(bountydetails[8])
    except Exception as e:
        print(e)
        metadata = {}
    try:
        claimee_metadata = json.loads(bountydetails[10])
    except Exception as e:
        print(e)
        claimee_metadata = {}

    #create new bounty (but only if things have changed)
    didChange = False
    old_bounties = Bounty.objects.none()
    try:
        old_bounties = Bounty.objects.filter(
            github_url=url,
            title=metadata.get('issueTitle'),
            current_bounty=True,
        ).order_by('-created_on')
        didChange = (bountydetails != old_bounties.first().raw_data)
        if not didChange:
            return (didChange, old_bounties.first(), old_bounties.first())
    except Exception as e:
        print(e)
        didChange = True

    with transaction.atomic():
        for old_bounty in old_bounties:
            old_bounty.current_bounty = False;
            old_bounty.save()
        new_bounty = Bounty.objects.create(
            title=metadata.get('issueTitle'),
            web3_created=datetime.datetime.fromtimestamp(bountydetails[7]),
            value_in_token=bountydetails[0],
            token_name=metadata.get('tokenName'),
            token_address=bountydetails[1],
            bounty_type=metadata.get('bountyType'),
            project_length=metadata.get('projectLength'),
            experience_level=metadata.get('experienceLevel'),
            github_url=url,
            bounty_owner_address=bountydetails[2],
            bounty_owner_email=metadata.get('notificationEmail', None),
            bounty_owner_github_username=metadata.get('githubUsername', None),
            claimeee_address=bountydetails[3],
            claimee_email=claimee_metadata.get('notificationEmail', None),
            claimee_github_username=claimee_metadata.get('githubUsername', None),
            is_open=bountydetails[4],
            expires_date=datetime.datetime.fromtimestamp(bountydetails[9]),
            raw_data=bountydetails,
            metadata=metadata,
            claimee_metadata=claimee_metadata,
            current_bounty=True,
            )

    return (didChange, old_bounties.first(), new_bounty)


def process_bounty_changes(old_bounty, new_bounty):

    # process bounty sync requests
    for bsr in BountySyncRequest.objects.filter(processed=False, github_url=new_bounty.github_url):
        bsr.processed = True;
        bsr.save()

    # new bounty
    null_address = '0x0000000000000000000000000000000000000000'
    if (old_bounty is None and new_bounty and new_bounty.is_open) or (not old_bounty.is_open and new_bounty.is_open):
        print('new bounty')
    elif old_bounty.claimeee_address == null_address and new_bounty.claimeee_address != null_address:
        print("new claim")
    elif old_bounty.is_open and not new_bounty.is_open:
        print("approved claim")
    elif old_bounty.claimeee_address != null_address and new_bounty.claimeee_address == null_address:
        print("rejected claim")
    else:
        print('some unknown event')

    print("TODO: process bounty changes")
