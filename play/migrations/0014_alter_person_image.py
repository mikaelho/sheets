# Generated by Django 4.1.7 on 2023-04-27 17:38

from django.db import migrations
import paste_image.fields


class Migration(migrations.Migration):
    dependencies = [
        ("play", "0013_case_player_notes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="person",
            name="image",
            field=paste_image.fields.PasteImageField(
                blank=True, null=True, upload_to="people_images"
            ),
        ),
    ]
