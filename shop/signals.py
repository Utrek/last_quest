from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Supplier

User = get_user_model()


@receiver(post_save, sender=User)
def create_supplier_profile(sender, instance, created, **kwargs):
    """
    Создает профиль поставщика при регистрации пользователя с типом 'supplier'
    """
    if created and instance.user_type == 'supplier' and not hasattr(instance, 'supplier_profile'):
        Supplier.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_existing_supplier_profiles(sender, instance, **kwargs):
    """
    Создает профиль поставщика для существующих пользователей с типом 'supplier'
    """
    if instance.user_type == 'supplier' and not hasattr(instance, 'supplier_profile'):
        Supplier.objects.get_or_create(user=instance)
