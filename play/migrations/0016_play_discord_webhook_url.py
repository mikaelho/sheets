# Generated by Django 4.1.7 on 2023-06-29 15:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("play", "0001_squashed_0015_alter_person_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="play",
            name="discord_webhook_url",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
