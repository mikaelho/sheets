import json
import os
import uuid

import requests
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import ensure_csrf_cookie

from create.models import Box
from create.models import BoxPosition
from create.views import default_size_by_kind
from play.admin import open_character
from play.models import Character
from play.models import Play


def game_view(request):
    play_id = int(request.GET.get("play_id"))
    play = Play.objects.get(id=play_id)

    def get_summary(full_description):
        return full_description[:full_description.index(".") + 1].strip()

    def get_rest(full_description):
        return full_description[full_description.index(".") + 1:].strip()

    characters = [{
        "name": str(character),
        "play_link": open_character(character),
        "player": character.player.name,
        "playbook": character.playbook.name,
        "summary": get_summary(character.playbook.description),
        "description": get_rest(character.playbook.description),
        "values": [
            (str(BoxPosition.objects.get(id=int(value_id)).box.id), value)
            for value_id, value in character.values.items()
        ],
    } for character in Character.objects.filter(play=play)]

    for_game = Q(game=play.game, sheet__isnull=True)
    for_sheets = Q(sheet__game=play.game)

    attributes = [{
        "group": box.group,
        "name": box.name,
        "id": str(box.id)
    } for box in Box.objects.filter(for_game | for_sheets).order_by(
        "group", "sort_order", "name")]

    attributes_in_groups = {}

    for attribute in attributes:
        attributes_in_groups.setdefault(attribute["group"],
                                        []).append(attribute)

    context = {
        "play_name": play.name,
        "characters": characters,
        "attributes": attributes,
        "attributes_in_groups": attributes_in_groups,
        "publish_key": os.environ["PUBNUB_PUBLISH"],
        "subscribe_key": os.environ["PUBNUB_SUBSCRIBE"],
        "user_id": str(uuid.uuid4()),
    }

    return render(request, "game.html", context=context)


@ensure_csrf_cookie
def edit_character(request):
    character_id = int(request.GET.get('character_id'))

    character = Character.objects.get(id=character_id)

    sheets = []
    left = top = max_height = 0

    for index in range(1, 10):
        sheet = getattr(character.playbook, f"sheet{index}")

        if not sheet: continue

        max_height = max(max_height, sheet.image_height)

        widgets = ""

        for box_position in BoxPosition.objects.filter(sheet=sheet):
            if box_position.box.kind == Box.Kind.TEXT_FIELD:
                value = get_value(character, box_position, "")

                widgets += f"""
                    <input style="{get_position(box_position, adjust_left=2, adjust_top=2)}; {get_font()}" value="{value}"
                        onblur="submitHandler(this.value, {character_id}, {box_position.id});">
                """
            elif box_position.box.kind == Box.Kind.NUMBER:
                value = get_value(character, box_position, 0)

                width = box_position.width
                absolute_100 = "position: absolute; width: 100%; height: 100%"
                all_center = "display: flex; justify-content: center; align-items: center; position: absolute"
                appearance = "cursor: default; font-size: 18;"
                full_size_center = f"{all_center}; width:100%; height:100%; {appearance}"
                select_events = f'onclick="showActions(event, {character_id}, {box_position.id});"'
                on_click_shared = f'''
                    onclick="incrementValue(this.parentElement, {character_id}, {box_position.id}
                '''
                increment_click = f'{on_click_shared}, 1);"'
                decrement_click = f'{on_click_shared}, -1);"'

                widgets += f"""
                    <div style="position: absolute; {get_position(box_position, adjust_left=2, adjust_top=1)};">
                        <button class="valueContainer" style="{absolute_100}; {get_font(32)};" {select_events}>
                            {value}
                        </button>
                        <button class="actions" style="left: 0; top: -{width}px; {absolute_100}; background-color: transparent; visibility: hidden;" {increment_click}>▲</button>
                        <button class="actions" style="left: 0; bottom: -{width}px; {absolute_100}; background-color: transparent; visibility: hidden" {decrement_click}>▼</button>
                        <!--<div style="{full_size_center};"
                                onclick="showRoller(event, {character_id}, {box_position.id});"
                            ></div>-->
                    </div>
                """
            elif box_position.box.kind == Box.Kind.CHECKBOX:
                always_checked = bool(box_position.box.meta) and box_position.box.meta.get("always_checked", False)
                value = get_value(character, box_position, always_checked)

                click = f'onclick="toggle(event, {character_id}, {box_position.id});"' if not always_checked else ""
                selection_visibility = "" if value else "visibility: hidden"
                style = "border: 1px solid black; background-color: white"
                inner = box_position.width - 2

                widgets += f"""
                    <div style="position: absolute; {get_position(box_position)}; {style}" {click}>
                        <div style="margin: 1px; width: {inner}px; height: {inner}px; background-color: grey;
                                    pointer-events: none; {selection_visibility};
                        ">
                        </div>
                    </div>
                """
            elif box_position.box.kind == Box.Kind.TEXT_BOX:
                value = get_value(character, box_position, "")
                change = f'onchange="submitHandler(this.value, {character_id}, {box_position.id});"'
                widgets += f"""
                    <textarea style="position: absolute; {get_position(box_position)};
                    resize: none; box-sizing: border-box; padding: 8px; border: none;" {change}
                    >{value}</textarea>
                """
            elif box_position.box.kind == Box.Kind.OVERLAY:
                widgets += f"""
                    <div style="position: absolute; {get_position(box_position)}; background-color: white;"></div>
                """
            elif box_position.box.kind == Box.Kind.CHECKABLE_TEXT_FIELD:
                value = get_value(character, box_position, {"state": False, "content": ""})
                click = f'onclick="toggleTextField(event, {character_id}, {box_position.id});"'
                change = f'onblur="updateCheckableTextField(event, {character_id}, {box_position.id});"'

                selection_visibility = "" if value['state'] else "visibility: hidden"
                style = "border: 1px solid black; background-color: white"

                width, height = default_size_by_kind[Box.Kind.CHECKBOX]
                inner = width - 2

                widgets += f"""
                    <div style="position: absolute; {get_position(box_position)}; background-color: white">
                        
                        <div style="position: absolute; top: 3px; width: {width}px; height: {height}px; {style}"
                            {click}>
                            <div style="margin: 1px; width: {inner}px; height: {inner}px; background-color: grey;
                                        pointer-events: none; {selection_visibility};
                            ">
                            </div>
                        </div>
                        
                        <input style="position: absolute; height: 100%; left: {width + 4}px; right: 0; {get_font()}"
                            value="{value['content']}" {change}>
                    </div>
                """

        sheets.append({
            "left": f"{left}pt",
            "top": f"{top}pt",
            "image_width": f"{sheet.image_width}pt",
            "image_height": f"{sheet.image_height}pt",
            "image_url": sheet.image.url,
            "widgets": mark_safe(widgets),
            "id": sheet.id,
        })
        if index % 3 == 0:
            top += max_height
            left = max_height = 0
        else:
            left += sheet.image_width

    context = {
        "sheets": sheets,
        "publish_key": os.environ["PUBNUB_PUBLISH"],
        "subscribe_key": os.environ["PUBNUB_SUBSCRIBE"],
        "user_id": str(uuid.uuid4()),
        "character_name": str(character),
    }

    return render(request, "playing.html", context)


def submit_value(request):
    data = json.loads(request.body)
    value = data.get("value")
    character_id = data.get("character_id")
    box_position_id = data.get("box_position_id")
    character = Character.objects.get(id=character_id)
    character.values[str(box_position_id)] = value
    character.save()

    return JsonResponse({"ok": True})


def report_roll_result(request):
    data = json.loads(request.body)
    character_id = data.get("character_id")
    box_position_id = data.get("box_position_id")
    roll_result = data.get("roll_result")
    character_name = str(Character.objects.get(id=character_id))
    attribute_name = BoxPosition.objects.get(id=box_position_id).box.name

    message = f"{character_name}\n{attribute_name}: {roll_result}"
    print(message)
    requests.post(os.environ["DISCORD_WEBHOOK"], data={"content": message})

    return JsonResponse({"ok": True})


def get_position(box_position, font_size=12, other_styles="", adjust_left=0, adjust_top=0):
    return f"""
    left: {box_position.left + adjust_left}px; top: {box_position.top + adjust_top}px;
    width: {box_position.width}px; height: {box_position.height}px;
    """


def get_font(font_size=12):
    return f"""
    font-family: Didot, 'Bodoni MT', 'Noto Serif Display', 'URW Palladio L', P052, Sylfaen, serif;
    font-weight: 600; font-size: {font_size}"
    """


def get_value(character, box_position, default_value):
    value = character.values.get(str(box_position.id))
    if value is None:
        character.values[str(box_position.id)] = default_value
        character.save()
        return default_value
    return value
