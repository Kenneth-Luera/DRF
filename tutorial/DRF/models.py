from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now



class User(AbstractUser):
    user_permissions = models.ManyToManyField('auth.Permission',related_name='custom_user_permissions',blank=True,)
    # aqui agregar opciones adicionales del usuario
    is_active = models.BooleanField(default=True)
    password = models.CharField(max_length=128, help_text='Required. 128 characters or fewer. Alphanumeric characters and @/./+/-/_ only.', verbose_name='password')

    def __str__(self):
        return self.username
    

    

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateTimeField()
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


class TaskAuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    ]

    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(default=now)
    changes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_action_display()} - Task: {self.task.title} - By: {self.user}"

class Numero(models.Model):
    numeroPagination = models.IntegerField(default=10)
    def __str__(self):
        return str(self.numeroPagination)