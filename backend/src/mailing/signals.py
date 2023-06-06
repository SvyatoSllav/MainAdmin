from functools import partial
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Mailing
from .task import send_newsletter_task
from django.db import transaction


@receiver(post_save, sender=Mailing)
def send_newsletter(sender, instance, created, **kwargs):
    transaction.on_commit(partial(send_newsletter_task.delay, instance.id))
        
