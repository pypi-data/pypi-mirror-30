"""Services module."""

# coding=utf-8
import abc
import base64
import binascii
import hashlib
import hmac
import importlib
import typing
from urllib.parse import urlencode, parse_qs

import bleach
from MailChecker import MailChecker
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import get_template
from django.utils.encoding import force_bytes
from django.utils.translation import ugettext_lazy

from . import models

DEFAULT_SETTINGS = {
  "MAIL_SERVICE": "django_competition.services.SimpleMailService",
  "COMPETITION_BASE_FORM": "django_competition.forms.CompetitionFormWithConfirmations",
  "BLEACH_CLEANER": "django_competition.services.BLEACH_CLEANER"
}


CompetitionVote = typing.NamedTuple(
  "CompetitionVote",
  (
    ("competition", 'models.Competition'),
    ("entries", typing.List['models.CompetitionEntry']),
    ("source_email", str),
    ("nonce", bytes),
  )
)

# pylint: disable=no-self-use


class SettingsService(object):

  """Service that encapsulates settings."""

  def __init__(self, settings_dict: typing.Optional[dict] = None):
    if settings_dict is None:
      settings_dict = settings.COMPETITION_SETTINGS
    self.settings = dict(DEFAULT_SETTINGS)
    self.settings.update(settings_dict)

  @classmethod
  def type_from_string(cls, service_type: str):
    """Load mail service from settings."""
    module, type_name = service_type.rsplit(".", 1)
    module = importlib.import_module(module)
    return getattr(module, type_name)

  @property
  def mail_service(self) -> typing.Type['AbstractMailService']:
    """Returns mail service."""
    return self.type_from_string(self.settings['MAIL_SERVICE'])

  @property
  def base_form(self) -> typing.Type:
    """Returns base form for voting."""
    return self.type_from_string(self.settings['COMPETITION_BASE_FORM'])

  @property
  def terms_url(self) -> str:
    """Returns terms and conditions url."""
    return self.settings['TERMS_AND_CONDITIONS_URL']

  @property
  def vote_registered_url(self):
    """Return vote redirect url after user """
    return self.settings['VOTE_REGISTERED_URL']

  @property
  def vote_confirm_success_url(self):
    """Return redirect after vote confirmation."""
    return self.settings['VOTE_SUCCESS_URL']

  @property
  def bleach_cleaner(self) -> bleach.Cleaner:
    """Returns cleaner used for sanitizing markdown"""
    return self.type_from_string(self.settings['BLEACH_CLEANER'])


class InvalidVoteException(Exception):
  """Error raised when we have invalid vote and error is an application"""
  pass


class UserInvalidVoteException(Exception):
  """Error raised when user made some disallowed action."""
  #                                     Not useless as we force message argument.
  def __init__(self, message) -> None:  # pylint: disable=useless-super-delegation
    super().__init__(message)


class CompetitionService(object):
  """Service handling competition."""

  def __init__(self, competition: 'models.Competition'):
    self.competition = competition

  def register_vote(self, vote: CompetitionVote):
    """Store vote in database."""
    assert self.competition == vote.competition
    with transaction.atomic():
      VoteService().validate_vote(vote)
      group = models.VoteGroup.objects.create(
        competition=vote.competition,
        used_nonce=vote.nonce,
        vote_source=vote.source_email
      )
      for entry in vote.entries:
        models.Vote.objects.create(group=group, entry=entry)

  @classmethod
  def recalculate_votes(cls, competition_id: int = None):
    """Recount all votes."""
    if isinstance(competition_id, models.Competition):
      competition_id = competition_id.pk

    queryset = models.CompetitionEntry.objects.all()
    if competition_id is not None:
      queryset = queryset.filter(competition__pk=competition_id)
    for entry in queryset.select_for_update():
      entry.votes = models.Vote.objects.filter(entry=entry).count()
      entry.save()


class VoteService(object):

  """Service for vote validation."""

  def validate_vote(self, vote: CompetitionVote):
    """Validates a vote."""
    self.__basic_validate_vote(vote)
    self.__validate_vote_with_competition(vote)

  def __validate_vote_with_competition(self, vote: CompetitionVote):
    """Helper. Validates a vote with competition requirements."""
    competition = vote.competition

    if not competition.voting_open:
      raise UserInvalidVoteException("Competition is closed.")

    if not MailChecker.is_valid_email_format(vote.source_email):
      raise UserInvalidVoteException("E-mail appears to be invalid")

    if not competition.allow_disposable_emails:
      if MailChecker.is_blacklisted(vote.source_email):
        raise UserInvalidVoteException(
          "You are using blacklisted e-mail provider"
        )

    if competition.entries_per_vote > 0:
      if competition.entries_per_vote < len(vote.entries):
        raise UserInvalidVoteException(ugettext_lazy(
          "You can vote for at most {} entries.".format(len(vote.entries))
        ))

  def __basic_validate_vote(self, vote: CompetitionVote):
    """
    Misc checks that verify vote was well-formed.
    """
    if not isinstance(vote.competition, models.Competition):
      raise InvalidVoteException()
    if not len(vote.entries) > 0:  # pylint: disable=len-as-condition
      raise InvalidVoteException()

    if not isinstance(vote.nonce, bytes):
      raise InvalidVoteException()

    all_entries = {entry.pk for entry in vote.competition.entries.all()}

    for entry in vote.entries:
      if not isinstance(entry, models.CompetitionEntry):
        raise InvalidVoteException()
      if entry.pk not in all_entries:
        raise InvalidVoteException()

    if len(vote.entries) != len({entry.pk for entry in vote.entries}):
      raise InvalidVoteException()

    conflicting_nonces = models.VoteGroup.objects.filter(
      competition=vote.competition,
      used_nonce=vote.nonce
    )
    if conflicting_nonces.exists():
      raise UserInvalidVoteException(
        "You have already confirmed this vote."
      )

  def serialize_vote(self, vote: CompetitionVote) -> bytes:
    """
    Serialize vote to opaque bytes (which can be signed).
    """
    vote_args = [
      ('competition', vote.competition.pk),
      ('nonce', vote.nonce),
      ('source_email', vote.source_email),
    ]
    vote_args.extend(sorted(("entry", str(entry.pk)) for entry in vote.entries))
    return urlencode(vote_args).encode('ascii')

  def deserialize_vote(self, vote: bytes) -> CompetitionVote:
    """De-serialize vote from bytes."""
    parsed = parse_qs(vote.decode('ascii'))

    return CompetitionVote(
      nonce=parsed['nonce'][0].encode('ascii'),
      source_email=parsed['source_email'][0],
      competition=models.Competition.objects.get(pk=int(parsed['competition'][0])),
      entries=list(models.CompetitionEntry.objects.filter(
        pk__in=[int(pk) for pk in parsed['entry']]
      ))
    )

  def sign_vote(
      self,
      competition: 'models.Competition',
      vote: bytes
  ) -> bytes:
    """Sign vote bytes."""
    hmac_obj = hmac.new(
      force_bytes(competition.competition_encryption_key),
      digestmod=hashlib.sha256
    )
    hmac_obj.update(vote)
    return hmac_obj.digest()

  def verify_vote_signature(
      self,
      competition: 'models.Competition',
      vote: bytes,
      signature: bytes
  ):
    """Verify vote signature."""
    expected_signature = self.sign_vote(competition, vote)
    if not hmac.compare_digest(signature, expected_signature):
      raise InvalidVoteException("Incorrect vote")

  def vote_to_signed_query_args(self, vote: CompetitionVote) -> typing.Dict:
    """Serialize vote to signed query arguments."""
    self.validate_vote(vote)
    serialized_vote = self.serialize_vote(vote)
    vote_signature = self.sign_vote(vote.competition, serialized_vote)
    return {
      "vote": base64.b64encode(serialized_vote),
      "sig": base64.b64encode(vote_signature)
    }

  def query_args_to_vote(self, query: typing.Dict) -> CompetitionVote:
    """De-serialize vote from signed query arguments."""
    try:
      vote_arg = query['vote']
      sig_arg = query['sig']
    except KeyError as key_error:
      raise InvalidVoteException from key_error

    vote_arg = vote_arg.encode('ascii') if isinstance(vote_arg, str) else vote_arg
    sig_arg = sig_arg.encode('ascii') if isinstance(sig_arg, str) else sig_arg

    if not all(isinstance(arg, bytes) for arg in[vote_arg, sig_arg]):
      raise InvalidVoteException()
    try:
      serialized_vote = base64.b64decode(vote_arg, validate=True)
      vote_signature = base64.b64decode(sig_arg, validate=True)
    except binascii.Error as decode_error:
      raise InvalidVoteException from decode_error

    vote = self.deserialize_vote(serialized_vote)
    self.verify_vote_signature(vote.competition, serialized_vote, vote_signature)

    self.validate_vote(vote)

    return vote


class AbstractMailService(object, metaclass=abc.ABCMeta):
  """Base class for a service that sends e-mails with confirmation."""
  def __init__(
      self,
      vote: CompetitionVote,
      confirm_url: str
  ):
    self.vote = vote
    self.confirm_url = confirm_url

  def send_confirm_mail(self):
    """Send confirmation e-mail to voter."""
    raise NotImplementedError


class SimpleMailService(AbstractMailService):
  """Base class for sending confirmation e-mails to users."""

  def get_subject(self) -> str:
    """Get message subject."""
    return ugettext_lazy("Vote confirmation for {}").format(self.vote.competition.name)

  def get_mail_render_context(self):
    """Get e-mail context"""
    return {
      "vote": self.vote,
      "vote_confirm_url": self.confirm_url
    }

  def get_mail_template(self):
    """Return mail template."""
    return get_template("django_competition/email.txt")

  def get_mail_contents(self):
    """Return rendered template."""
    return self.get_mail_template().render(context=self.get_mail_render_context())

  def get_email_from(self):
    """Sender address."""
    return settings.DEFAULT_FROM_EMAIL

  def send_confirm_mail(self):
    send_mail(
      subject=self.get_subject(),
      message=self.get_mail_contents(),
      from_email=self.get_email_from(),
      recipient_list=[self.vote.source_email]
    )


SETTINGS_SERVICE = SettingsService()


BLEACH_ALLOWED_TAGS = tuple(bleach.ALLOWED_TAGS + ['p'])
BLEACH_CLEANER = bleach.Cleaner(tags=BLEACH_ALLOWED_TAGS)
