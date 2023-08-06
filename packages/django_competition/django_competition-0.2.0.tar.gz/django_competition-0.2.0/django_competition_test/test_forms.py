# coding=utf-8

"""Tests for competition form."""

import typing

import pytest
from django.forms import Form

from django_competition.forms import create_vote_form

# pylint: disable=redefined-outer-name


@pytest.fixture()
def competition_form(competition):
  """Type representing a form for this competition."""
  return create_vote_form(competition)


@pytest.mark.django_db
def test_choice_fields(competition_form):
  """Test choice form has fields for each vote."""
  form = competition_form()
  choice_fields = {
    field for field in form.fields.keys()
    if field.startswith("choice_")
  }
  assert choice_fields == {'choice_0', 'choice_1', 'choice_2'}


@pytest.mark.django_db
def test_valid_form(valid_competition_form_data, competition_form: typing.Type[Form]):
  """Tests a form with valid data validates."""
  form = competition_form(data=valid_competition_form_data)
  assert form.is_valid()


@pytest.mark.django_db
def test_invalid_form(invalid_competition_form_data, competition_form: typing.Type[Form]):
  """Multiple tests that check various inputs that could make competition form not validate."""
  data, broken_field = invalid_competition_form_data
  form = competition_form(data=data)
  assert not form.is_valid()
  assert form.errors.keys() == broken_field, form.errors

