import errno
import logging
import os
import socket
from collections import namedtuple
from httplib import BadStatusLine

from django.conf.urls import url
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt as csrf_exempt_decorator
from django.views.defaults import page_not_found
from docker.errors import NotFound
from httpproxy.views import HttpProxy

from container_managers.docker_engine import DockerEngineManagerError
from django_docker_engine.historian import NullHistorian
from docker_utils import DockerClientWrapper

try:
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import HTTPError

try:
    from django.views import View
except ImportError:  # Support Django 1.7
    from django.views.generic import View

try:
    from django.template.backends.django import DjangoTemplates
except ImportError:  # Support Django 1.7
    from django.template import Context, Template

logging.basicConfig()
logger = logging.getLogger(__name__)

UrlPatterns = namedtuple('UrlPatterns', ['urlpatterns'])


class Proxy():
    def __init__(self,
                 historian=NullHistorian(),
                 please_wait_title='Please wait',
                 please_wait_body_html='<h1>Please wait</h1>',
                 csrf_exempt=True):
        self.historian = historian
        self.csrf_exempt = csrf_exempt
        self.content = self._render({
            'title': please_wait_title,
            'body_html': please_wait_body_html
        })

    def _render(self, context):
        template_path = os.path.join(
            os.path.dirname(__file__), 'please-wait.html')
        template_code = open(template_path).read()

        # Normally, we would use template loaders, but could there be
        # interactions between the configs necessary here and in the parent app?
        try:  # 1.11
            engine = DjangoTemplates({
                'OPTIONS': {}, 'NAME': None, 'DIRS': [], 'APP_DIRS': []
            })
            # All the keys are required, but the values don't seem to matter.
            template = engine.from_string(template_code)
        except NameError:  # 1.7
            template = Template(template_code)
            context = Context(context)

        return template.render(context)

    def url_patterns(self):
        return [
            url(
                r'^(?P<container_name>[^/]*)/(?P<url>.*)$',
                csrf_exempt_decorator(self._proxy_view) if self.csrf_exempt
                else self._proxy_view
            )
        ]

    def _proxy_view(self, request, container_name, url):
        self.historian.record(container_name, url)
        try:
            client = DockerClientWrapper()
            container_url = client.lookup_container_url(container_name)
            view = HttpProxy.as_view(base_url=container_url)
            return view(request, url=url)
        except (DockerEngineManagerError, NotFound, BadStatusLine) as e:
            # TODO: Should DockerEngineManagerError be sufficient by itself?
            logger.info(
                'Normal transient error. '
                'Container: %s, Exception: %s', container_name, e)
            view = self._please_wait_view_factory().as_view()
            return view(request)
        except socket.error as e:
            if e.errno != errno.ECONNRESET:
                raise
            logger.info(
                'Container not yet listening. '
                'Container: %s, Exception: %s', container_name, e)
            view = self._please_wait_view_factory().as_view()
            return view(request)
        except HTTPError as e:
            logger.warn(e)
            return page_not_found(request, e)
            # The underlying error is not necessarily a 404,
            # but this seems ok.

    def _please_wait_view_factory(self):
        class PleaseWaitView(View):
            def get(inner_self, request, *args, **kwargs):  # noqa: N805
                response = HttpResponse(self.content)
                response.status_code = 503
                response.reason_phrase = 'Container not yet available'
                # Non-standard, but more clear than default;
                # Also, before 1.9, this is not set just by changing status code.
                return response
            http_method_named = ['get']
        return PleaseWaitView
