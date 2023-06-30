# Generated by Django 4.1.7 on 2023-06-30 16:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "create",
            "0001_squashed_0012_playbook_sheet4_playbook_sheet5_playbook_sheet6_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="box",
            name="kind",
            field=models.CharField(
                choices=[
                    ("text_field", "Text Field"),
                    ("text_box", "Text Box"),
                    ("number", "Number"),
                    ("checkbox", "Checkbox"),
                    ("move", "Move"),
                    ("overlay", "Overlay"),
                    ("checkbox_and_text_field", "Checkable Text Field"),
                    ("default_move", "Default Move"),
                    ("optional_move", "Optional Move"),
                    ("list", "List"),
                    (
                        "many_checkboxes_and_text_fields",
                        "Many Checkboxes And Text Fields",
                    ),
                    ("clear_button", "Clear Button"),
                    ("map_pin", "Map Pin"),
                ],
                max_length=50,
            ),
        ),
    ]
