try:
    import rfc822
except ImportError:
    import email.utils as rfc822

try:
    basestring = basestring
except NameError:
    # Define basestring when Python >= 3.0
    basestring = str


class Email(object):
    """An email address with an optional name."""

    def __init__(self,
                 email=None,
                 name=None,
                 substitutions=None,
                 subject=None,
                 p=0,
                 dynamic_template_data=None):
        """Create an Email with the given address and name.

        Either fill the separate name and email fields, or pass all information
        in the email parameter (e.g. email="dude Fella <example@example.com>").
        :param email: Email address, or name and address in standard format.
        :type email: string, optional
        :param name: Name for this sender or recipient.
        :type name: string, optional
        :param substitutions: String substitutions to be applied to the email.
        :type substitutions: list(Substitution), optional
        :param subject: Subject for this sender or recipient.
        :type subject: string, optional
        :param p: p is the Personalization object or Personalization object
                  index
        :type p: Personalization, integer, optional
        :param dynamic_template_data: Data for a dynamic transactional template.
        :type dynamic_template_data: DynamicTemplateData, optional
        """
        self._name = None
        self._email = None
        self._personalization = p

        if email and not name:
            # allows passing emails as "Example Name <example@example.com>"
            self.parse_email(email)
        else:
            # allows backwards compatibility for Email(email, name)
            if email is not None:
                self.email = email

            if name is not None:
                self.name = name

        # Note that these only apply to To Emails (see Personalization.add_to)
        # and should be moved but have not been for compatibility.
        self._substitutions = substitutions
        self._dynamic_template_data = dynamic_template_data
        self._subject = subject

    @property
    def name(self):
        """Name associated with this email.

        :rtype: string
        """
        return self._name

    @name.setter
    def name(self, value):
        """Name associated with this email.

        :param value: Name associated with this email.
        :type value: string
        """
        if not (value is None or isinstance(value, basestring)):
            raise TypeError('name must be of type string.')

        self._name = value

    @property
    def email(self):
        """Email address.

        See http://tools.ietf.org/html/rfc3696#section-3 and its errata
        http://www.rfc-editor.org/errata_search.php?rfc=3696 for information
        on valid email addresses.

        :rtype: string
        """
        return self._email

    @email.setter
    def email(self, value):
        """Email address.

        See http://tools.ietf.org/html/rfc3696#section-3 and its errata
        http://www.rfc-editor.org/errata_search.php?rfc=3696 for information
        on valid email addresses.

        :param value: Email address.
        See http://tools.ietf.org/html/rfc3696#section-3 and its errata
        http://www.rfc-editor.org/errata_search.php?rfc=3696 for information
        on valid email addresses.
        :type value: string
        """
        self._email = value

    @property
    def substitutions(self):
        """A list of Substitution objects. These substitutions will apply to
           the text and html content of the body of your email, in addition
           to the subject and reply-to parameters. The total collective size
           of your substitutions may not exceed 10,000 bytes per
           personalization object.

        :rtype: list(Substitution)
        """
        return self._substitutions

    @substitutions.setter
    def substitutions(self, value):
        """A list of Substitution objects. These substitutions will apply to
        the text and html content of the body of your email, in addition to
        the subject and reply-to parameters. The total collective size of
        your substitutions may not exceed 10,000 bytes per personalization
        object.

        :param value: A list of Substitution objects. These substitutions will
        apply to the text and html content of the body of your email, in
        addition to the subject and reply-to parameters. The total collective
        size of your substitutions may not exceed 10,000 bytes per
        personalization object.
        :type value: list(Substitution)
        """
        self._substitutions = value

    @property
    def dynamic_template_data(self):
        """Data for a dynamic transactional template.

        :rtype: DynamicTemplateData
        """
        return self._dynamic_template_data

    @dynamic_template_data.setter
    def dynamic_template_data(self, value):
        """Data for a dynamic transactional template.

        :param value: DynamicTemplateData
        :type value: DynamicTemplateData
        """
        self._dynamic_template_data = value

    @property
    def subject(self):
        """Subject for this sender or recipient.

        :rtype: string
        """
        return self._subject

    @subject.setter
    def subject(self, value):
        """Subject for this sender or recipient.

        :param value: Subject for this sender or recipient.
        :type value: string, optional
        """
        self._subject = value

    @property
    def personalization(self):
        """The Personalization object or Personalization object index

        :rtype: Personalization, integer
        """
        return self._personalization

    @personalization.setter
    def personalization(self, value):
        """The Personalization object or Personalization object index

        :param value: The Personalization object or Personalization object
                      index
        :type value: Personalization, integer
        """
        self._personalization = value

    def parse_email(self, email_info):
        """Allows passing emails as "Example Name <example@example.com>"

        :param email_info: Allows passing emails as
                           "Example Name <example@example.com>"
        :type email_info: string
        """
        name, email = rfc822.parseaddr(email_info)

        # more than likely a string was passed here instead of an email address
        if "@" not in email:
            name = email
            email = None

        if not name:
            name = None

        if not email:
            email = None

        self.name = name
        self.email = email
        return name, email

    def get(self):
        """
        Get a JSON-ready representation of this Email.

        :returns: This Email, ready for use in a request body.
        :rtype: dict
        """
        email = {}
        if self.name is not None:
            email["name"] = self.name

        if self.email is not None:
            email["email"] = self.email
        return email
