"""Models."""

import os

from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.safestring import SafeString
from django.utils.translation import ugettext_lazy
from markdown import markdown

from django_competition.services import SETTINGS_SERVICE


def random_key() -> bytes:
  """Generate random key for competition."""
  return os.urandom(32)


class Competition(models.Model):
  """Configuration for a single competition."""

  name = models.CharField(max_length=128)
  description = models.TextField()

  votes_per_day = models.IntegerField(
    default=-1,
    help_text=ugettext_lazy(
      "If > 0 allows single e-mail to vote this many votes in each day."
      "If <= 0 allows only single vote."
    )
  )

  entries_per_vote = models.PositiveIntegerField(
    default=3,
    blank=False,
    validators=[MinValueValidator(1)],
    help_text=ugettext_lazy("How many (equally weighted) entries you may select in each vote. ")
  )

  allow_disposable_emails = models.BooleanField(
    default=True,
    blank=True,
    help_text=ugettext_lazy("If false we will try to block disposable e-mails.")
  )

  competition_encryption_key = models.BinaryField(
    default=random_key,
    editable=False,
    help_text=ugettext_lazy("Encryption key used to sign vote requests.")
  )

  voting_open = models.BooleanField(
    verbose_name=ugettext_lazy("True if users can vote on the competition"),
    default=True,
  )

  @property
  def description_html(self):
    """Return HTML from rendered markdown."""
    return SafeString(SETTINGS_SERVICE.bleach_cleaner.clean(markdown(self.description)))

  def __str__(self):
    return self.name


class CompetitionEntry(models.Model):

  """
  Competition entry.

  This can be voted on.
  """

  competition = models.ForeignKey(
    Competition,
    related_name="entries",
    on_delete=models.CASCADE
  )
  name = models.CharField(max_length=256)
  description = models.TextField(
    help_text=ugettext_lazy("You can use some markdown here.")
  )
  votes = models.IntegerField(default=0)
  """
  De-normalized vote count. This can be derived by counting all Votes attached
  to this entry.
  """

  @property
  def description_html(self):
    """Markdown rendered HTML."""
    return SafeString(SETTINGS_SERVICE.bleach_cleaner.clean(markdown(self.description)))

  def __str__(self):
    return self.name


class VoteGroup(models.Model):
  """
  Vote group.

  Represents a singe vote from a single user, but this vote might be for
  more than one entries.

  Each vote for each entry is stored in Vote model.
  """

  class Meta:
    ordering = ['competition', 'date_voted']

  competition = models.ForeignKey(Competition)
  vote_source = models.TextField(null=False, blank=False)
  """
  Identifier of voting entity. Most often e-mail ;)
  """
  date_voted = models.DateTimeField(null=False, blank=False, auto_now_add=True)

  used_nonce = models.BinaryField(
    db_index=True
  )


class Vote(models.Model):
  """
  Single vote for a single competition entry.
  """

  class Meta:
    ordering = ['group__competition', 'entry', 'group__date_voted']

  group = models.ForeignKey(
    VoteGroup,
    related_name="votes",
    on_delete=models.CASCADE
  )

  entry = models.ForeignKey(
    CompetitionEntry,
    related_name="entries",
    on_delete=models.CASCADE
  )


@receiver(post_save, sender=Vote)
def on_vote_save(instance: Vote, **kwargs):  # pylint: disable=unused-argument
  """On vote save add vote to entry."""
  with transaction.atomic():
    entry = CompetitionEntry.objects.select_for_update().get(pk=instance.entry_id)
    entry.votes += 1
    entry.save(update_fields=['votes'])


@receiver(post_delete, sender=Vote)
def on_vote_delete(instance: Vote, **kwargs):  # pylint: disable=unused-argument
  """On vote delete remove vote from entry."""
  with transaction.atomic():
    entry = CompetitionEntry.objects.select_for_update().get(pk=instance.entry_id)
    entry.votes -= 1
    entry.save(update_fields=['votes'])
