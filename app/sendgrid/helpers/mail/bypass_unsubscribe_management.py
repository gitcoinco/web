class BypassUnsubscribeManagement(object):
    """Setting for Bypass Unsubscribe Management


    Allows you to bypass the global unsubscribe list to ensure that the email is delivered to recipients.
    Bounce and spam report lists will still be checked; addresses on these other lists will not receive
    the message. This filter applies only to global unsubscribes and will not bypass group unsubscribes.
    This filter cannot be combined with the bypass_list_management filter.
    """

    def __init__(self, enable=None):
        """Create a BypassUnsubscribeManagement.

        :param enable: Whether emails should bypass unsubscribe management.
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
        Get a JSON-ready representation of this BypassUnsubscribeManagement.

        :returns: This BypassUnsubscribeManagement, ready for use in a request body.
        :rtype: dict
        """
        bypass_unsubscribe_management = {}
        if self.enable is not None:
            bypass_unsubscribe_management["enable"] = self.enable
        return bypass_unsubscribe_management
