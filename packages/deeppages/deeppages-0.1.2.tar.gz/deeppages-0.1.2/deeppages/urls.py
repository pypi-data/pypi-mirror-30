from django.conf.urls import url

from .views import PageView


urlpatterns = [
    url('', PageView.as_view(), name='__deep_page_view__'),
]
