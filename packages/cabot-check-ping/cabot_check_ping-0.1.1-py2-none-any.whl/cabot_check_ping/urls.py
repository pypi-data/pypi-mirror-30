from django.conf.urls import url

from .views import (PingCheckCreateView, PingCheckUpdateView,
                    duplicate_check)

urlpatterns = [

    url(r'^pingcheck/create/',
        view=PingCheckCreateView.as_view(),
        name='create-ping-check'),

    url(r'^pingcheck/update/(?P<pk>\d+)/',
        view=PingCheckUpdateView.as_view(),
        name='update-ping-check'),

    url(r'^pingcheck/duplicate/(?P<pk>\d+)/',
        view=duplicate_check,
        name='duplicate-ping-check')

]
