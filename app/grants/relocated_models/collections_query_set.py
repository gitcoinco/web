class CollectionsQuerySet(models.QuerySet):
    """Handle the manager queryset for Collections."""

    def visible(self):
        """Filter results down to visible collections only."""
        return self.filter(hidden=False)

    def keyword(self, keyword):
        if not keyword:
            return self
        return self.filter(
            Q(description__icontains=keyword) |
            Q(title__icontains=keyword) |
            Q(profile__handle__icontains=keyword)
        )