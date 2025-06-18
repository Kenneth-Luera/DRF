from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Task, TaskAuditLog
from .thread_local import get_current_user

@receiver(post_save, sender=Task)
def audit_task_save(sender, instance, created, **kwargs):
    user = get_current_user()
    action = 'CREATE' if created else 'UPDATE'
    
    TaskAuditLog.objects.create(
        action=action,
        task=instance,
        user=user,
        changes=str(instance.__dict__)
    )

@receiver(post_delete, sender=Task)
def audit_task_delete(sender, instance, **kwargs):
    user = get_current_user()

    TaskAuditLog.objects.create(
        action='DELETE',
        task=instance,
        user=user,
        changes=str(instance.__dict__)
    )
