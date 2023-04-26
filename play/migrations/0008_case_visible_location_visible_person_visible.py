# Generated by Django 4.1.7 on 2023-04-25 16:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("play", "0007_alter_casefiles_case_files_subtitle"),
    ]

    operations = [
        migrations.AddField(
            model_name="case",
            name="visible",
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name="location",
            name="visible",
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name="person",
            name="visible",
            field=models.BooleanField(default=False, null=True),
        ),
    ]