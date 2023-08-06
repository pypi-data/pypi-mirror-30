# coding=utf-8
"""Tests utilities related to saving votes and updating entry.votes attribute."""

import pytest
from django.core.management import call_command

from django_competition import services, models


# pylint: disable=redefined-outer-name,invalid-name,unused-argument


@pytest.fixture()
def persisted_vote(
    vote,
    competition: models.Competition
) -> services.CompetitionVote:
  """Vote stored in database."""
  service = services.CompetitionService(competition)
  service.register_vote(vote)
  return vote


@pytest.mark.django_db
def test_saved_vote_updates_entries(
    persisted_vote: services.CompetitionVote
):
  """Test entry.votes are updated when entry is saved."""
  for entry in persisted_vote.entries:
    entry.refresh_from_db()
    assert entry.votes == 1


@pytest.mark.django_db
def test_saved_vote_delete_updates_entries(
    persisted_vote: services.CompetitionVote
):
  """Test entry.votes are updated when entry is deleted."""
  for vote_group in models.VoteGroup.objects.all():
    vote_group.delete()
  for entry in persisted_vote.entries:
    entry.refresh_from_db()
    assert entry.votes == 0


def reset_competition_votes(competition):
  """
  Helper that sets votes to zero (but doesn't remove vote instants so after
  vote recalculation we should recover votes.
  """
  for entry in competition.entries.all():
    entry.votes = 0
    entry.save()


@pytest.mark.django_db
def test_synchronize_votes_single_competition(
    competition,
    other_competition,
    with_competition_votes
):
  """Test vote sync on single competition (other competition is not synced)"""
  reset_competition_votes(competition)
  reset_competition_votes(other_competition)
  services.CompetitionService.recalculate_votes(competition)
  for entry in competition.entries.all():
    assert entry.votes == abs(entry.pk)
  for entry in other_competition.entries.all():
    assert entry.votes == 0


@pytest.mark.django_db
def test_synchronize_votes_all_competitions(
    competition,
    other_competition,
    with_competition_votes
):
  """Test vote sync on all competitions."""
  reset_competition_votes(competition)
  reset_competition_votes(other_competition)
  services.CompetitionService.recalculate_votes()
  for entry in competition.entries.all():
    assert entry.votes == abs(entry.pk)
  for entry in other_competition.entries.all():
    assert entry.votes == abs(entry.pk)


@pytest.mark.django_db
def test_update_votes_command_single_competition(
    competition,
    other_competition,
    with_competition_votes
):
  """Test vote sync on single competition (using manage command)."""
  reset_competition_votes(competition)
  reset_competition_votes(other_competition)
  call_command("update_votes", **{"competition-id": competition.pk})
  for entry in competition.entries.all():
    assert entry.votes == abs(entry.pk)
  for entry in other_competition.entries.all():
    assert entry.votes == 0


@pytest.mark.django_db
def test_update_votes_command_both_competitions(
    competition,
    other_competition,
    with_competition_votes
):
  """Test vote sync on all competitions (using manage command)."""
  reset_competition_votes(competition)
  reset_competition_votes(other_competition)
  call_command("update_votes")
  for entry in competition.entries.all():
    assert entry.votes == abs(entry.pk)
  for entry in other_competition.entries.all():
    assert entry.votes == abs(entry.pk)
