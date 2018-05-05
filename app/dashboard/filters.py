from django_filters import BaseInFilter, BooleanFilter, CharFilter, Filter, FilterSet, MultipleChoiceFilter, UUIDFilter

from .models import Bounty


class CharInFilter(BaseInFilter, CharFilter):
    pass

class RawDataFilter(Filter):
    def filter(self, queryset, value):
        _queryset = queryset.none()
        for v in value.strip().split(','):
            if v.strip():
                _queryset = _queryset | queryset.filter(**{'raw_data__icontains': v.strip()})
                queryset = _queryset
        return queryset


class BountyFilter(FilterSet):
    raw_data = RawDataFilter()
    experience_level = MultipleChoiceFilter(
      field_name='experience_level',
      choices=Bounty.EXPERIENCE_LEVELS,
    )
    project_length = MultipleChoiceFilter(
      field_name='project_length',
      choices=Bounty.PROJECT_LENGTHS,
    )
    bounty_type = MultipleChoiceFilter(
      field_name='bounty_type',
      choices=Bounty.BOUNTY_TYPES
    )
    network = MultipleChoiceFilter(
      field_name='network',
      choices=(
        ('custom', 'custom'),
        ('ropsten', 'ropsten'),
        ('rinkeby', 'rinkeby'),
        ('mainnet', 'mainnet'),
      ),
    )
    pk = UUIDFilter(field_name='pk', lookup_expr=['gt'],)
    started = CharInFilter(field_name='interested__profile__handle',)
    github_url = CharInFilter()
    fulfiller_github_username = CharFilter(field_name='fulfillments__fulfiller_github_username',)
    interested_github_username = CharFilter(field_name='interested__profile__handle',)

    class Meta:
        model = Bounty
        fields = (
          'raw_data',
          'experience_level',
          'project_length',
          'bounty_type',
          'bounty_owner_address',
          'idx_status',
          'network',
          'bounty_owner_github_username',
          'standard_bounties_id',
          'pk',
          'started',
          'is_open',
          'github_url',
          'fulfiller_github_username',
          'interested_github_username'
        )
