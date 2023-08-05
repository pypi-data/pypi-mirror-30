#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from . import api_views


urlpatterns = [
    # materials module
    url(r'^api/material/$', api_views.MaterialsListView.as_view()),
    url(r'^api/material/(?P<pk>[0-9]+)/$', api_views.MaterialsDetailView.as_view()),
    url(r'^api/material-spec/$', api_views.MaterialsSpecificationListView.as_view()),
    url(r'^api/material-spec/(?P<pk>[0-9]+)/$', api_views.MaterialsSpecificationDetailView.as_view()),
    url(r'^api/material-entry/$', api_views.MaterialEntryListView.as_view()),
    url(r'^api/material-entry/(?P<pk>[0-9]+)/$', api_views.MaterialEntryDetailView.as_view()),
    url(r'^api/material-entry/statistics/$', api_views.MaterialStatisticsView.as_view()),




]
