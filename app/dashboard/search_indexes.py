from haystack import indexes

from .models import Bounty, HackathonProject, Profile

class BountyIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    title = indexes.CharField(model_attr='title')

    def get_model(self):
        return Bounty

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

class HackathonProjectIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    name = indexes.CharField(model_attr='name')
    summary = indexes.CharField(model_attr='summary')

    def get_model(self):
        return HackathonProject

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

class ProfileIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    # data = indexes.CharField(model_attr='to_es')
    # user = indexes.IntegerField(model_attr='user__id')
    # handle = indexes.CharField(model_attr='handle')
    # first_name = indexes.CharField(model_attr='user__first_name')
    # last_name = indexes.CharField(model_attr='user__last_name')
    # rank_coder = indexes.IntegerField(model_attr='rank_coder', faceted=True)
    # rank_funder = indexes.IntegerField(model_attr='rank_funder', faceted=True)
    # sms_verification = indexes.BooleanField(model_attr='sms_verification', faceted=True)
    # num_hacks_joined = indexes.IntegerField(model_attr='', faceted=True)
    # github_created_at = indexes.DateField(model_attr='github_created_on')
    # join_date = indexes.DateField(model_attr='created_on')

    # We add this for autocomplete.
    handle_auto = indexes.EdgeNgramField(model_attr='handle')
    first_name_auto = indexes.EdgeNgramField(model_attr='user__first_name')
    last_name_auto = indexes.EdgeNgramField(model_attr='user__last_name')


    def prepare(self, obj):
        data = super(ProfileIndex, self).prepare(obj)
        merged = { **data, **obj.to_dict() }
        return merged

    def get_model(self):
        return Profile

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.prefetch_related('user').filter(hide_profile=False)
