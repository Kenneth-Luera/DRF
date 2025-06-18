from .models import *
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username','password', 'email', 'first_name', 'last_name')

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class TaskAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAuditLog
        fields = ['id', 'action', 'user', 'timestamp', 'changes']

class NumeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Numero
        fields = '__all__'
