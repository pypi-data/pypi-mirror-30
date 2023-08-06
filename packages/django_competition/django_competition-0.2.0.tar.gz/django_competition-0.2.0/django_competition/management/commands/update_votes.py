# coding=utf-8
"""Command that recalculates votes."""
from django.core.management import CommandParser
from django.core.management.base import BaseCommand

from django_competition import services


class Command(BaseCommand):
  """Command that recalculates votes."""
  help = 'Re-calculate votes on competitions (in case of mismatch)'

  def add_arguments(self, parser: CommandParser):
    parser.add_argument('--competition-id', type=int)

  def handle(self, *args, **options):

    services.CompetitionService.recalculate_votes(options.get('competition-id'))
