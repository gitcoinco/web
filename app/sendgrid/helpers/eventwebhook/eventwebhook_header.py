class EventWebhookHeader:
    """
    This class lists headers that get posted to the webhook. Read the docs for
    more details: https://sendgrid.com/docs/for-developers/tracking-events/event
    """
    SIGNATURE = 'X-Twilio-Email-Event-Webhook-Signature'
    TIMESTAMP = 'X-Twilio-Email-Event-Webhook-Timestamp'

    def __init__(self):
        pass
