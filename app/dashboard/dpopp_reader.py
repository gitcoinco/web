# libs for processing the deterministic stream location
import dag_cbor
import hashlib

# Making GET requests against the ceramic_url to read streams
import requests

# Base36 is the expected encoding for a ceramic streamID
from .base36 import base36

# Location of a ceramic node that we can read state from
ceramic_url = "https://ceramic-clay.3boxlabs.com"
# Ceramic definition id for CryptoAccounts on the ceramic model
ceramic_crypto_accounts_stream_id = "kjzl6cwe1jw149z4rvwzi56mjjukafta30kojzktd9dsrgqdgz4wlnceu59f95f"
# Ceramic definition id for dPoPP passport
ceramic_passport_stream_id = "kjzl6cwe1jw14b5pv8zucigpz0sc2lh9z5l0ztdrvqw5y1xt2tvz8cjt34bkub9"

def clean_address(address):
    # strip addresses suffix
    return address.replace("@eip155:1", "")

def get_stream_ids(did, ids=[ceramic_crypto_accounts_stream_id, ceramic_passport_stream_id]):
    # encode the input object with cborg (Concise Binary Object Representation)
    input_bytes = dag_cbor.encode({"header":{"controllers":[did],"family":"IDX"}})
    # hash the input_bytes and pad with STREAMID_CODEC and type (as bytes)
    stream_id_digest = [206, 1, 0, 1, 113, 18, 32] + list(bytearray(hashlib.sha256(input_bytes).digest()))

    # encode the bytes array with base36 to get the derministic streamId from the DIDs genesis
    stream_id = base36(stream_id_digest)

    # return streams in a dict
    streams = {}
    content = {}

    try:
        # get the stream content for the given did according to its genesis stream_id
        stream_response = requests.get(f"{ceramic_url}/api/v0/streams/{stream_id}")
        content = stream_response.json()['state']['content']
        # return streams for the given ids
        for linked_stream_id in ids:
            # pull CryptoAccounts streamID from expected location (kjzl6cwe1jw149z4rvwzi56mjjukafta30kojzktd9dsrgqdgz4wlnceu59f95f)
            streams[linked_stream_id] = content[linked_stream_id].replace("ceramic://", "") if content[linked_stream_id] else False
    except requests.exceptions.RequestException:
        pass
    except:
        pass

    # return the CryptoAccounts streamID (without the ceramic:// prefix)
    return streams

def get_crypto_accounts(did="", stream_ids=[]):
    # use of get new streamIds
    stream_ids = stream_ids if len(stream_ids) > 0 else get_stream_ids(did, [ceramic_crypto_accounts_stream_id])

    # create an empty list of accounts
    crypto_accounts = []

    # attempt to pull content
    try:
        # pull the CryptoAccounts streamID
        stream_id = stream_ids[ceramic_crypto_accounts_stream_id]

        # get the stream content from given streamID
        stream_response = requests.get(f"{ceramic_url}/api/v0/streams/{stream_id}")
        crypto_accounts = list(map(clean_address, stream_response.json()['state']['content'].keys()))
    except requests.exceptions.RequestException:
        pass
    except:
        pass

    # return a list of wallet address without the @eip155:1 suffix
    return crypto_accounts

def get_passport(did="", stream_ids=[]):
    # use of get new streamIds
    stream_ids = stream_ids if len(stream_ids) > 0 else get_stream_ids(did, [ceramic_passport_stream_id])

    # attempt to pull content
    passport = get_stamps(get_passport_stream(stream_ids))

    # return a list of wallet address without the @eip155:1 suffix
    return passport

def get_stamps(passport):
    # hydrate stamps contained within the passport
    if passport and passport['stamps']:
        for stamp in passport['stamps']:
            stamp = get_stamp_stream(stamp)

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
        # passport contained within
        passport = stream_response.json()['state']['content']
    except requests.exceptions.RequestException:
        pass
    except:
        pass

    return passport

def get_stamp_stream(stamp):
    try:
        stamp['credential'] = stamp['credential'].replace("ceramic://", "")
        stamp_response = requests.get(f"{ceramic_url}/api/v0/streams/{stamp['credential']}")
        stamp['credential'] = stamp_response.json()['state']['content']
    except requests.exceptions.RequestException:
        pass
    except:
        pass

    return stamp
