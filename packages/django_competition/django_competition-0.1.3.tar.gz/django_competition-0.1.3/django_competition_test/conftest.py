# coding=utf-8
"""Shared fixtures."""

import pytest

from django_competition import models, services


# pylint: disable=redefined-outer-name


@pytest.fixture()
def competition():
  """
  Main competition used in tests.

  Uses negative primary keys, so other tests can assume *known* primary keys and
  we don't have to

  """
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
  """Second competition."""
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
def with_competition_votes(competition, other_competition):
  """Adds votes to competitions, each entry has abs(entry.pk) votes."""
  def __make_votes(competition):
    for entry in competition.entries.all():
      for _ in range(abs(entry.pk)):
        vote_group = models.VoteGroup.objects.create(
          competition=competition, vote_source="test@somewhere.org"
        )
        models.Vote.objects.create(
          group=vote_group, entry=entry
        )

  __make_votes(competition)
  __make_votes(other_competition)


@pytest.fixture()
def other_entry(other_competition):
  """Entry on other competition"""
  return other_competition.entries.first()


@pytest.fixture()
def service():
  """Vote service."""
  return services.VoteService()


@pytest.fixture()
def vote(competition):
  """Valid competition vote."""
  return services.CompetitionVote(
    competition,
    entries=list(competition.entries.all().order_by('pk'))[2:],
    nonce=b'1234',
    source_email='none@no-such-email-provider.pl'
  )


@pytest.fixture()
def serialized_vote():
  """Serialized version of ``vote``"""
  return b"competition=-1&nonce=1234" \
         b"&source_email=none%40no-such-email-provider.pl&" \
         b"entry=-1&entry=-2"


@pytest.fixture()
def vote_signature():
  """Valid signature for serialized_vote."""
  return (
    b'\x17=\xe6\xfb\xe9\xc8\xe9:\xcd\xf9\x88\xad\xfe@\x86\x10\xa6h\xd4\xdd'
    b'\xa4"0\xcb}\xc0\x9b\x85\xbc)\xb8\x95'
  )


@pytest.fixture()
def valid_competition_form_data():
  """Valid data for competition form."""
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
    {
      'choice_0': '-1', "your_email": "Invalid email",
      "store_e_mail_consent": "on", "terms_and_condition_consents": "on",
    },
    {"your_email"}
  ],
  # Blocked e-mail domain
  [
    {
      'choice_0': '-1', "your_email": "jacek@niepodam.pl",
      "store_e_mail_consent": "on", "terms_and_condition_consents": "on",
    },
    {"__all__"}
  ],
  # No choice
  [
    {
      "your_email": "someone@no-such-domain.pl", "store_e_mail_consent": "on",
      "terms_and_condition_consents": "on"
    },
    {"choice_0"}
  ],
  # No consent
  [
    {
      'choice_0': '-1', "your_email": "someone@no-such-domain.pl",
      "terms_and_condition_consents": "on",
    },
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
