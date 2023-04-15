from enum import auto

from django.db import models
from pypdf import PdfReader


class Game(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Sheet(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    image = models.FileField(upload_to="sheet_images", null=True, blank=True)
    image_width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image_height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.game.name})"

    def save(self, **kwargs):
        if self.image and self.image.name.endswith("pdf"):
            reader = PdfReader(self.image.file)
            file_size = reader.pages[0].mediabox
            self.image_width = file_size.width
            self.image_height = file_size.height

        super().save(**kwargs)


class Box(models.Model):
    class Meta:
        verbose_name_plural = "boxes"
        ordering = ("group", "sort_order", "name")

    class Kind(models.TextChoices):
        TEXT_FIELD = "text_field"
        TEXT_BOX = "text_box"
        NUMBER = "number"
        CHECKBOX = "checkbox"
        MOVE = "move"
        OVERLAY = "overlay"
        CHECKABLE_TEXT_FIELD = "checkbox_and_text_field"
        DEFAULT_MOVE = "default_move"
        OPTIONAL_MOVE = "optional_move"
        LIST = "list"
        MANY_CHECKBOXES_AND_TEXT_FIELDS = "many_checkboxes_and_text_fields"
        CLEAR_BUTTON = "clear_button"

    name = models.CharField(max_length=200)
    group = models.CharField(max_length=50, null=True, blank=True)
    sort_order = models.IntegerField(null=True, blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    sheet = models.ForeignKey(Sheet, null=True, blank=True, on_delete=models.CASCADE)
    kind = models.CharField(max_length=50, choices=Kind.choices)
    meta = models.JSONField(null=True, blank=True)
    adjustable_width = models.BooleanField(default=False, null=True, blank=True)
    adjustable_height = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.group})"


class BoxPosition(models.Model):
    sheet = models.ForeignKey(Sheet, on_delete=models.CASCADE)
    box = models.ForeignKey(Box, on_delete=models.CASCADE)
    left = models.DecimalField(decimal_places=2, max_digits=10)
    top = models.DecimalField(decimal_places=2, max_digits=10)
    width = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    height = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)


class Playbook(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    sheet1 = models.ForeignKey(Sheet, null=True, blank=True, related_name="playbook1", on_delete=models.CASCADE)
    sheet2 = models.ForeignKey(Sheet, null=True, blank=True, related_name="playbook2", on_delete=models.CASCADE)
    sheet3 = models.ForeignKey(Sheet, null=True, blank=True, related_name="playbook3", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.game.name})"
