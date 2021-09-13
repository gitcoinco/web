from ellipticcurve.ecdsa import Ecdsa
from ellipticcurve.publicKey import PublicKey
from ellipticcurve.signature import Signature

from .eventwebhook_header import EventWebhookHeader

class EventWebhook:
    """
    This class allows you to use the Event Webhook feature. Read the docs for
    more details: https://sendgrid.com/docs/for-developers/tracking-events/event
    """

    def __init__(self, public_key=None):
        """
        Construct the Event Webhook verifier object
        :param public_key: verification key under Mail Settings
        :type public_key: string
        """
        self.public_key = self.convert_public_key_to_ecdsa(public_key) if public_key else public_key

    def convert_public_key_to_ecdsa(self, public_key):
        """
        Convert the public key string to a ECPublicKey.

        :param public_key: verification key under Mail Settings
        :type public_key string
        :return: public key using the ECDSA algorithm
        :rtype PublicKey
        """
        return PublicKey.fromPem(public_key)

    def verify_signature(self, payload, signature, timestamp, public_key=None):
        """
        Verify signed event webhook requests.

        :param payload: event payload in the request body
        :type payload: string
        :param signature: value obtained from the 'X-Twilio-Email-Event-Webhook-Signature' header
        :type signature: string
        :param timestamp: value obtained from the 'X-Twilio-Email-Event-Webhook-Timestamp' header
        :type timestamp: string
        :param public_key: elliptic curve public key
        :type public_key: PublicKey
        :return: true or false if signature is valid
        """
        timestamped_payload = timestamp + payload
        decoded_signature = Signature.fromBase64(signature)

        key = public_key or self.public_key
        return Ecdsa.verify(timestamped_payload, decoded_signature, key)
