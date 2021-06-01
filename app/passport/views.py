import didkit
import json
import uuid
from datetime import datetime, timedelta

from django.conf import settings
from django.http import JsonResponse

from dashboard.utils import get_web3
from eth_account.messages import defunct_hash_message

from .models import PassportRequest


def index(request):
    # setup
    player = request.GET.get('coinbase')
    network = request.GET.get('network')
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'msg': 'You must login'})

    # setup web3 interactions
    w3 = get_web3(network)
    player = w3.toChecksumAddress(player)
    contract_address_rinkeby = w3.toChecksumAddress('0xcEFBf0A9Ada7A03056dD08B470AA843ef8ca5D79')
    contract_address_mainnet = w3.toChecksumAddress('0xb4e903dc14dfe994fe291fc5b385c4718413366d')
    if network not in ['rinkeby', 'mainnet']:
        return JsonResponse({'status': 'error', 'msg': 'Unsupported network'})

    # get contract
    contract_address = contract_address_mainnet if network == 'mainnet' else contract_address_rinkeby
    abi = '[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"approved","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"operator","type":"address"},{"indexed":false,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"baseURI","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"burn","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"tokenURI","type":"string"},{"internalType":"bytes","name":"signature","type":"bytes"},{"internalType":"uint256","name":"_nonce","type":"uint256"}],"name":"createPassport","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_messageHash","type":"bytes32"}],"name":"getEthSignedMessageHash","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"string","name":"_message","type":"string"},{"internalType":"uint256","name":"_nonce","type":"uint256"}],"name":"getMessageHash","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_ethSignedMessageHash","type":"bytes32"},{"internalType":"bytes","name":"_signature","type":"bytes"}],"name":"recoverSigner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"operator","type":"address"},{"internalType":"bool","name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes","name":"sig","type":"bytes"}],"name":"splitSignature","outputs":[{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"},{"internalType":"uint8","name":"v","type":"uint8"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"index","type":"uint256"}],"name":"tokenByIndex","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint256","name":"index","type":"uint256"}],"name":"tokenOfOwnerByIndex","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"tokenURI","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_signer","type":"address"},{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"string","name":"_message","type":"string"},{"internalType":"uint256","name":"_nonce","type":"uint256"},{"internalType":"bytes","name":"signature","type":"bytes"}],"name":"verify","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"pure","type":"function"}]'
    abi = json.loads(abi)
    contract = w3.eth.contract(contract_address, abi=abi)

    # validation
    balance = contract.functions.balanceOf(player).call()
    if balance > 0:
        return JsonResponse({'status': 'error', 'msg': 'You already have a passport.  You must burn your passport before you can generate another one!'})

    # validation passed
    nonce = contract.functions.totalSupply().call() + 5
    _uuid = uuid.uuid4()
    tokenURI = f'{_uuid}'

    if request.user.profile.passport_requests.filter(network=network).exists():
        return JsonResponse({'status': 'error', 'msg': 'You already have a passport.  You must burn your passport before you can generate another one!'})

    ppr = PassportRequest.objects.create(
        profile=request.user.profile,
        nonce=nonce,
        address=player,
        uuid=_uuid,
        network=network,
        uri=tokenURI,
        )

    # sign message
    message = contract.functions.getMessageHash(player, 0, tokenURI, nonce).call()
    message_hash = defunct_hash_message(primitive=message)
    private_key = settings.PASSPORT_PK_RINKEBY if network == 'rinkeby' else settings.PASSPORT_PK_MAINNET
    signed_message = w3.eth.account.signHash(message_hash, private_key=private_key).signature.hex()

    context = {
        'status': 'success',
        'contract_address': contract_address,
        'contract_abi': abi,
        'nonce': nonce,
        'tokenURI': tokenURI,
        'hash': signed_message,
    }
    return JsonResponse(context)


def passport(request, pattern):

    passport = None
    try:
        passport = PassportRequest.objects.get(uuid=pattern)
        if not passport:
            raise Exception
    except:
        return JsonResponse({'status': 'error', 'msg': 'Not found'})

    cost_of_forgery = round((passport.profile.trust_bonus - 1) * 100, 1)
    image_url = 'https://proofofpersonhood.com/images/passport_square.png' #TODO - make dynamic based upon how many stamps user has
    personhood_score = cost_of_forgery
    context = {
        "name": "Personhood Passport",
        "description": "Proof of Personhood Passport (PoPP) is a transportable proof of personhood identity for the web3 space.",
        "image": image_url,
        'external_url': 'https://proofofpersonhood.com',
        'background_color': 'fbfbfb',
        "attributes": [
            {
                "trait_type": "personhood_score",
                "value": personhood_score,
            },
            {
                "trait_type": "cost_of_forgery",
                "value": cost_of_forgery,
            },
        ],
    }
    return JsonResponse(context)


def verifiable_credential(request):
    passport = None

    player = request.GET.get('coinbase')
    network = request.GET.get('network')

    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'msg': 'You must login'})

    cost_of_forgery = round((request.user.profile.trust_bonus - 1) * 100, 1)
    personhood_score = cost_of_forgery
    
    did = 'did:pkh:eth:' + player

    issuer = settings.POPP_VC_ISSUER
    issuance_date = datetime.utcnow().replace(microsecond=0)
    expiration_date = issuance_date + timedelta(weeks=4)

    credential = {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            {
                "ProofOfPersonhood": {
                    "@id": "https://gitcoin.co/ProofOfPersonhood",
                    "@context": {
                        "@protected": True,
                        "@version": 1.1,
                        "passport": {
                            "@id": "https://gitcoin.co/passport",
                            "@type": "https://gitcoin.co/ProofOfPersonhoodPassport",
                        },
                    },
                },
                "ProofOfPersonhoodPassport": {
                    "@id": "https://gitcoin.co/ProofOfPersonhoodPassport",
                    "@context": {
                        "@version": 1.1,
                        "@protected": True,
                        "personhood_score": "https://gitcoin.co/personhood_score",
                        "cost_of_forgery": "https://gitcoin.co/cost_of_forgery",
                    },
                },
            },
        ],
        "type": ["VerifiableCredential", "ProofOfPersonhood"],
        "issuer": issuer,
        "issuanceDate": issuance_date.isoformat() + "Z",
        "expirationDate": expiration_date.isoformat() + "Z",
        "credentialSubject": {
            "id": did,
        },
        "passport": {
            "type": ["ProofOfPersonhoodPassport"],
            "personhood_score": personhood_score,
            "cost_of_forgery": cost_of_forgery,
        },
    }

    options = {
        "proofPurpose": "assertionMethod",
        "verificationMethod": issuer + "#default",
    }

    signed = didkit.issueCredential(
        json.dumps(credential),
        json.dumps(options),
        json.dumps(settings.DIDKIT_KEY_JWK),
    )

    response = {
        "vc":json.loads(signed),
    }

    return JsonResponse(response)
