class GrantType(SuperModel):

    name = models.CharField(unique=True, max_length=15, help_text="Grant Type")
    label = models.CharField(max_length=25, null=True, help_text="Display Name")
    is_active = models.BooleanField(default=True, db_index=True, help_text="Is Grant Type currently active")
    is_visible = models.BooleanField(default=True, db_index=True, help_text="Is visible on the Grant filters")
    categories = models.ManyToManyField(
        GrantCategory,
        help_text="Grant Categories associated with Grant Type"
    )
    logo = models.ImageField(
        upload_to=get_upload_filename,
        null=True,
        blank=True,
        max_length=500,
        help_text=_('The default category\'s marketing banner (aspect ratio = 10:3)'),
    )


    def __str__(self):
        """Return the string representation."""
        return f"{self.name}"

    @property
    def clrs(self):
        return GrantCLR.objects.filter(grant_filters__grant_type=str(self.pk))

    @property
    def active_clrs(self):
        return GrantCLR.objects.filter(is_active=True, grant_filters__grant_type=str(self.pk))

    @property
    def active_clrs_sum(self):
        return sum(self.active_clrs.values_list('total_pot', flat=True))