# Generated by Django 4.1.7 on 2023-04-26 17:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("play", "0011_location_sort_order_person_sort_order"),
    ]

    operations = [
        migrations.AddField(
            model_name="case",
            name="open",
            field=models.BooleanField(default=False, null=True),
        ),
    ]
