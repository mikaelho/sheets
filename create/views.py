from django.http import JsonResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe

from create.models import Box
from create.models import BoxPosition
from create.models import Sheet


def edit_boxes(request):
    sheet_id = int(request.GET.get('sheet_id'))

    sheet = Sheet.objects.get(id=sheet_id)

    box_positions = mark_safe("".join(
        create_box_html(box_position)
        for box_position in BoxPosition.objects.filter(sheet=sheet).all()
    ))

    context = {
        "sheet_id": sheet.id,
        "sheet_url": sheet.image.url,
        "image_width": f"{sheet.image_width}pt",
        "image_height": f"{sheet.image_height}pt",
        "box_list": mark_safe(format_unordered_list_of_boxes(sheet)),
        "box_positions": box_positions,
    }
    return render(request, "sheet_edit.html", context)


def create_initial_box_position(request):
    sheet_id = int(request.GET.get("sheet_id"))
    box_id = int(request.GET.get("box_id"))

    sheet = Sheet.objects.get(id=sheet_id)
    box = Box.objects.get(id=box_id)

    attributes = dict(box.__dict__)
    attributes.pop("_state")

    width, height = default_size_by_kind[box.kind]
    box_position = BoxPosition.objects.create(sheet=sheet, box=box, left=100, top=100, width=width, height=height)

    return JsonResponse({
        "element_id": f"box{box_position.id}",
        "adjust_width": box_position.box.adjustable_width,
        "adjust_height": box_position.box.adjustable_height,
        "box_html": create_box_html(box_position),
    })


def update_box_position(request):
    box_position_id = int(request.GET.get("box_id"))
    left = request.GET.get("left")
    top = request.GET.get("top")
    width = request.GET.get("width")
    height = request.GET.get("height")

    BoxPosition.objects.filter(id=box_position_id).update(left=left, top=top, width=width, height=height)

    return JsonResponse({"ok": True})


def format_unordered_list_of_boxes(sheet):
    box_dict = get_all_boxes(sheet)

    return (
        f'<div style="padding: 8px;">{"".join(format_group(group_name, boxes) for group_name, boxes in box_dict.items())}</div>'
    )


def format_group(group_name, boxes):
    return f'<div style="position:relative; margin-top: 8px;"><strong>{group_name}</strong><div style="position:relative; padding: 8px;">{get_box_list(boxes)}</div></div>'


def get_box_list(boxes):
    return "".join(get_box(box) for box in boxes)


def get_box(box):
    return f"""
    <div style="position:relative; padding: 4px; margin: 4px; border: 1px solid #759FEA; user-select: none;"
        onclick="getNewBox({box.id});"
        class="elementSelect"
    >{box.name}</div>
    """


def get_all_boxes(sheet):
    # Get all
    box_list = list(Box.objects.filter(game=sheet.game, sheet__isnull=True))
    box_list.extend(list(Box.objects.filter(sheet=sheet)))

    # Group by group
    boxes = {}
    for box in box_list:
        boxes.setdefault(box.group, []).append(box)

    # Sort by name in groups
    group: list
    for group in boxes.values():
        group.sort(key=lambda box: box.name)

    return boxes


default_size_by_kind = {
    Box.Kind.TEXT_FIELD: (200, 20),
    Box.Kind.NUMBER: (35, 35),
    Box.Kind.TEXT_BOX: (200, 200),
    Box.Kind.CHECKBOX: (12, 12),
    Box.Kind.DEFAULT_MOVE: (12, 12),
    Box.Kind.OPTIONAL_MOVE: (12, 12),
    Box.Kind.CHECKABLE_TEXT_FIELD: (210, 20),
    Box.Kind.OVERLAY: (200, 200),
    Box.Kind.MOVE: (210, 20),
}


def create_box_html(box_position):
    widther = ""
    heighter = ""
    if box_position.box.adjustable_width:
        widther = """
            <div class="widther"
                style="width: 20px; height: 100%; right: 0; cursor: e-resize;"
                onpointerdown="widthDownHandler(event)" onpointerup="widthUpHandler(event)"
            ></div>
            """
    if box_position.box.adjustable_height:
        heighter = """
            <div class="heighter" style="width: 100%; height: 20px; bottom: 0; cursor: s-resize;"
                onpointerdown="heightDownHandler(event)" onpointerup="heightUpHandler(event)"
            ></div>
        """

    return f"""
    <div id="box{box_position.id}" class="placeholder" 
        style="
            left: {box_position.left}px; top: {box_position.top}px;
            width: {box_position.width}px; height: {box_position.height}px;
        "
        onpointerdown="downHandler(event)" onpointerup="upHandler(event)"
        >
        <div class="boxName">{box_position.box.name}</div> 
        {widther}{heighter}
    </div>
    """
