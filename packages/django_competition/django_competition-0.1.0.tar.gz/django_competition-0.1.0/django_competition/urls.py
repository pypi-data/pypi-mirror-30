# coding=utf-8

from django.conf.urls import url


from . import views


urlpatterns = [
    url('^done/?$', views.VoteSaved.as_view(), name='done'),
    url('^confirm/?$', views.ConfirmVote.as_view(), name='confirm'),
    url(
      'vote/(?P<pk>[\-\d]+)/?$', views.CompetitionVote.as_view(), name='vote'
    )
]
