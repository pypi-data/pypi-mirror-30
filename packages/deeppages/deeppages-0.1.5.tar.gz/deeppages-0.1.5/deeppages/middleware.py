from django.utils.deprecation import MiddlewareMixin
from django.http.response import HttpResponse

from .utils import get_page_by_path

import logging

logger = logging.getLogger(__name__)


class DeepPageTemplateRendererMiddleware(MiddlewareMixin):
    '''
        The goal of this middleware is find the respective page by URL, render
        the page content and return it.
    '''

    def process_request(self, request):
        '''
            Look for Deep Page's PATH pattern and return a rendered template
        '''
        rendered_page = get_page_by_path(self, request, logger)
        if not rendered_page:
            return

        return HttpResponse(rendered_page)
