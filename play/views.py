import io
import json
import os
import uuid

from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.db.models import F

import play
import requests
from create.models import Box
from create.models import BoxPosition
from create.models import Playbook
from create.views import default_size_by_kind
from django.core.files import File
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import ensure_csrf_cookie
from markdown import markdown
from play.admin import open_character
from play.image_manipulation import add_noise
from play.image_manipulation import convert_sepia
from play.image_manipulation import open_image
from play.models import Case
from play.models import CaseFiles
from play.models import Character
from play.models import Location
from play.models import Person
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
        "image_link": character.image and character.image.url or "",
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
                    <div id="box{box_position.id}" style="position: absolute; {get_position(box_position, adjust_left=2, adjust_top=1)};">
                        <button class="valueContainer" style="{absolute_100}; {get_font(32)};" {select_events}>
                            {value}
                        </button>
                        <button class="actions" style="left: 0; top: -{width}px; {absolute_100}; background-color: transparent; visibility: hidden;" {increment_click}>▲</button>
                        <button class="actions" style="left: 0; bottom: -{width}px; {absolute_100}; background-color: transparent; visibility: hidden" {decrement_click}>▼</button>
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
            elif box_position.box.kind == Box.Kind.MAP_PIN:
                if (meta := box_position.box.meta) and meta.get("hidden"):
                    continue
                widgets += f"""
                    <div class="pin" style="position: absolute; left: {box_position.left+8}px; top: {box_position.top-16}px;">
                    </div>
                    <div style="
                        position: absolute; left: {box_position.left+14}px; top: {box_position.top+20}px;
                        transform: translate(-50%, 0);
                        text-shadow: white 1px 1px, white -1px -1px, white 1px 1px 5px;
                        font-family: IngeborgHeavy; font-size: 18px;
                    ">
                    {box_position.box.name}
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
    character = Character.objects.get(id=character_id)
    character_name = str(character)
    attribute_name = BoxPosition.objects.get(id=box_position_id).box.name

    message = f"{character_name}\n{attribute_name}: {roll_result}"
    print(message)

    if discord_webhook_url := character.play.discord_webhook_url or os.environ.get("DISCORD_WEBHOOK"):
        requests.post(discord_webhook_url, data={"content": message})

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


@ensure_csrf_cookie
def case_files(request):
    play_id = int(request.GET.get("play_id"))
    play = Play.objects.get(id=play_id)
    files = CaseFiles.objects.get(play_id=play_id)

    cases = [
        format_case(case)
        for case in Case.objects.filter(play_id=play_id, visible=True).order_by("-sort_order")
    ]

    context = {
        "title": f"{files.case_files_are_called.upper()} OF {play.name.upper()}",
        "subtitle": files.case_files_subtitle,
        "cases": cases,
        "publish_key": os.environ["PUBNUB_PUBLISH"],
        "subscribe_key": os.environ["PUBNUB_SUBSCRIBE"],
        "user_id": str(uuid.uuid4()),
    }

    return render(request, "cases.html", context)


def format_case(case: Case):
    people = Person.objects.filter(case=case, visible=True).order_by(F("sort_order").asc(nulls_last=True))
    locations = Location.objects.filter(case=case, visible=True).order_by(F("sort_order").asc(nulls_last=True))

    if case.image:
        title = f'<img src="{case.image.url}" style="height: 70px; fit-image:contain;">'
    else:
        title = f'<span class="caseTitle">{case.name.upper()}</span>'

    people_html = f"""
        <h3 class="sectionTitle">Persons of Note</h3>
        <div class="gridWrap">
            {"".join(f'<div class="card">{format_person(person)}</div>' for person in people)}
        </div>
    """ if people.count() else ""

    location_html = f"""
        <h3 class="sectionTitle">Places of Interest</h3>
        <div class="gridWrap">
            {"".join(f'<div class="card">{format_location(location)}</div>' for location in locations)}
        </div>
    """ if locations.count() else ""

    return mark_safe(f"""
    <details {'open="true"' if case.open else ""}>
        <summary>{title}</summary>
        <h3 class="sectionTitle">Notes</h3>
        {format_notes(case, "c")}

        {people_html}
        
        {location_html}
    </details>
    """)


def format_person(person: Person):
    image = f"""
    <div style="background: radial-gradient(transparent 50%, white), url('{ person.image.url }');
                 background-size: cover; width: 150px; height: 225px; margin: auto;">
    </div>
    """ if person.image else ""

    return f"""
    {image}
    <p><strong>{person.name}</strong><br/>{person.description}</p>
    <span style="font-style: italic;">Notes:</span>
    {format_notes(person, "p")}
    """


def format_location(location: Location):
    return f"""
        <p><strong>{location.name}</strong><br/>{location.description}</p>
        <p><span style="font-style: italic;">Notes:</span></p>
        {format_notes(location, "l")}
        """


def format_notes(obj, obj_type):
    return f"""
    <div id="{obj_type}{obj.id}">
        <div class="notes asHTML" onclick="startEditNote(this);">{markdown(obj.player_notes or "")}
        </div>
        <div class="notes asMarkdown" contenteditable onblur="stopEditNote(this);"
         style="display: none; white-space: pre-wrap;">{obj.player_notes or ""}</div>
    </div>
    """

def update_notes(request):
    data = json.loads(request.body)
    note_id = data.get("noteId")
    value = data.get("value")

    model_map = {"p": Person, "l": Location, "c": Case}
    obj = model_map[note_id[0]].objects.get(id=int(note_id[1:]))
    obj.player_notes = value
    obj.save()

    return JsonResponse({"content": format_notes(obj, note_id[0])})


def modify_and_save_image(request, type_id, obj_id):
    type_obj = getattr(play.models, type_id)
    obj = type_obj.objects.get(id=obj_id)

    image_data = request.body
    original = open_image(io.BytesIO(image_data))
    sepia_image = convert_sepia(original)
    add_noise(sepia_image)

    image_bytes = io.BytesIO()
    sepia_image.save(image_bytes, "png")
    obj.image = File(image_bytes, name=f"{type_id}-{obj_id}.png")
    obj.save()

    return JsonResponse({"ok": True})





def graph_view(request):
    play_id = int(request.GET.get("play_id"))
    graph_data = get_graph("play.play", play_id)

    context = {"graph_json": mark_safe(json.dumps(graph_data))}

    return render(request, "graph.html", context)


graph_relationships = {
    Case: ["play", "person_set", "location_set"],
    Character: ["play", "playbook"],
    Location: ["case"],
    Person: ["case"],
    Play: ["case_set", "character_set"],
    Playbook: [],
    # Case: ["play"],
    # Character: ["play", "playbook"],
    # Location: ["case"],
    # Person: ["case"],
    # Play: ["case_set", "character_set"],
    # Playbook: [],

}


def get_graph(model_name, instance_id):
    seen = set()
    to_process = [(model_name, instance_id)]
    nodes = {}
    edges = []

    while next_to_process := to_process.pop(0) if len(to_process) else False:
        model_name, instance_id = next_to_process
        node_id = f"{model_name}-{instance_id}"
        seen.add((model_name, instance_id))
        model_content_type = ContentType.objects.get_by_natural_key(*(model_name.split(".")))
        model = model_content_type.model_class()
        instance = model.objects.get(id=instance_id)

        for attribute in graph_relationships[model]:
            value = getattr(instance, attribute)
            if hasattr(value, "all") and callable(value.all):
                value = value.all()
            else:
                value = [value]
            for related_instance in value:
                related_content_type = ContentType.objects.get_for_model(related_instance)
                related_model_name = f"{related_content_type.app_label}.{related_content_type.model}"
                edges.append([node_id, f"{related_model_name}-{related_instance.pk}"])
                consider_processing(related_instance, to_process, seen)

        node = serialize_instance(model, instance_id)
        if model is Character:
            node["fields"]["name"] = str(instance)
        nodes[node_id] = node

    return {"nodes": nodes, "edges": edges}

def consider_processing(instance, to_process, seen):
    content_type = ContentType.objects.get_for_model(instance)
    natural_key = f"{content_type.app_label}.{content_type.model}"
    if not (natural_key, instance.id) in seen:
        to_process.append((natural_key, instance.id))


def serialize_instance(model, instance_id):
    return json.loads(serializers.serialize("jsonl", model.objects.filter(pk=instance_id)))
