from django.contrib import admin
from django.contrib.admin import register
from django.urls import reverse
from django.utils.safestring import mark_safe

from create.models import Box
from create.models import BoxPosition
from create.models import Game
from create.models import Playbook
from create.models import Sheet


@register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("name",)


def image_added(sheet) -> bool:
    return bool(sheet.image is not None)


def image_size(sheet) -> str:
    return f"{sheet.image_width} x {sheet.image_height}" if sheet.image else ""


def edit_places(sheet):
    return mark_safe(f'<a href="{reverse("edit_boxes")}?sheet_id={sheet.id}">Edit boxes</a>')


@register(Sheet)
class SheetAdmin(admin.ModelAdmin):
    list_display = "name", edit_places, "game", image_added, image_size


@register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = "name", "group", "sheet", "game", "sort_order"
    list_filter = "game", "group", "sheet"


@register(BoxPosition)
class BoxPositionAdmin(admin.ModelAdmin):
    list_display = "box", "sheet", "left", "top", "width", "height"
    list_filter = "sheet", "box"


@register(Playbook)
class PlaybookAdmin(admin.ModelAdmin):
    list_display = "name", "game"
