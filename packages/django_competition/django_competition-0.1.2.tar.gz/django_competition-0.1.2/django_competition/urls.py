# coding=utf-8
"""Urls."""
from django.conf.urls import url

from . import views

urlpatterns = [
  url(r'^done/?$', views.VoteSaved.as_view(), name='done'),
  url(r'^confirm/?$', views.ConfirmVote.as_view(), name='confirm'),
  url(
    r'vote/(?P<pk>[\-\d]+)/?$', views.CompetitionVote.as_view(), name='vote'
  )
]
