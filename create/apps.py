from django.apps import AppConfig


class CreateConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "create"

    def ready(self):
        from create.models import Box
        from create.models import Game

        the_between_default_sheet_boxes = [
            dict(name="Name", kind=Box.Kind.TEXT_FIELD, group="0 - Basics", adjustable_width=True),
            dict(name="Look", kind=Box.Kind.TEXT_FIELD, group="0 - Basics", adjustable_width=True),
            dict(name="Vice", kind=Box.Kind.TEXT_FIELD, group="0 - Basics", adjustable_width=True),
            dict(name="Vitality", kind=Box.Kind.NUMBER, group="1 - Abilities"),
            dict(name="Composure", kind=Box.Kind.NUMBER, group="1 - Abilities"),
            dict(name="Reason", kind=Box.Kind.NUMBER, group="1 - Abilities"),
            dict(name="Presence", kind=Box.Kind.NUMBER, group="1 - Abilities"),
            dict(name="Sensitivity", kind=Box.Kind.NUMBER, group="1 - Abilities"),
            dict(name="Condition", kind=Box.Kind.TEXT_FIELD, group="2 - Conditions", adjustable_width=True),
            dict(name="XP", kind=Box.Kind.CHECKBOX, group="3 - XP"),
            dict(name="Increase an ability modifier by 1 (max +3)", kind=Box.Kind.CHECKBOX, group="4 - Advancements"),
            dict(name="Write a custom move for your character.", kind=Box.Kind.CHECKBOX, group="4 - Advancements"),
            dict(name="Item", kind=Box.Kind.CHECKABLE_TEXT_FIELD, group="5 - Personal Quarters", adjustable_width=True),
        ]

        # game, _ = Game.objects.get_or_create(name="The Between")
        # for box in the_between_default_sheet_boxes:
        #     defaults = dict(box)
        #     defaults.pop("name")
        #     Box.objects.get_or_create(game=game, name=box["name"], defaults=defaults)
