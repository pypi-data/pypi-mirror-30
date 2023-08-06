"""Admin module."""

from django.contrib import admin

from . import models


class CompetitionEntry(admin.TabularInline):
  """Competition Entry in-line admin."""
  model = models.CompetitionEntry

  fields = [
    'name',
    'description',
    'votes',
  ]

  readonly_fields = [
    'votes'
  ]


@admin.register(models.Competition)
class CompetitionAdmin(admin.ModelAdmin):
  """Competition model admin."""

  list_display = [
    'name'
  ]

  fields = [
    'name',
    'description',
    'votes_per_day',
    'entries_per_vote',
    'allow_disposable_emails'
  ]

  inlines = [
    CompetitionEntry
  ]
