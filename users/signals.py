from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import ResourceCategory

@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    if sender.name == "resources":
        ResourceCategory.create_default_categories()
