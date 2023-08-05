# coding=utf-8
from __future__ import (
    absolute_import, division, print_function, unicode_literals,
)

from django.contrib import admin

from .models import Category, Content


@admin.register(Category)
class CmsPageCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('url', 'title', 'publish', 'status', 'link')
    list_filter = ('publish', 'category', 'status', 'author')
    search_fields = ('title', 'url', 'template')
    readonly_fields = ('created_on', 'modified_on')

    def link(self, obj):
        return "<a target='_blank' href='{}'>View on site</a>".format(
            obj.get_absolute_url()
        )
    link.allow_tags = True
