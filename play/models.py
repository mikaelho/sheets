from create.models import BoxPosition
from create.models import Game
from create.models import Playbook
from django.db import models


class Play(models.Model):
    name = models.CharField(max_length=50)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    discord_webhook_url = models.CharField(max_length=200, blank=True, null=True)
    gm_notes = models.TextField(null=True, blank=True)
    attachment = models.FileField(upload_to="attachments", null=True, blank=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Character(models.Model):
    play = models.ForeignKey(Play, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    playbook = models.ForeignKey(Playbook, on_delete=models.CASCADE)
    image = models.FileField(upload_to="people_images", null=True, blank=True)
    values = models.JSONField(default=dict, null=True, blank=True)

    def __str__(self):
        name_box = BoxPosition.objects.filter(box__name="Name", sheet=self.playbook.sheet1).first()
        return name_box and self.values.get(str(name_box.id)) or "No name"


class CaseFiles(models.Model):
    class Meta:
        verbose_name_plural = "case files"

    play = models.OneToOneField(Play, on_delete=models.CASCADE)
    case_files_are_called = models.CharField(default="Case Files", max_length=50)
    case_files_subtitle = models.CharField(max_length=1024, null=True, blank=True)
    cases_are_called = models.CharField(default="Case", max_length=50, null=True, blank=True)
    people_are_called = models.CharField(default="Persons of Interest", max_length=50, null=True, blank=True)
    locations_are_called = models.CharField(default="Places of Note", max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.case_files_are_called} for {self.play.name}"


class Case(models.Model):
    name = models.CharField(max_length=50)
    sort_order = models.PositiveIntegerField(null=True, blank=True)
    play = models.ForeignKey(Play, on_delete=models.CASCADE)
    image = models.FileField(upload_to="people_images", null=True, blank=True)
    visible = models.BooleanField(default=False, null=True)
    open = models.BooleanField(default=False, null=True)
    player_notes = models.TextField(null=True, blank=True)
    gm_notes = models.TextField(null=True, blank=True)
    attachment = models.FileField(upload_to="attachments", null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.play.name})"


class Person(models.Model):
    name = models.CharField(max_length=50)
    sort_order = models.PositiveIntegerField(null=True, blank=True)
    visible = models.BooleanField(default=False, null=True)
    image = models.FileField(upload_to="people_images", null=True, blank=True)
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    player_notes = models.TextField(null=True, blank=True)
    gm_notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.case.name})"


class Location(models.Model):
    name = models.CharField(max_length=50)
    sort_order = models.PositiveIntegerField(null=True, blank=True)
    visible = models.BooleanField(default=False, null=True)
    image = models.FileField(upload_to="people_images", null=True, blank=True)
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    player_notes = models.TextField(null=True, blank=True)
    gm_notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.case.name})"
