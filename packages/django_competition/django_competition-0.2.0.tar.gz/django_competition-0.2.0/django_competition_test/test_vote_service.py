# coding=utf-8

"""Tests for vote service."""

import pytest

from django_competition import models, services
from django_competition.services import InvalidVoteException, UserInvalidVoteException


# pylint: disable=redefined-outer-name,invalid-name,no-member,unused-argument


@pytest.mark.django_db
def test_serialize_vote(
    service: services.VoteService,
    vote,
    serialized_vote
):
  """Checks vote serialized form (serialization part)."""
  assert service.serialize_vote(vote) == serialized_vote


@pytest.mark.django_db
def test_deserialize_vote(
    service: services.VoteService,
    vote,
    serialized_vote
):
  """Checks vote serialized form (deserialization part)."""
  assert service.deserialize_vote(serialized_vote) == vote


@pytest.mark.django_db
def test_vote_signature(
    service: services.VoteService,
    competition,
    serialized_vote,
    vote_signature
):
  """Test vote signature."""
  assert service.sign_vote(competition, serialized_vote) == vote_signature


@pytest.mark.django_db
def test_vote_verify_positive(
    service: services.VoteService,
    competition,
    serialized_vote,
    vote_signature
):
  """Test verification for valid vote."""
  service.verify_vote_signature(competition, serialized_vote, vote_signature)


@pytest.mark.django_db
def test_vote_verify_negative(
    service: services.VoteService,
    competition,
    serialized_vote,
    vote_signature
):
  """Test verification for invalid signature."""
  invalid_signature = b'\x01' * 32
  assert invalid_signature != vote_signature
  with pytest.raises(InvalidVoteException):
    service.verify_vote_signature(competition, serialized_vote, invalid_signature)


@pytest.mark.django_db
def test_vote_to_query(
    service: services.VoteService,
    vote
):
  """Test vote serialization and deserialization recovers the same vote."""
  query = service.vote_to_signed_query_args(vote)
  recovered_vote = service.query_args_to_vote(query)
  assert vote == recovered_vote


@pytest.mark.django_db
@pytest.mark.parametrize('query', [
  # Missing signature and vote
  {},
  {"foo": "bar"},
  # Invalid types
  {"sig": 1, "vote": object()},
  # Not base64 encoded signature and vote
  {"sig": b"foo", "vote": b"bar"}
])
def test_vote_to_query_invalid_args(
    service: services.VoteService,
    query
):
  """Test various malformed votes."""
  with pytest.raises(InvalidVoteException):
    service.query_args_to_vote(query)


@pytest.mark.django_db
def test_validate_invalid_email(service: services.VoteService, vote):
  """Validate vote that does not contain a valid e-mail."""
  with pytest.raises(UserInvalidVoteException):
    service.validate_vote(vote._replace(
      source_email="Not a valid e-mail"
    ))


@pytest.mark.django_db
def test_validate_disposable_email(service: services.VoteService, vote):
  """Test vote with disposable e-mail."""
  with pytest.raises(UserInvalidVoteException):
    service.validate_vote(vote._replace(
      source_email="test@niepodam.pl"
    ))


@pytest.mark.django_db
def test_validate_entries(service: services.VoteService, vote):
  """Test vote with too many entries."""
  with pytest.raises(UserInvalidVoteException):
    service.validate_vote(vote._replace(
      entries=list(models.CompetitionEntry.objects.all())
    ))


@pytest.mark.django_db
def test_validate_invalid_competition_type(service: services.VoteService, vote):
  """Test for invalid competition."""
  with pytest.raises(InvalidVoteException):
    service.validate_vote(vote._replace(competition=42))


@pytest.mark.django_db
def test_validate_invalid_entry_type(service: services.VoteService, vote):
  """Test for invalid entry."""
  with pytest.raises(InvalidVoteException):
    service.validate_vote(vote._replace(entries=[42]))


@pytest.mark.django_db
def test_validate_invalid_no_entries(service: services.VoteService, vote):
  """Test for no entries in vote."""
  with pytest.raises(InvalidVoteException):
    service.validate_vote(vote._replace(entries=[]))


@pytest.mark.django_db
def test_validate_invalid_entry_from_other_competition(
    service: services.VoteService,
    vote,
    other_entry
):
  """Test entry from other competition."""
  with pytest.raises(InvalidVoteException):
    service.validate_vote(vote._replace(entries=[other_entry]))


@pytest.mark.django_db
def test_validate_conflicting_nonce(service: services.VoteService, vote):
  """Test vote with conflicting nonce does not validate."""

  models.VoteGroup.objects.create(competition=vote.competition, used_nonce=vote.nonce)

  with pytest.raises(UserInvalidVoteException):
    service.validate_vote(vote)


@pytest.mark.django_db
def test_validate_duplicate_entries(service: services.VoteService, vote):
  """Test validate vote with duplicate entries."""
  with pytest.raises(InvalidVoteException):
    service.validate_vote(vote._replace(
      entries=vote.entries + vote.entries
    ))


@pytest.mark.django_db
@pytest.mark.parametrize('nonce', [1, 'foobarbaz', object()])
def test_vote_nonce_invalid(service: services.VoteService, vote, nonce):
  """Test vote with invalid nonce type."""
  with pytest.raises(InvalidVoteException):
    service.validate_vote(vote._replace(nonce=nonce))


@pytest.mark.django_db
def test_validate_competition_closed(
    service: services.VoteService,
    vote,
    competition,
):
  """Test validate case where vote is valid, but competition is closed."""
  competition.voting_open = False
  competition.save()

  with pytest.raises(UserInvalidVoteException):
    service.validate_vote(vote)

