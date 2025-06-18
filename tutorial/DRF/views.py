from datetime import timedelta
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny 
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination

from django.views.generic import DeleteView
from auditlog.mixins import LogAccessMixin
from auditlog.models import LogEntry

from rest_framework.views import APIView
from datetime import datetime
from datetime import date
from django.core.mail import send_mail
import datetime



class registerUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class TaskAuditLogView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, pk):
        if request.user.is_authenticated:
            if request.user.is_staff == 1:    
                task = get_object_or_404(Task, pk=pk)
                logs = TaskAuditLog.objects.filter(task=task).order_by('-timestamp')
                serializer = TaskAuditLogSerializer(logs, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No tienes permiso para ver los registros de auditoría."}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"error": "No estas autenticado."}, status=status.HTTP_401_UNAUTHORIZED)        


from django_filters.rest_framework import DjangoFilterBackend

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    pagination_class = PageNumberPagination
    pagination_class.page_size = 10
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'priority', 'assigned_to', 'created_by', 'created_at']


    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff == 0:
                user = request.user.id
                queseryset = Task.objects.filter(created_by=user , assigned_to=user)
            elif request.user.is_staff == 1:
                queseryset = Task.objects.all()
        else:
            return Response({"error": "No estas autenticado."}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = TaskSerializer(queseryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        tiempo = request.data.get('due_date')
        fecha_hoy = date.today()
        fecha_date = datetime.datetime.strptime(tiempo, "%Y-%m-%dT%H:%M")
        fecha_datetime = datetime.datetime.combine(fecha_hoy, datetime.time(0, 0))
        if request.user.is_authenticated:
                if fecha_date > fecha_datetime:
                    return Response({"error": "La fecha de vencimiento no puede ser anterior a la fecha actual."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    serializers = TaskSerializer(data=request.data)
                    if serializers.is_valid():
                        task = serializers.save(created_by=request.user)
                        serializers.save(created_by=request.user)
                        asunto = f"Nueva tarea asignada: {task.title}"
                        mensaje = f"Hola {task.assigned_to.username},\nTienes una nueva tarea asignada:\nTítulo: {task.title}\nDescripción: {task.description}\nFecha de vencimiento: {task.due_date}\nPrioridad: {task.priority}\nSaludos,\nEquipo de Tareas"
                        from_email = 'kennethpl30.5@gmail.com'
                        destinatario = task.assigned_to.email
                        try:
                            send_mail(asunto, mensaje, from_email, [destinatario])
                            return Response({"mensaje": "Tarea creada y correo enviado correctamente."}, status=status.HTTP_201_CREATED)
                        except Exception as e:
                            return Response({"error": f"Error al enviar el correo: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "No estas autenticado."}, status=status.HTTP_401_UNAUTHORIZED)

    def patch(self, request, pk, *args, **kwargs):
            task = get_object_or_404(Task, pk=pk)
            if request.user != task.created_by and request.user != task.assigned_to:
                return Response({"error": "No tienes permiso para editar esta tarea."}, status=status.HTTP_403_FORBIDDEN)
            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"error": "No estas autenticado."}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            pk = kwargs.get('pk')
            if not pk:
                return Response({"error": "ID de tarea no proporcionado."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                task = Task.objects.get(pk=pk)
                if request.user != task.created_by and request.user != task.assigned_to:
                    return Response({"error": "No tienes permiso para eliminar esta tarea."}, status=status.HTTP_403_FORBIDDEN)
                task.delete()
                return Response({"mensaje": "Tarea eliminada correctamente."}, status=status.HTTP_204_NO_CONTENT)
            except Task.DoesNotExist:
                return Response({"error": "Tarea no encontrada."}, status=status.HTTP_404_NOT_FOUND)

class TaskMetricsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        tasks = Task.objects.filter(status='COMPLETED')
        total_time = 0
        count = 0
        for task in tasks:
            if hasattr(task, 'created_at') and hasattr(task, 'updated_at') and task.created_at and task.updated_at:
                delta = (task.updated_at - task.created_at).total_seconds()
                total_time += delta
                count += 1
        promedio_minutos = (total_time / count) / 60 if count else 0
        return Response({
            "tareas_completadas": count,
            "promedio_minutos": promedio_minutos
        })

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import csv
from io import TextIOWrapper
from .models import Task

from pika import BlockingConnection, ConnectionParameters

class ImportTaskCSVView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        csv_file = request.FILES.get('file')
        if not csv_file:
            return Response({"error": "No se envió ningún archivo."}, status=400)

        data = TextIOWrapper(csv_file.file, encoding='utf-8')
        lines = list(data)
        lines[0] = lines[0].replace('\ufeff', '').strip() + '\n'
        reader = csv.DictReader(lines, delimiter=';', skipinitialspace=True)
        tasks_created = 0
        errores = []
        for i, row in enumerate(reader):
            if i >= 100:
                break
            row = {k.strip(): v for k, v in row.items() if k}
            columnas = ['title', 'description', 'assigned_to_id', 'created_by_id', 'due_date', 'status', 'priority']
            if not all(k in row for k in columnas):
                errores.append(f"Fila {i+2}: Faltan columnas requeridas.")
                return Response({"error": "Corrige lo requerido para enviar."},status=status.HTTP_400_BAD_REQUEST)
            try:
                due_date = datetime.strptime(row['due_date'], "%d/%m/%Y").date()
                Task.objects.create(
                    title=row['title'],
                    description=row['description'],
                    assigned_to_id=row['assigned_to_id'] or None,
                    created_by_id=row['created_by_id'],
                    due_date=due_date,
                    status=row['status'],
                    priority=row['priority']
                )
                tasks_created += 1
            except Exception as e:
                errores.append(f"Fila {i+2}: {str(e)}")

        msg = {"mensaje": f"{tasks_created} tareas importadas correctamente."}
        if errores:
            msg["errores"] = errores
        return Response(msg)    
import time

class ExportTaskCSVView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, format=None):
        time.sleep(15)
        tasks = Task.objects.all()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tasks.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Title', 'Description', 'Assigned To', 'Created By', 'Due Date', 'Status', 'Priority'])
        for task in tasks:
            writer.writerow([task.id, task.title, task.description, task.assigned_to_id, task.created_by_id, task.due_date, task.status, task.priority])
        return response