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
from rest_framework.views import APIView
import time



class registerUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    pagination_class = PageNumberPagination
    pagination_class.page_size = 10
    permission_classes = [AllowAny]


    def create(self, request, *args, **kwargs):
        tiempo = request.data.get('due_date')
        if tiempo < timezone.now():
            return Response({"error": "La fecha de vencimiento no puede ser anterior a la fecha actual."}, status=status.HTTP_400_BAD_REQUEST)
        elif request.user.is_staff == 0:
            if request.data.get('priority') == 'CRITICAL':
                return Response({"error": "No tienes permiso para crear tareas con prioridad crítica."}, status=status.HTTP_403_FORBIDDEN)
            serializer = TaskSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.data.get('priority') == 'URGENT':
            max_date = timezone.now().date() + timedelta(days=3)
            if tiempo > max_date:
                return Response(
                    {"error": "Las tareas URGENT no pueden tener una fecha de vencimiento mayor a 3 días desde hoy."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        user_task_count = Task.objects.filter(created_by=request.user).count()
        if user_task_count >= 10:
            return Response({"error": "Solo puedes tener un máximo de 10 tareas activas."},status=status.HTTP_400_BAD_REQUEST)

        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            if request.user.is_staff == 0:
                user = request.user.id
                queryset = Task.objects.filter(created_by=user)
            elif request.user.is_staff == 1:
                queryset = Task.objects.all()
            else:
                return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = TaskSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = TaskSerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    
    def patch(self, request, pk, *args, **kwargs):
            task = get_object_or_404(Task, pk=pk)
            if request.user != task.created_by and request.user != task.assigned_to:
                return Response({"error": "No tienes permiso para editar esta tarea."}, status=status.HTTP_403_FORBIDDEN)
            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user.id
            queryset = Task.objects.filter(created_by=user)
            serializer = TaskSerializer(queryset, many=True)
            return Response(serializer.data)

class AuditoriaViewSets(viewsets.ModelViewSet):
    queryset = Auditoria.objects.all()
    serializer_class = AuditoriaSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination

    def list(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        task_id = request.query_params.get('task_id')

        if not user_id:
            return Response({"error": "El parámetro 'user_id' es obligatorio."}, status=400)

        queryset = Auditoria.objects.filter(cambio_user_id=user_id)
        if task_id:
            queryset = queryset.filter(task_assigned_id=task_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TaskMetricsView(APIView):
    permission_classes = [AllowAny]

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
from datetime import datetime
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
                due_date = datetime.strptime(row['due_date'], '%b %d, %Y').date()
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

class ExportTaskCSVView(APIView):
    permission_classes = [IsAuthenticated]

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