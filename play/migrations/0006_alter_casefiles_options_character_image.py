# Generated by Django 4.1.7 on 2023-04-25 06:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("play", "0005_case_person_location_casefiles"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="casefiles",
            options={"verbose_name_plural": "case files"},
        ),
        migrations.AddField(
            model_name="character",
            name="image",
            field=models.FileField(blank=True, null=True, upload_to="people_images"),
        ),
    ]