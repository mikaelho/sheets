# Generated by Django 4.1.7 on 2023-04-18 18:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("create", "0011_alter_box_kind"),
    ]

    operations = [
        migrations.AddField(
            model_name="playbook",
            name="sheet4",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="playbook4",
                to="create.sheet",
            ),
        ),
        migrations.AddField(
            model_name="playbook",
            name="sheet5",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="playbook5",
                to="create.sheet",
            ),
        ),
        migrations.AddField(
            model_name="playbook",
            name="sheet6",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="playbook6",
                to="create.sheet",
            ),
        ),
        migrations.AddField(
            model_name="playbook",
            name="sheet7",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="playbook7",
                to="create.sheet",
            ),
        ),
        migrations.AddField(
            model_name="playbook",
            name="sheet8",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="playbook8",
                to="create.sheet",
            ),
        ),
        migrations.AddField(
            model_name="playbook",
            name="sheet9",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="playbook9",
                to="create.sheet",
            ),
        ),
    ]
