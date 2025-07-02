# vendor/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Processor, Graphic, Storage, Product


@receiver(post_save, sender=Processor)
@receiver(post_save, sender=Graphic)
@receiver(post_save, sender=Storage)
def update_product_scores_on_component_save(sender, instance, **kwargs):
    """
    This signal triggers whenever a Processor, Graphic, or Storage
    instance is saved. It finds all Products using that component and
    updates their denormalized score fields.
    """
    if sender == Processor:
        # Find all products using this processor and update their cpu_score
        Product.objects.filter(processor=instance).update(cpu_score=instance.score)
        print(
            f"Signal: Updated cpu_score for products using Processor ID {instance.id}"
        )

    elif sender == Graphic:
        # Find all products using this graphic card and update their gpu_score
        Product.objects.filter(graphic=instance).update(gpu_score=instance.score)
        print(f"Signal: Updated gpu_score for products using Graphic ID {instance.id}")

    elif sender == Storage:
        # Find all products using this storage and update their storage_score
        Product.objects.filter(storage=instance).update(storage_score=instance.score)
        print(
            f"Signal: Updated storage_score for products using Storage ID {instance.id}"
        )
