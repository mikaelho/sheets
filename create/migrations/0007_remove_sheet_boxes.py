# Generated by Django 4.1.7 on 2023-04-03 11:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("create", "0006_sheet_image_height_sheet_image_width"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="sheet",
            name="boxes",
        ),
    ]
