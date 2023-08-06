"""Views module"""
import random
from urllib.parse import urlencode

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.utils.safestring import SafeString
from django.views.generic import FormView, TemplateView, DetailView

from django_competition.services import (
  VoteService,
  UserInvalidVoteException,
  InvalidVoteException,
  SETTINGS_SERVICE,
)
from . import services, models, forms


class ConfirmVote(TemplateView):
  """View that asks user to confirm vote."""

  template_name = "django_competition/vote_confirm.html"

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.service = services.VoteService()
    self.vote = None
    self.form_error = None

  def get_context_data(self, **kwargs):
    kwargs.update({
      "vote": self.vote,
      "form_error": self.form_error
    })
    return super().get_context_data(**kwargs)

  def dispatch(self, *args, **kwargs):  # pylint: disable=arguments-differ
    try:
      self.vote = self.service.query_args_to_vote(self.request.GET)
    except UserInvalidVoteException as exception:
      self.form_error = exception.args[0]
      return self.get(*args, **kwargs)
    except InvalidVoteException:
      return HttpResponse(status=400)
    return super().dispatch(*args, **kwargs)

  def post(self, request):  # pylint: disable=unused-argument
    """Post handler, register vote and redirects."""
    competition_service = services.CompetitionService(self.vote.competition)
    # Note we know vote is now valid.
    competition_service.register_vote(self.vote)
    return HttpResponseRedirect(
      redirect_to=SETTINGS_SERVICE.vote_registered_url
    )


class VoteSaved(TemplateView):
  """Landing page after user voted but before confirmed."""

  template_name = "django_competition/vote_performed.html"


class CompetitionVote(DetailView, FormView):

  """Vote page."""

  model = models.Competition
  context_object_name = "competition"
  template_name = "django_competition/vote.html"

  def get_form_class(self):
    return forms.create_vote_form(
      self.object,
      SETTINGS_SERVICE.base_form
    )

  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    entries = list(self.object.entries.all())
    random.shuffle(entries)
    ctx.update({
      "entries": entries,
    })
    return ctx

  def send_email(self, vote):
    """Send confirmation e-mail."""

    SETTINGS_SERVICE.mail_service(
      vote=vote,
      confirm_url=self.format_confirm_url(vote)
    ).send_confirm_mail()

  def format_confirm_url(self, vote) -> SafeString:
    """Prepare confirmation url."""
    service = VoteService()
    params = service.vote_to_signed_query_args(vote)
    query_string = urlencode(params, doseq=False)
    path = reverse("competition:confirm")
    return SafeString(
      self.request.build_absolute_uri(path) + "?" + query_string
    )

  def form_valid(self, form):
    self.send_email(form.make_vote())
    return super().form_valid(form)

  def get_success_url(self):
    return SETTINGS_SERVICE.vote_confirm_success_url

  def dispatch(self, request, *args, **kwargs):
    self.object = self.get_object()  # pylint: disable=attribute-defined-outside-init
    return super().dispatch(request, *args, **kwargs)
