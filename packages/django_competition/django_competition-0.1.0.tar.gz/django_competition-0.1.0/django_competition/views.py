
import importlib
import random

from urllib.parse import urlencode

from django import views
from django.conf import settings
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.utils.safestring import SafeString
from django.views.generic import FormView, TemplateView, DetailView

from django_competition.services import VoteService
from . import services, models, forms


class ConfirmVote(TemplateView):

  template_name = "django_competition/vote_confirm.html"

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.service = services.VoteService()

  def dispatch(self, *args, **kwargs):
    self.vote = self.service.query_args_to_vote(self.request.GET)
    return super().dispatch(*args, **kwargs)

  def post(self, request):
    competition_service = services.CompetitionService(self.vote.competition)
    competition_service.register_vote(self.vote)
    return HttpResponseRedirect(
      redirect_to=settings.VOTE_REGISTERED
    )


class VoteSaved(TemplateView):

  template_name = "django_competition/vote_performed.html"


class CompetitionVote(DetailView, FormView):

  model = models.Competition
  context_object_name = "competition"
  template_name = "django_competition/vote.html"
  voting_form_base=forms.CompetitionFormWithConfirmations

  def get_form_class(self, form_class=None):
    return forms.create_vote_form(
      self.object,
      self.voting_form_base
    )

  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    entries = list(self.object.entries.all())
    random.shuffle(entries)
    ctx.update({
      "entries": entries,
    })
    return ctx

  def get_email_service_type(self):
    module, type_name = settings.COMPETITION_MAIL_SERVICE.rsplit(".", 1)
    module = importlib.import_module(module)
    return getattr(module, type_name)

  def send_email(self, vote):
    self.get_email_service_type()(
      vote=vote,
      confirm_url=self.format_confirm_url(vote)
    ).send_confirm_mail()

  def format_confirm_url(self, vote) -> SafeString:
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
    return reverse(settings.COMPETITION_VOTES_SUCCESS_REDIRECT)

  def dispatch(self, request, *args, **kwargs):
    self.object = self.get_object()
    return super().dispatch(request, *args, **kwargs)

