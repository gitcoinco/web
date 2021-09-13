class BypassSpamManagement(object):
    """Setting for Bypass Spam Management

    Allows you to bypass the spam report list to ensure that the email is delivered to recipients.
    Bounce and unsubscribe lists will still be checked; addresses on these other lists will not
    receive the message. This filter cannot be combined with the bypass_list_management filter.
    """

    def __init__(self, enable=None):
        """Create a BypassSpamManagement.

        :param enable: Whether emails should bypass spam management.
        :type enable: boolean, optional
        """
        self._enable = None

        if enable is not None:
            self.enable = enable

    @property
    def enable(self):
        """Indicates if this setting is enabled.

        :rtype: boolean
        """
        return self._enable

    @enable.setter
    def enable(self, value):
        """Indicates if this setting is enabled.

        :param value: Indicates if this setting is enabled.
        :type value: boolean
        """
        self._enable = value

    def get(self):
        """
        Get a JSON-ready representation of this BypassSpamManagement.

        :returns: This BypassSpamManagement, ready for use in a request body.
        :rtype: dict
        """
        bypass_spam_management = {}
        if self.enable is not None:
            bypass_spam_management["enable"] = self.enable
        return bypass_spam_management
