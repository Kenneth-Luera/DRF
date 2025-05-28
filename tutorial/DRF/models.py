from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    groups = models.ManyToManyField('auth.Group',related_name='custom_user_groups',blank=True,)
    user_permissions = models.ManyToManyField('auth.Permission',related_name='custom_user_permissions',blank=True,)
    # aqui agregar opciones adicionales del usuario
    def __str__(self):
        return self.username
    
class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateField()
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
        ('URGENT', 'Urgent'),
    ]
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='LOW')

    def __str__(self):
        return self.title

class Auditoria(models.Model):
    cambio_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'auditoria')
    task_assigned = models.ForeignKey(Task, on_delete=models.CASCADE, related_name= 'cambios_task')

    def __str__(self):
        return self.cambio_user

class Numero(models.Model):
    numeroPagination = models.IntegerField(default=10)
    def __str__(self):
        return str(self.numeroPagination)