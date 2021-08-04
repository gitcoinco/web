# class GrantStat(SuperModel):
#     SNAPSHOT_TYPES = [
#         ('total', 'total'),
#         ('increment', 'increment')
#     ]

#     grant = models.ForeignKey(Grant, on_delete=models.CASCADE, related_name='stats',
#                               help_text=_('Grant to add stats for this grant'))
#     data = JSONField(default=dict, blank=True, help_text=_('Stats for this Grant'))
#     snapshot_type = models.CharField(
#         max_length=50,
#         blank=False,
#         null=False,
#         help_text=_('Snapshot Type'),
#         db_index=True,
#         choices=SNAPSHOT_TYPES,
#     )

#     def __str__(self):
#         return f'{self.snapshot_type} {self.created_on} for {self.grant.title}'