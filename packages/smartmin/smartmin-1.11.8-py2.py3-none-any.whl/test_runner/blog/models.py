from __future__ import unicode_literals

import six
import uuid

from django.db import models
from django.utils.timezone import now
from smartmin.models import SmartModel, ActiveManager


@six.python_2_unicode_compatible
class Post(SmartModel):
    title = models.CharField(max_length=128,
                             help_text="The title of this blog post, keep it relevant")
    body = models.TextField(help_text="The body of the post, go crazy")
    order = models.IntegerField(help_text="The order for this post, posts with smaller orders come first")
    tags = models.CharField(max_length=128,
                            help_text="Any tags for this post")

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    written_on = models.DateField(default=now, null=True, blank=True)

    objects = models.Manager()
    active = ActiveManager()

    @classmethod
    def pre_create_instance(cls, field_dict):
        field_dict['body'] = "Body: %s" % field_dict['body']
        return field_dict

    @classmethod
    def prepare_fields(cls, field_dict, import_params=None, user=None):
        field_dict['order'] = int(float(field_dict['order']))
        return field_dict

    @classmethod
    def validate_import_header(cls, header):
        if 'title' not in header:
            raise Exception('missing "title" header')

    def __str__(self):
        return self.title


class Category(SmartModel):
    name = models.SlugField(max_length=64, unique=True,
                            help_text="The name of this category")
