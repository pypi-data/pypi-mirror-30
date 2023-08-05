# coding=utf-8
import abc
import base64
import hashlib
import hmac
from urllib.parse import urlencode, parse_qs

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.db import transaction
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy

from . import models

import binascii
import typing

from MailChecker import MailChecker


CompetitionVote = typing.NamedTuple(
  "CompetitionVote",
  (
    ("competition", models.Competition),
    ("entries", typing.List[models.CompetitionEntry]),
    ("source_email", str),
    ("nonce", bytes),
  )
)


class InvalidVoteException(Exception):
  pass


class UserInvalidVoteException(Exception):

  def __init__(self, message) -> None:
    super().__init__(message)


class CompetitionService(object):

  def __init__(self, competition: models.Competition):
    self.competition = competition

  def register_vote(self, vote: CompetitionVote):
    with transaction.atomic():
      group = models.VoteGroup.objects.create(
        competition=vote.competition,
        used_nonce=vote.nonce,
        vote_source=vote.source_email
      )
      for entry in vote.entries:
        models.Vote.objects.create(group=group, entry=entry)


class VoteService(object):

  def validate_vote(self, vote: CompetitionVote):
    self.__basic_validate_vote(vote)
    self.__validate_vote_with_competition(vote)

  def __validate_vote_with_competition(self, vote: CompetitionVote):
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
    :param vote:
    :return:
    """
    if not isinstance(vote.competition, models.Competition):
      raise InvalidVoteException()
    if not len(vote.entries) > 0:
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
    vote_args = [
      ('competition', vote.competition.pk),
      ('nonce', vote.nonce),
      ('source_email', vote.source_email),
    ]
    vote_args.extend(sorted(("entry", str(entry.pk)) for entry in vote.entries))
    return urlencode(vote_args).encode('ascii')

  def deserialize_vote(self, vote: bytes) -> CompetitionVote:
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
      competition: models.Competition,
      vote: bytes
  ) -> bytes:
    hmac_obj = hmac.new(
      competition.competition_encryption_key,
      digestmod=hashlib.sha256
    )
    hmac_obj.update(vote)
    return hmac_obj.digest()

  def verify_vote_signature(
      self,
      competition: models.Competition,
      vote: bytes,
      signature: bytes
  ):

    expected_signature = self.sign_vote(competition, vote)
    if not hmac.compare_digest(signature, expected_signature):
      raise InvalidVoteException("Incorrect vote")

  def vote_to_signed_query_args(self, vote: CompetitionVote) -> typing.Dict:
    self.validate_vote(vote)
    serialized_vote = self.serialize_vote(vote)
    vote_signature = self.sign_vote(vote.competition, serialized_vote)
    return {
      "vote": base64.b64encode(serialized_vote),
      "sig": base64.b64encode(vote_signature)
    }

  def query_args_to_vote(self, query: typing.Dict) -> CompetitionVote:
    try:
      vote_arg = query['vote']
      sig_arg = query['sig']
    except KeyError as key_error:
      raise InvalidVoteException from key_error

    vote_arg = vote_arg.encode('ascii') if isinstance(vote_arg, str) else vote_arg
    sig_arg = sig_arg.encode('ascii') if isinstance(sig_arg, str) else sig_arg

    if not all(isinstance(obj, bytes) for obj in[vote_arg, sig_arg]):
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

  def __init__(
      self,
      vote: CompetitionVote,
      confirm_url: str
  ):
    self.vote = vote
    self.confirm_url = confirm_url

  def send_confirm_mail(self):
    raise NotImplementedError


class SimpleMailService(AbstractMailService):

  def get_subject(self) -> str:
    return ugettext_lazy("Vote confirmation for {}").format(self.vote.competition.name)

  def get_mail_render_context(self):
    return {
      "vote": self.vote,
      "vote_confirm_url": self.confirm_url
    }

  def get_mail_template(self):
    return get_template("django_competition/email.txt")

  def get_mail_contents(self):
    return self.get_mail_template().render(context=self.get_mail_render_context())

  def get_email_from(self):
    return settings.DEFAULT_FROM_EMAIL

  def send_confirm_mail(self):
    send_mail(
      subject=self.get_subject(),
      message=self.get_mail_contents(),
      from_email=self.get_email_from(),
      recipient_list=[self.vote.source_email]
    )
