from django.contrib import admin
from django.contrib.admin import register
from django.urls import reverse
from django.utils.safestring import mark_safe
from play.models import Case
from play.models import CaseFiles
from play.models import Character
from play.models import Location
from play.models import Person
from play.models import Play
from play.models import Player


def all_characters(play):
    return mark_safe(f'<a href="{reverse("all_characters")}?play_id={play.id}">All characters</a>')


@register(Play)
class PlayAdmin(admin.ModelAdmin):
    list_display = ("name", "game", all_characters)


@register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("name",)


def open_character(character):
    return mark_safe(f'<a href="{reverse("edit_character")}?character_id={character.id}">▶︎</a>')


@register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ("__str__", open_character, "playbook", "play", "player")


@register(CaseFiles)
class CaseFilesAdmin(admin.ModelAdmin):
    list_display = ("__str__",)


@register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = "name", "play"


@register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = "name", "case"


@register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = "name", "case"
