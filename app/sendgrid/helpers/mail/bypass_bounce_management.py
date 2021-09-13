class BypassBounceManagement(object):
    """Setting for Bypass Bounce Management


    Allows you to bypass the bounce list to ensure that the email is delivered to recipients.
    Spam report and unsubscribe lists will still be checked; addresses on these other lists
    will not receive the message. This filter cannot be combined with the bypass_list_management filter.
    """

    def __init__(self, enable=None):
        """Create a BypassBounceManagement.

        :param enable: Whether emails should bypass bounce management.
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
        Get a JSON-ready representation of this BypassBounceManagement.

        :returns: This BypassBounceManagement, ready for use in a request body.
        :rtype: dict
        """
        bypass_bounce_management = {}
        if self.enable is not None:
            bypass_bounce_management["enable"] = self.enable
        return bypass_bounce_management
