# coding=utf-8
from __future__ import (
    absolute_import, division, print_function, unicode_literals,
)

from django.db.models import Manager, QuerySet
from django.utils import timezone


class ContentQuerySet(QuerySet):
    def by_author(self, user):
        return self.filter(author=user)

    def by_category(self, category):
        return self.filter(category=category)

    def published(self):
        return self.filter(
            status__gte=self.model.PUBLIC, publish__lte=timezone.now()
        )

    def static_pages(self):
        return self.filter(category__is_static=True)

    def blog_posts(self):
        return self.filter(category__is_static=False)


ContentManager = Manager.from_queryset(ContentQuerySet)
