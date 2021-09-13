"""
This library allows you to quickly and easily use the Twilio Email Web API v3 via Python.

For more information on this library, see the README on GitHub.
    http://github.com/sendgrid/sendgrid-python
For more information on the Twilio SendGrid v3 API, see the v3 docs:
    http://sendgrid.com/docs/API_Reference/api_v3.html
For the user guide, code examples, and more, visit the main docs page:
    http://sendgrid.com/docs/index.html

This file provides the Twilio Email API Client.
"""
import os
from base64 import b64encode

from .base_interface import BaseInterface


class TwilioEmailAPIClient(BaseInterface):
    """The Twilio Email API Client.

    Use this object to interact with the v3 API. For example:
        mail_client = sendgrid.TwilioEmailAPIClient(os.environ.get('TWILIO_API_KEY'),
                                                    os.environ.get('TWILIO_API_SECRET'))
        ...
        mail = Mail(from_email, subject, to_email, content)
        response = mail_client.send(mail)

    For examples and detailed use instructions, see
        https://github.com/sendgrid/sendgrid-python
    """

    def __init__(
            self,
            username=None,
            password=None,
            host='https://email.twilio.com',
            impersonate_subuser=None):
        """
        Construct the Twilio Email v3 API object.
        Note that the underlying client is being set up during initialization,
        therefore changing attributes in runtime will not affect HTTP client
        behaviour.

        :param username: Twilio Email API key SID or Account SID to use. If not
                         provided, value will be read from the environment
                         variable "TWILIO_API_KEY" or "TWILIO_ACCOUNT_SID"
        :type username: string
        :param password: Twilio Email API key secret or Account Auth Token to
                         use. If not provided, value will be read from the
                         environment variable "TWILIO_API_SECRET" or
                         "TWILIO_AUTH_TOKEN"
        :type password: string
        :param impersonate_subuser: the subuser to impersonate. Will be passed
                                    by "On-Behalf-Of" header by underlying
                                    client. See
                                    https://sendgrid.com/docs/User_Guide/Settings/subusers.html
                                    for more details
        :type impersonate_subuser: string
        :param host: base URL for API calls
        :type host: string
        """
        self.username = username or \
                        os.environ.get('TWILIO_API_KEY') or \
                        os.environ.get('TWILIO_ACCOUNT_SID')

        self.password = password or \
                        os.environ.get('TWILIO_API_SECRET') or \
                        os.environ.get('TWILIO_AUTH_TOKEN')

        auth = 'Basic ' + b64encode('{}:{}'.format(self.username, self.password).encode()).decode()

        super(TwilioEmailAPIClient, self).__init__(auth, host, impersonate_subuser)
