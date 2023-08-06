# coding=utf-8

"""Forms."""

import base64
import os
import typing
from collections import OrderedDict

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField
from django.forms.forms import DeclarativeFieldsMetaclass
from django.utils.safestring import SafeString
from django.utils.translation import ugettext_lazy

from django_competition.services import SETTINGS_SERVICE
from . import models, services


class BaseVoteCompetitionForm(forms.Form):
  """Base form, that contains validations."""

  your_email = forms.EmailField(
    required=True,
    label=ugettext_lazy("Your e-mail"),
  )

  def clean(self):

    if self.errors:
      # If there are errors already don't validate further
      return

    selected_entries = set()

    for name in self.fields.keys():
      if not name.startswith('choice_'):
        continue
      entry = self.cleaned_data.get(name)
      if entry is None:
        continue
      if entry in selected_entries:
        raise ValidationError(
          "You have selected the same entry twice. Entry is: {}".format(entry.name)
        )
      selected_entries.add(entry)

    vote = self.make_vote()
    try:
      services.VoteService().validate_vote(vote)
    except services.UserInvalidVoteException as exception:
      raise ValidationError(exception.args[0]) from exception

  def get_vote_entries(self):
    """Returns entries this vote voted on."""
    entries = []
    for name in self.fields.keys():
      if name.startswith('choice_'):
        value = self.cleaned_data[name]
        if value is not None:
          entries.append(value)
    return entries

  def make_vote(self):
    """Create a CompetitionVote instance."""
    return services.CompetitionVote(
      competition=self.competition,
      source_email=self.cleaned_data['your_email'],
      entries=self.get_vote_entries(),
      nonce=base64.b64encode(os.urandom(16))
    )


class CompetitionFormWithConfirmations(BaseVoteCompetitionForm):

  """Base form with extra consents."""

  store_e_mail_consent = forms.BooleanField(
    label=ugettext_lazy(
      "I agree that this platform will store my e-mail address and use it to check any "
      "fraudulent activity in the voting process."
    ),
    required=True
  )

  terms_and_condition_consents = forms.BooleanField(
    required=True,
  )

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['terms_and_condition_consents'].label = SafeString(ugettext_lazy(
      "I agree to terms and conditions <a href=\"{}\">located here</a>".format(
        SETTINGS_SERVICE.terms_url
      )
    ))


class CompetitionEntryChoiceField(ModelChoiceField):

  """Field for competition entry in voting view."""

  def label_from_instance(self, obj: models.Competition):
    return obj.name


def create_vote_form(
    competition: models.Competition,
    form_base=CompetitionFormWithConfirmations
) -> typing.Type[BaseVoteCompetitionForm]:
  """
  Creates competition form form a base form.

  Adds choice fields that allow end-users to actually vote.
  :param competition: Competition for which to prepare form.
  :param form_base: Base form.
  """

  form_fields = [
    ('competition', competition)
  ]

  votes = min(
    competition.entries.count(),
    competition.entries_per_vote
  )

  form_fields.extend((
    (
      "choice_{choice}".format(choice=choice),
      CompetitionEntryChoiceField(
        required=choice == 0,
        queryset=competition.entries.all(),
        label=ugettext_lazy("Your choice"))
    )
    for choice in range(votes)
  ))

  return DeclarativeFieldsMetaclass(
    "CompetitionForm", (form_base, ), OrderedDict(form_fields)
  )
