import os
import uuid

from django.db.models import Model
from django.db.models.signals import post_save
from django.dispatch import receiver
from pubnub.exceptions import PubNubException

from create.models import Playbook
from play.models import Case
from play.models import Character
from play.models import Location
from play.models import Person
from play.models import Play

from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

from play.views import serialize_instance


pnconfig = PNConfiguration()
pnconfig.subscribe_key =  os.environ["PUBNUB_SUBSCRIBE"]
pnconfig.publish_key = os.environ["PUBNUB_PUBLISH"]
pnconfig.user_id = str(uuid.uuid4())
pubnub = PubNub(pnconfig)


@receiver(post_save, sender=Play)
@receiver(post_save, sender=Character)
@receiver(post_save, sender=Playbook)
@receiver(post_save, sender=Case)
@receiver(post_save, sender=Location)
@receiver(post_save, sender=Person)
def process_save(sender: Model, created, instance, **kwargs):
    node_id = f"{sender._meta.label_lower}-{instance.id}"
    payload = serialize_instance(sender, instance)
    message = { "id": node_id, "content": payload}

    pubnub.publish().channel("updates").message(message).sync()

    if sender == Character:
        pubnub.publish().channel("characters").message(message).sync()
