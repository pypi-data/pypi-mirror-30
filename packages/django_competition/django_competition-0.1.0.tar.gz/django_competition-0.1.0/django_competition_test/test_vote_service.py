# coding=utf-8
import base64

import pytest
from django.views.generic import base

from django_competition import models, services
from django_competition.services import InvalidVoteException, UserInvalidVoteException


@pytest.mark.django_db
def test_serialize_vote(
    service: services.VoteService,
    vote,
    serialized_vote
):
  assert service.serialize_vote(vote) == serialized_vote


@pytest.mark.django_db
def test_deserialize_vote(
    service: services.VoteService,
    vote,
    serialized_vote
):
  assert service.deserialize_vote(serialized_vote) == vote

@pytest.mark.django_db
def test_vote_signature(
    service: services.VoteService,
    competition,
    serialized_vote,
    vote_signature
):
  assert service.sign_vote(competition, serialized_vote) == vote_signature


@pytest.mark.django_db
def test_vote_verify_positive(
  service: services.VoteService,
  competition,
  serialized_vote,
  vote_signature
):
  service.verify_vote_signature(competition, serialized_vote, vote_signature)


@pytest.mark.django_db
def test_vote_verify_negative(
  service: services.VoteService,
  competition,
  serialized_vote,
  vote_signature
):
  invalid_signature = b'\x01' * 32
  assert invalid_signature != vote_signature
  with pytest.raises(InvalidVoteException):
    service.verify_vote_signature(competition, serialized_vote, invalid_signature)


@pytest.mark.django_db
def test_vote_to_query(
  service: services.VoteService,
  competition,
  vote
):
  query = service.vote_to_signed_query_args(vote)
  recovered_vote = service.query_args_to_vote(query)
  assert vote == recovered_vote


@pytest.mark.django_db
def test_validate_invalid_vote(service: services.VoteService, vote):

  with pytest.raises(UserInvalidVoteException):
    service.validate_vote(vote._replace(
      source_email="Not a valid e-mail"
    ))




@pytest.mark.django_db
def test_validate_invalid_vote(service: services.VoteService, vote):

  with pytest.raises(UserInvalidVoteException):
    service.validate_vote(vote._replace(
      source_email="Not a valid e-mail"
    ))


@pytest.mark.django_db
def test_validate_disposable_email(service: services.VoteService, vote):

  with pytest.raises(UserInvalidVoteException):
    service.validate_vote(vote._replace(
      source_email="test@niepodam.pl"
    ))


@pytest.mark.django_db
def test_validate_entries(service: services.VoteService, vote):

  with pytest.raises(UserInvalidVoteException):
    service.validate_vote(vote._replace(
      entries=list(models.CompetitionEntry.objects.all())
    ))


@pytest.mark.django_db
def test_validate_entries(service: services.VoteService, vote):

  with pytest.raises(UserInvalidVoteException):
    service.validate_vote(vote._replace(
      entries=list(models.CompetitionEntry.objects.all())
    ))


@pytest.mark.django_db
def test_validate_in(service: services.VoteService, vote):
  with pytest.raises(UserInvalidVoteException):
    service.validate_vote(vote._replace(
      entries=list(models.CompetitionEntry.objects.all())
    ))


@pytest.mark.django_db
def test_validate_invalid_competition_type(service: services.VoteService, vote):
  with pytest.raises(InvalidVoteException):
    service.validate_vote(vote._replace(competition=42))


@pytest.mark.django_db
def test_validate_invalid_entry_type(service: services.VoteService, vote):
  with pytest.raises(InvalidVoteException):
    service.validate_vote(vote._replace(entries=[42]))


@pytest.mark.django_db
def test_validate_invalid_invalid_entry(service: services.VoteService, vote):
  with pytest.raises(InvalidVoteException):
    service.validate_vote(vote._replace(entries=[]))


@pytest.mark.django_db
def test_validate_invalid_no_entries(service: services.VoteService, vote, other_entry):
  with pytest.raises(InvalidVoteException):
    service.validate_vote(vote._replace(entries=[other_entry]))


@pytest.mark.django_db
def test_validate_conflicting_nonce(service: services.VoteService, vote):

  models.VoteGroup.objects.create(competition=vote.competition, used_nonce=vote.nonce)

  with pytest.raises(UserInvalidVoteException):
    service.validate_vote(vote)


@pytest.mark.django_db
def test_validate_duplicate_entries(service: services.VoteService, vote):

  with pytest.raises(InvalidVoteException):
    service.validate_vote(vote._replace(
      entries=vote.entries+vote.entries
    ))


