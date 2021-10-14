import traceback
from io import BytesIO

from django.contrib.postgres.fields import JSONField
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models import Q
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

from economy.models import SuperModel
from grants.utils import generate_collection_thumbnail, get_upload_filename


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


class GrantCollection(SuperModel):
    grants = models.ManyToManyField(blank=True, to='Grant', help_text=_('References to grants related to this collection'))
    profile = models.ForeignKey('dashboard.Profile', help_text=_('Owner of the collection'), related_name='curator', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, help_text=_('Name of the collection'))
    description = models.TextField(default='', blank=True, help_text=_('The description of the collection'))
    cover = models.ImageField(upload_to=get_upload_filename, null=True,blank=True, max_length=500, help_text=_('Collection image'))
    hidden = models.BooleanField(default=False, help_text=_('Hide the collection'), db_index=True)
    cache = JSONField(default=dict, blank=True, help_text=_('Easy access to grant info'),)
    featured = models.BooleanField(default=False, help_text=_('Show grant as featured'))
    objects = CollectionsQuerySet.as_manager()
    shuffle_rank = models.PositiveIntegerField(default=1, db_index=True)
    curators = models.ManyToManyField(blank=True, to='dashboard.Profile', help_text=_('List of allowed curators'))

    def generate_cache(self):
        grants = self.grants.all()

        cache = {
            'count': grants.count(),
            'grants': [{
                'id': grant.id,
                'title': grant.title,
                'logo': grant.logo.url if grant.logo and grant.logo.url else static(f'v2/images/grants/logos/{grant.id % 3}.png'),
            } for grant in grants]
        }

        try:
            cover = generate_collection_thumbnail(self, 348 * 5, 175 * 5)
            filename = f'thumbnail_{self.id}.png'
            buffer = BytesIO()
            cover.save(fp=buffer, format='PNG')
            tempfile = ContentFile(buffer.getvalue())
            image_file = InMemoryUploadedFile(tempfile, None, filename, 'image/png', tempfile.tell, None)
            self.cover.save(filename, image_file)
        except Exception:
            print('ERROR: failed build thumbnail')
            traceback.print_exc()

        print(self.cover)
        self.cache = cache
        self.save()

    def to_json_dict(self, build_absolute_uri):
        curators = [{
            'url': curator.url,
            'handle': curator.handle,
            'avatar_url': curator.lazy_avatar_url
        } for curator in self.curators.all()]

        owner = {
            'url': self.profile.url,
            'handle': self.profile.handle,
            'avatar_url': self.profile.lazy_avatar_url
        }

        grants = self.cache.get('grants', 0)

        if grants:
            grants = [{
                **grant,
                'logo': build_absolute_uri(static(grant['logo'])) if 'v2/images' in grant['logo'] else grant['logo']
            } for grant in grants]
        return {
            'id': self.id,
            'owner': owner,
            'title': self.title,
            'description': self.description,
            'cover': self.cover.url if self.cover else '',
            'count': self.cache.get('count', 0),
            'grants': grants,
            'curators': curators + [owner]
        }
