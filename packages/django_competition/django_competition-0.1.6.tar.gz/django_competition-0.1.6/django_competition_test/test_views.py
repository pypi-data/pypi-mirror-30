# coding=utf-8
"""Tests for views."""
import re
from urllib.parse import urlparse, parse_qs, urlencode

import pytest
from django.core import mail
from django.test import Client
from django.urls import reverse

from django_competition.models import VoteGroup
from django_competition.services import VoteService


# pylint: disable=redefined-outer-name,invalid-name,no-member,unused-argument


@pytest.fixture()
def vote_url(competition):
  """Returns url for page that allows voting on a competition."""
  return reverse("competition:vote", kwargs={"pk": competition.pk})


@pytest.fixture()
def valid_vote_response(
    valid_competition_form_data,
    vote_url,
    client,
):
  """HTTPS response to valid vote POST."""
  return client.post(vote_url, valid_competition_form_data)


@pytest.mark.django_db()
def test_vote_view_get(
    competition,
    client,
    vote_url,
):
  """Basic sanity checks in HTML response for voting view."""
  response = client.get(vote_url)
  body = response.content.decode('utf-8')
  assert competition.name in body
  for entry in competition.entries.all():
    assert entry.name in body


@pytest.mark.django_db()
def test_vote_view_post_single_vote(valid_vote_response):
  """Checks that post to vote pages is a redirect."""
  response = valid_vote_response
  assert response.status_code == 302
  assert response.url == reverse("competition:done")


@pytest.mark.django_db()
def test_after_vote_posted_email_is_sent(valid_vote_response):
  """Checks that post to vote pages results in an e-mail sent."""
  assert len(mail.outbox) == 1
  message_body = mail.outbox[0].body
  url_regex = re.compile(r"To confirm the vote go to the following page:\s*(.*)\s*\.\s*")
  match = re.findall(url_regex, message_body)
  assert len(match) == 1
  confirm_url = urlparse(match[0])
  query_args = parse_qs(confirm_url.query)

  service = VoteService()
  # This validates vote --- which means vote would be stored.
  service.query_args_to_vote({k: v[0] for k, v in query_args.items()})


@pytest.mark.django_db()
def test_invalid_vote_view(
    client: Client,
    vote_url,
    invalid_competition_form_data
):
  """Suite of tests for invalid votes."""
  data, __ = invalid_competition_form_data
  response = client.post(vote_url, data=data)
  # If form is invalid it is displayed again
  assert response.status_code == 200
  assert VoteGroup.objects.count() == 0


@pytest.fixture()
def valid_confirmation_url(
    vote,
):
  """Returns confirmation url for a vote."""
  service = VoteService()
  query_args = service.vote_to_signed_query_args(vote)
  return reverse("competition:confirm") + "?" + urlencode(query_args)


@pytest.mark.django_db()
def test_valid_vote_confirmation_get(
    client: Client,
    valid_confirmation_url,
    vote
):
  """Test for user entering a confirmation page. (No vote recorded)"""
  response = client.get(valid_confirmation_url)
  assert response.status_code == 200
  response_contents = response.content.decode('utf-8')
  assert "I confirm this vote" in response_contents
  assert vote.competition.name in response_contents
  for entry in vote.entries:
    assert entry.name in response_contents
  # Still no vote recorded
  assert VoteGroup.objects.count() == 0


@pytest.mark.django_db()
def test_valid_vote_confirmation_post(client: Client, valid_confirmation_url):
  """Tests POST on confirmation page confirms a vote."""
  response = client.post(path=valid_confirmation_url, data={})
  assert response.status_code == 302
  # Vote recorded
  assert VoteGroup.objects.count() == 1


@pytest.mark.django_db()
def test_invalid_vote_confirm(competition, client: Client, valid_confirmation_url):
  """Tests POST on confirmation page confirms a vote."""
  competition.voting_open = False
  competition.save()
  response = client.post(path=valid_confirmation_url, data={})
  assert response.status_code == 200
  assert "You can't confirm this vote right now" in response.content.decode('utf-8')
  assert VoteGroup.objects.count() == 0


@pytest.mark.django_db()
def test_malformed_vote_confirm(competition, client: Client):
  """Tests POST on confirmation page confirms a vote."""
  competition.voting_open = False
  competition.save()
  #                           No vote parameters so invalid vote
  response = client.post(path=reverse("competition:confirm"), data={})
  assert response.status_code == 400


