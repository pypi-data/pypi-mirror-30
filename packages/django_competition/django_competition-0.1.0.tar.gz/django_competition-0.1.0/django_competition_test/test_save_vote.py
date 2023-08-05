# coding=utf-8

import pytest

from django_competition import services, models

@pytest.fixture()
def persisted_vote(
    vote,
    competition: models.Competition
):
  service = services.CompetitionService(competition)
  service.register_vote(vote)
  return vote


@pytest.mark.django_db
def test_sanity(vote: services.CompetitionVote):
  for entry in vote.entries:
    assert entry.votes == 0


@pytest.mark.django_db
def test_saved_vote_updates_entries(
    persisted_vote: services.CompetitionVote
):
  for entry in persisted_vote.entries:
    entry.refresh_from_db()
    assert entry.votes == 1


@pytest.mark.django_db
def test_saved_vote_updates_entries(
    persisted_vote: services.CompetitionVote
):
  for entry in persisted_vote.entries:
    entry.refresh_from_db()
    assert entry.votes == 1


@pytest.mark.django_db
def test_saved_vote_delete_updates_entries(
    persisted_vote: services.CompetitionVote
):
  for vote_group in models.VoteGroup.objects.all():
    vote_group.delete()
  for entry in persisted_vote.entries:
    entry.refresh_from_db()
    assert entry.votes == 0

