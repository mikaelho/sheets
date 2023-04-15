from django.db import models

from create.models import BoxPosition
from create.models import Game
from create.models import Playbook
from create.models import Sheet


class Play(models.Model):
    name = models.CharField(max_length=50)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

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

    values = models.JSONField(default=dict, null=True, blank=True)

    def __str__(self):
        name_box = BoxPosition.objects.filter(box__name="Name", sheet=self.playbook.sheet1).first()
        return name_box and self.values.get(str(name_box.id)) or "No name"
