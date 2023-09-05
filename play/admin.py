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


def view_case_files(play):
    return mark_safe(f'<a href="{reverse("case_files")}?play_id={play.id}">Case files</a>')


def has_image(obj):
    return "✔︎" if obj.image else ""


def paste_image(obj):
    return mark_safe(
        f"""<div style="cursor: copy" onclick="pasteImage('{type(obj).__name__}', {obj.id});">Paste image</div>"""
    )


def show(modeladmin, request, queryset):
    queryset.update(visible=True)


def hide(modeladmin, request, queryset):
    queryset.update(visible=False)


@register(Play)
class PlayAdmin(admin.ModelAdmin):
    list_display = ("name", "game", all_characters, view_case_files)


@register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("name",)


def open_character(character):
    return mark_safe(f'<a href="{reverse("edit_character")}?character_id={character.id}">▶︎</a>')


@register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ("__str__", open_character, "playbook", paste_image, "play", "player")
    list_filter = "playbook", "play", "player"


@register(CaseFiles)
class CaseFilesAdmin(admin.ModelAdmin):
    list_display = ("__str__",)


@register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = "name", "sort_order", has_image, paste_image, "visible", "play"
    list_filter = ("play",)
    ordering = ["-sort_order"]
    actions = show, hide


@register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = "name", "description", "sort_order", has_image, paste_image, "visible", "case"
    list_filter = "case", "case__play"
    actions = show, hide


@register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = "name", "sort_order", "visible", "case"
    list_filter = "case", "case__play"
    actions = show, hide
