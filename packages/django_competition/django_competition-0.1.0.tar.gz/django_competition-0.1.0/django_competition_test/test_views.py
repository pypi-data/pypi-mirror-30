# coding=utf-8

import re
from urllib.parse import urlparse, parse_qs, ParseResult, urlencode

import pytest
from django.test import Client
from django.urls import reverse

from django.core import mail

from django_competition.models import VoteGroup
from django_competition.services import VoteService


@pytest.fixture()
def vote_url(competition):
  return reverse("competition:vote", kwargs={"pk": competition.pk})


@pytest.fixture()
def valid_vote_response(
    valid_competition_form_data,
    vote_url,
    client,
):
  return client.post(vote_url, valid_competition_form_data)


@pytest.mark.django_db()
def test_vote_view_get(
    competition,
    client,
    vote_url,
):
  response = client.get(vote_url)
  body = response.content.decode('utf-8')
  assert competition.name in body
  for entry in competition.entries.all():
    assert entry.name in body


@pytest.mark.django_db()
def test_vote_view_post_single_vote(valid_vote_response):
  response = valid_vote_response
  assert response.status_code == 302
  assert response.url == reverse("competition:done")


@pytest.mark.django_db()
def test_after_vote_posted_email_is_sent(valid_vote_response):
  assert len(mail.outbox) == 1
  message_body = mail.outbox[0].body
  url_regex = re.compile(r"To confirm the vote go to the following page:\s*(.*)\s*\.\s*")
  match = re.findall(url_regex, message_body)
  assert len(match) == 1
  confirm_url = urlparse(match[0])
  query_args = parse_qs(confirm_url.query)

  service = VoteService()
  # This validates vote --- which means vote would be stored.
  service.query_args_to_vote({k: v[0] for k,v in query_args.items()})


@pytest.mark.django_db()
def test_invalid_vote_view(
    client: Client,
    vote_url,
    invalid_competition_form_data
):
  data, __ = invalid_competition_form_data
  response = client.post(vote_url, data=data)
  # If form is invalid it is displayed again
  assert response.status_code == 200
  assert VoteGroup.objects.count() == 0


@pytest.fixture()
def valid_confirmation_url(
    vote,
):
  service = VoteService()
  query_args = service.vote_to_signed_query_args(vote)
  return reverse("competition:confirm") + "?" + urlencode(query_args)


@pytest.mark.django_db()
def test_valid_vote_confirmation_get(client: Client, valid_confirmation_url):
  response = client.get(valid_confirmation_url)
  assert response.status_code == 200
  assert "I confirm this vote" in response.content.decode('utf-8')
  # Still no vote recorded
  assert VoteGroup.objects.count() == 0


@pytest.mark.django_db()
def test_valid_vote_confirmation_post(client: Client, valid_confirmation_url):
  response = client.post(path=valid_confirmation_url, data = {})
  assert response.status_code == 302
  # Still no vote recorded
  assert VoteGroup.objects.count() == 1



