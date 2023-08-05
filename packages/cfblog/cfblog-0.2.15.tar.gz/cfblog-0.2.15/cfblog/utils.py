# coding=utf-8
from __future__ import (
    absolute_import, division, print_function, unicode_literals,
)

import re
from functools import wraps

from django.conf import settings
from django.core import urlresolvers
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.template import Template, TemplateSyntaxError
from django.template.base import tag_re as django_tag_re
from django.template.context import make_context
from django.test.client import Client
from django.utils import six
from django.utils.decorators import available_attrs
from django.utils.functional import SimpleLazyObject

from bs4 import BeautifulSoup
from mistune import markdown

from .validators import ValidationError, validate_and_get_template

# we are initialising Client as global variable
# so that we need to load the middlewares only once
_dum_client = Client()


# noinspection PyTypeChecker,PyProtectedMember
@SimpleLazyObject
def dum_request():
    """
    Returns WSGIRequest object that is ready to be passed into a view
    """
    request_handler = _dum_client.handler
    environ = _dum_client._base_environ()

    request = WSGIRequest(environ)
    if request_handler._request_middleware is None:
        request_handler.load_middleware()

    urlconf = settings.ROOT_URLCONF
    urlresolvers.set_urlconf(urlconf)
    resolver = urlresolvers.RegexURLResolver(r'^/', urlconf)
    try:
        response = None
        # Apply request middleware
        for middleware_method in request_handler._request_middleware:
            response = middleware_method(request)
            if response:
                break

        if response is None:
            if hasattr(request, 'urlconf'):
                # Reset url resolver with a custom urlconf.
                urlconf = request.urlconf
                urlresolvers.set_urlconf(urlconf)
                resolver = urlresolvers.RegexURLResolver(r'^/', urlconf)

            resolver_match = resolver.resolve(request.path_info)
            callback, callback_args, callback_kwargs = resolver_match
            request.resolver_match = resolver_match

            # Apply view middleware
            for middleware_method in request_handler._view_middleware:
                response = middleware_method(
                    request, callback, callback_args, callback_kwargs
                )
                if response:
                    break
    except:
        pass
    finally:
        return request


ATTR_TAG = 'data-cms-attr'
INCLUDE_TAG = 'data-cms-include'
CONTENT_TAG = 'data-cms-content'
NAMESPACE_TAG = 'data-cms-namespace'
REPLACE_TAG = 'data-cms-replace'

CMS_ATTRIBUTES = [ATTR_TAG, CONTENT_TAG, INCLUDE_TAG]

attr_re = re.compile(
    r'^(?:(?:[a-z-]+:[a-z_0-9]+)+(?:\|(?:[a-z-]+:[a-z_0-9]+))*)*$',
    re.IGNORECASE
)
content_re = re.compile(
    r'^(?:md:)?([a-z_0-9])+$',
    re.IGNORECASE
)
include_html_re = re.compile(
    r'^(?:(?:[a-z_0-9])+:)?.+$',
    re.IGNORECASE
)
namespace_re = re.compile(
    r'^(?:[a-z_0-9])+$',
    re.IGNORECASE
)

NAMESPACE_DELIMITER = '-'

# only 'html.parser' doesn't bother adding <html> tag for html components
HTML_PARSER = 'html.parser'


def parse_cms_template(html, cms_context, parent_namespace='', public=False,
                       request=dum_request, template_context=None, using=None):
    """
    Refer to tests for cms syntax

    :param html: Html to be parsed using cms syntax
    :type html: str|unicode
    :param cms_context: Dictionary that is to be used to parse the
    cms attributes in template
    :type cms_context: dict
    :param parent_namespace: Namespace of the html content to be parsed (if any)
    :type parent_namespace: str
    :param public: Renders the page for public usage
    :type public: bool
    :param request: Request object to be used for template context
    :param template_context: Template context to be used for rendering the
    base and included templates
    :type template_context: dict
    :param using: Template engine used to render the final template
    :rtype : str
    """
    soup = BeautifulSoup(html, features=HTML_PARSER)

    for tag in soup.find_all(attrs={INCLUDE_TAG: include_html_re}):
        namespace = get_namespace(tag, parent_namespace=parent_namespace)
        include_value = tag.attrs.pop(INCLUDE_TAG)
        if ':' in include_value:
            local_namespace, default_template_name = include_value.split(':', 1)
        else:
            try:
                local_namespace = tag.attrs[NAMESPACE_TAG]
            except KeyError:
                raise TemplateSyntaxError(
                    'value of data-cms-include should be of the form '
                    '{namespace}:{template path}.'
                    'if namespace is not specified then another attribute '
                    'data-cms-namespace should be defined'
                )
            else:
                if not namespace_re.match(local_namespace):
                    raise TemplateSyntaxError(
                        '"{}" is not a valid value for {}'.format(
                            local_namespace, NAMESPACE_TAG
                        )
                    )
                else:
                    default_template_name = include_value

        if namespace:
            namespace += NAMESPACE_DELIMITER + local_namespace
        else:
            namespace = local_namespace

        template_name = cms_context.get(namespace, default_template_name)

        if template_name.endswith('.html'):
            template_name = template_name[:-5]

        try:
            include_template = validate_and_get_template(
                name=template_name, using=using
            )
        except ValidationError:
            include_template = validate_and_get_template(
                name=default_template_name, using=using
            )

        include_html = include_template.render(template_context, request)

        tag.attrs[NAMESPACE_TAG] = local_namespace
        if not public:
            tag.attrs[INCLUDE_TAG] = template_name

        replace_tag_content(tag=tag, content=include_html)

    for tag in soup.find_all(attrs={ATTR_TAG: attr_re}):
        _ns = get_namespace(tag, parent_namespace=parent_namespace)
        attrs = tag[ATTR_TAG].split('|')

        for attr in attrs:
            attr_name, key = attr.split(':', 1)
            key = _ns + NAMESPACE_DELIMITER + key if _ns else key

            if key in cms_context:
                tag[attr_name] = render_template_string(
                    template_string=cms_context[key],
                    context=template_context,
                    request=request, using=using
                )

    for tag in soup.find_all(attrs={CONTENT_TAG: content_re}):
        _ns = get_namespace(tag, parent_namespace=parent_namespace)
        key = tag[CONTENT_TAG]
        md = False

        if key.startswith('md:'):
            key = key[3:]
            md = True

        key = _ns + NAMESPACE_DELIMITER + key if _ns else key

        if key in cms_context or REPLACE_TAG in tag.attrs:
            # REPLACE_TAG will be replaced with it's content.
            # So, it doesn't make much sense to process it in else loop
            content = cms_context.get(key, '')
        else:
            content = tag.decode_contents()
            if not any(attr in content for attr in CMS_ATTRIBUTES):
                continue

        if any(attr in content for attr in CMS_ATTRIBUTES):
            content = parse_cms_template(
                html=content, cms_context=cms_context, parent_namespace=key,
                request=request, template_context=template_context, using=using
            )

        if md:
            content = markdown(content, escape=False)

        content = render_template_string(
            template_string=content,
            context=template_context,
            request=request, using=using
        )

        if public and REPLACE_TAG in tag.attrs:
            new_tag = BeautifulSoup(content, features=HTML_PARSER)
            tag.replace_with(new_tag)
        else:
            # We don't replace the tag in auth render so as to keep it editable
            replace_tag_content(tag=tag, content=content)

    # don't use soup.prettify as it will insert empty spaces inside textarea
    return soup.decode_contents()


def replace_tag_content(tag, content):
    tag.clear()

    if isinstance(content, six.string_types):
        # Don't even bother
        if not content:
            return tag
        content = BeautifulSoup(content, features=HTML_PARSER)

    tag.append(content)
    if content.contents:
        # Not sure why .append doesn't do this by default
        tag.next_element = content.contents[0]
    return tag


def get_namespace(tag, parent_namespace=''):
    ancestor_namespaces = [
        parent.attrs.get(NAMESPACE_TAG) or parent.attrs.get(CONTENT_TAG)
        for parent in tag.find_parents(is_namespace_parent)
    ]

    if parent_namespace:
        ancestor_namespaces.append(parent_namespace)

    return NAMESPACE_DELIMITER.join(reversed(ancestor_namespaces))


def is_namespace_parent(tag):
    attrs = tag.attrs
    if namespace_re.match(attrs.get(NAMESPACE_TAG, '')):
        return True

    if content_re.match(attrs.get(CONTENT_TAG, '')):
        return True

    return False


def render_template_string(template_string, context=None,
                           request=None, using=None):
    if django_tag_re.findall(template_string):
        return Template(
            template_string=template_string, engine=using
        ).render(context=make_context(context=context, request=request))

    return template_string


def can_edit_content(user):
    return any(
        user.has_perm(perm)
        for perm in ('cfblog.change_content', 'cfblog.can_publish')
    )


def can_publish_content(user):
    return user.has_perm('cfblog.can_publish')


def user_passes_test(test_func=None):
    """
    Similar to user_passes_test in django.contrib.auth.decorators.
    Instead of redirecting it just raises PermissionDenied.

    :param test_func: Should take a User object and return a bool
    :type test_func: function
    """
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return _wrapped_view
    return decorator
