from django.core.management import BaseCommand
from django.db import transaction

from create.models import BoxPosition
from create.models import Sheet


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("source", type=int)
        parser.add_argument("target", type=int)

    @transaction.atomic()
    def handle(self, *args, **options):
        source = Sheet.objects.get(id=options["source"])
        target = Sheet.objects.get(id=options["target"])

        for field in BoxPosition.objects.filter(sheet=source, box__sheet__isnull=True):
            BoxPosition.objects.get_or_create(
                sheet=target,
                box=field.box,
                left=field.left,
                top=field.top,
                width=field.width,
                height=field.height,
            )
