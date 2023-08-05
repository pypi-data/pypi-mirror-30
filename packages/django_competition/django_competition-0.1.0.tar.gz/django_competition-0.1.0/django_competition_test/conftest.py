# coding=utf-8

import base64

import pytest
from django.views.generic import base

from django_competition import models, services
from django_competition.services import InvalidVoteException, UserInvalidVoteException


@pytest.fixture()
def competition():
  competition = models.Competition.objects.create(
    id=-1,
    name="Test",
    description="Test",
    votes_per_day=1,
    entries_per_vote=3,
    allow_disposable_emails=False,
    competition_encryption_key=64 * b'\x01'
  )

  for entry_id in range(4):
    models.CompetitionEntry.objects.create(
      id=-(1 + entry_id),
      competition=competition,
      name="Entry {}".format(entry_id),
      description=""
    )

  return competition

@pytest.fixture()
def other_competition():
  competition = models.Competition.objects.create(
    name="Test",
    description="Test",
    votes_per_day=1,
    entries_per_vote=3,
    allow_disposable_emails=False,
    competition_encryption_key=64 * b'\x01'
  )

  for entry_id in range(4):
    models.CompetitionEntry.objects.create(
      competition=competition,
      name="Entry {}".format(entry_id),
      description=""
    )
  return competition


@pytest.fixture()
def other_entry(other_competition):
  return other_competition.entries.first()

@pytest.fixture()
def service():
  return services.VoteService()


@pytest.fixture()
def vote(competition):
  return services.CompetitionVote(
    competition,
    entries=list(competition.entries.all().order_by('pk'))[2:],
    nonce=b'1234',
    source_email='none@no-such-email-provider.pl'
  )


@pytest.fixture()
def serialized_vote():
  return b"competition=-1&nonce=1234" \
         b"&source_email=none%40no-such-email-provider.pl&" \
         b"entry=-1&entry=-2"


@pytest.fixture()
def vote_signature():
  return (
    b'\x17=\xe6\xfb\xe9\xc8\xe9:\xcd\xf9\x88\xad\xfe@\x86\x10\xa6h\xd4\xdd'
    b'\xa4"0\xcb}\xc0\x9b\x85\xbc)\xb8\x95'
  )


@pytest.fixture()
def valid_competition_form_data():
  return {
    "choice_0": -1,
    "your_email": "user@gmail.com",
    "store_e_mail_consent": "on",
    "terms_and_condition_consents": "on",
  }


INVALID_COMPETITION_FORM_DATA = [
  # No email
  [
    {'choice_0': '-1', "store_e_mail_consent": "on", "terms_and_condition_consents": "on"},
    {"your_email"}
  ],
  # Invalid e-mail format
  [
    {'choice_0': '-1', "your_email": "Invalid email", "store_e_mail_consent": "on", "terms_and_condition_consents": "on", },
    {"your_email"}
  ],
  # Blocked e-mail domain
  [
    {'choice_0': '-1', "your_email": "jacek@niepodam.pl", "store_e_mail_consent": "on", "terms_and_condition_consents": "on", },
    {"__all__"}
  ],
  # No choice
  [
    {"your_email": "someone@no-such-domain.pl", "store_e_mail_consent": "on", "terms_and_condition_consents": "on", },
    {"choice_0"}
  ],
  # No consent
  [
    {'choice_0': '-1', "your_email": "someone@no-such-domain.pl", "terms_and_condition_consents": "on", },
    {"store_e_mail_consent"}
  ],
  # No consent
  [
    {'choice_0': '-1', "your_email": "someone@no-such-domain.pl", "store_e_mail_consent": "on", },
    {"terms_and_condition_consents"}
  ],
  # Repeated choices
  [
    {
      'choice_0': '-1',
      'choice_1': '-1',
      "your_email": "jacek@niepodam.pl",
      "store_e_mail_consent": "on",
      "terms_and_condition_consents": "on"
    },
    {"__all__"}
  ]
]


@pytest.fixture(params=INVALID_COMPETITION_FORM_DATA)
def invalid_competition_form_data(request):
  """
  Returns tuple form_data, broken_fields,
  where form_data a dictionary of form field values and
  broken fields is a set of fields that have errors.
  """
  return request.param
