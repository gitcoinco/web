class GrantQuerySet(models.QuerySet):
    """Define the Grant default queryset and manager."""

    def active(self):
        """Filter results down to active grants only."""
        return self.filter(active=True)

    def inactive(self):
        """Filter results down to inactive grants only."""
        return self.filter(active=False)

    def keyword(self, keyword):
        """Filter results to all Grant objects containing the keywords.

        Args:
            keyword (str): The keyword to search title, description, and reference URL by.

        Returns:
            dashboard.models.GrantQuerySet: The QuerySet of grants filtered by keyword.

        """
        if not keyword:
            return self
        return self.filter(
            Q(description__icontains=keyword) |
            Q(title__icontains=keyword) |
            Q(reference_url__icontains=keyword)
        )