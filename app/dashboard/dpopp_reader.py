# libs for processing the deterministic stream location
import hashlib
import json

import dag_cbor
# Making GET requests against the ceramic_url to read streams
import requests

# Base36 is the expected encoding for a ceramic streamID
from .base36 import base36

# Location of a ceramic node that we can read state from
ceramic_url = "https://ceramic.staging.dpopp.gitcoin.co"

# Ceramic definition id for CryptoAccounts on the ceramic model
ceramic_crypto_accounts_stream_id = "kjzl6cwe1jw149z4rvwzi56mjjukafta30kojzktd9dsrgqdgz4wlnceu59f95f"
# Ceramic definition id for dPoPP passport
ceramic_passport_stream_id = "kjzl6cwe1jw14b5pv8zucigpz0sc2lh9z5l0ztdrvqw5y1xt2tvz8cjt34bkub9"

def get_did(address, network="1"):
    # default to no did found
    did = False

    # attempt to discover the did associated to the account via a caip10 link
    try:
        # grab did that this address controls (defaults to "on mainnet")
        data = {"type":1,"genesis":{"header":{"controllers":[f"{address.lower()}@eip155:{network}"],"family":f"caip10-eip155:{network}"}},"opts":{"anchor":False,"publish":True,"sync":0,"pin":True}}
        response = requests.post(url=f"{ceramic_url}/api/v0/streams", json=data)
        did = response.json()['state']['content']
    except requests.exceptions.RequestException:
        pass
    except:
        pass

    # returns the did associated with the address on the given network
    return did

def clean_address(address, network="1"):
    # strip addresses suffix like @eip155:1, @eip155:4, @eip155:137
    return address.split("@eip155")[0]

def get_stream_ids(did, ids=[ceramic_crypto_accounts_stream_id, ceramic_passport_stream_id]):
    # encode the input genesis with cborg (Concise Binary Object Representation)
    input_bytes = dag_cbor.encode({"header":{"controllers":[did],"family":"IDX"}})
    # hash the input_bytes and pad with STREAMID_CODEC and type (as bytes)
    stream_id_digest = [206, 1, 0, 1, 113, 18, 32] + list(bytearray(hashlib.sha256(input_bytes).digest()))

    # encode the bytes array with base36 to get the derministic streamId from the DIDs genesis
    stream_id = base36(stream_id_digest)

    # return streams in a dict
    streams = {}

    try:
        # get the stream content for the given did according to its genesis stream_id
        stream_response = requests.get(f"{ceramic_url}/api/v0/streams/{stream_id}")
        # get the state and default to empty content
        state = stream_response.json().get('state', { "content": {}})
        # check for a next record else pull from content
        content = state['next']['content'] if state.get('next') else state['content']

        # return streams for the given ids
        for linked_stream_id in ids:
            # pull CryptoAccounts streamID from expected location (kjzl6cwe1jw149z4rvwzi56mjjukafta30kojzktd9dsrgqdgz4wlnceu59f95f)
            streams[linked_stream_id] = content[linked_stream_id].replace("ceramic://", "") if content.get(linked_stream_id) else False
    except requests.exceptions.RequestException:
        pass
    except:
        pass

    # return the CryptoAccounts streamID (without the ceramic:// prefix)
    return streams

def get_crypto_accounts(did="", stream_ids=[]):
    # get streamIds if non are provided
    stream_ids = stream_ids if len(stream_ids) > 0 else get_stream_ids(did, [ceramic_crypto_accounts_stream_id])

    # create an empty list of accounts
    crypto_accounts = []

    # attempt to pull content
    try:
        # pull the CryptoAccounts streamID
        stream_id = stream_ids[ceramic_crypto_accounts_stream_id]

        # get the stream content from given streamID
        stream_response = requests.get(f"{ceramic_url}/api/v0/streams/{stream_id}")
        # get the state and default to empty content
        state = stream_response.json().get('state', {"content": {}})

        # check for a next record else pull from content
        content = state['next']['content'] if state.get('next') else state['content']

        # extract all accounts
        crypto_accounts = list(map(clean_address, content.keys()))
    except requests.exceptions.RequestException:
        pass
    except:
        pass

    # return a list of wallet address without the @eip155:1 suffix
    return crypto_accounts

def get_passport(did="", stream_ids=[]):
    # get streamIds if non are provided
    stream_ids = stream_ids if len(stream_ids) > 0 else get_stream_ids(did, [ceramic_passport_stream_id])

    # attempt to pull content
    passport = get_stamps(get_passport_stream(stream_ids))

    # return a list of wallet address without the @eip155:1 suffix
    return passport

def get_stamps(passport):
    # hydrate stamps contained within the passport
    if passport and passport['stamps']:
        for (index, stamp) in enumerate(passport['stamps']):
            passport['stamps'][index] = get_stamp_stream(stamp)

    return passport

def get_passport_stream(stream_ids=[]):
    # create an empty passport
    passport = {
        "stamps": []
    }

    try:
        # pull the CryptoAccounts streamID
        stream_id = stream_ids[ceramic_passport_stream_id]
        # get the stream content from given streamID
        stream_response = requests.get(f"{ceramic_url}/api/v0/streams/{stream_id}")
        # get back the state object
        state = stream_response.json().get('state', {"content": {}})

        # check for a next record else pull from content
        passport = state['next']['content'] if state.get('next') else state['content']
    except requests.exceptions.RequestException:
        pass
    except:
        pass

    return passport

def get_stamp_stream(stamp):
    try:
        stamp['credential'] = stamp['credential'].replace("ceramic://", "")
        stamp_response = requests.get(f"{ceramic_url}/api/v0/streams/{stamp['credential']}")
        # get back the state object
        state = stamp_response.json().get('state', {"content": {}})
        # check for a next record else pull from content
        stamp['credential'] = state['next']['content'] if state.get('next') else state['content']
    except requests.exceptions.RequestException:
        pass
    except:
        pass

    return stamp
