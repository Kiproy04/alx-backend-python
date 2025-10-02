from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory, User


@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    if created:  
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if instance.id:  
        try:
            old_message = Message.objects.get(id=instance.id)
        except Message.DoesNotExist:
            return

        if old_message.content != instance.content:
            MessageHistory.objects.create(
                message=old_message,
                old_content=old_message.content
            )
            instance.edited = True


@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()
    Notification.objects.filter(user=instance).delete()