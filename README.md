DRF API Project
Este es un proyecto de API RESTful construido con Django REST Framework (DRF). Proporciona una base sólida para desarrollar APIs escalables y mantenibles, siguiendo buenas prácticas y patrones de diseño comunes.

Características principales
Autenticación JWT: Soporte para autenticación basada en tokens usando Simple JWT.

Swagger/OpenAPI: Documentación interactiva de la API usando drf-yasg.

Configuración modular: Estructura de proyecto organizada en apps separadas.


Requisitos previos
Python 3.11

Docker (opcional, si deseas usar contenedores)

PostgreSQL (recomendado para producción)

Configuración inicial
Clona el repositorio:

bash

    git clone https://github.com/Kenneth-Luera/DRF.git
cd DRF
Crea un entorno virtual (recomendado):

bash
venv\Scripts\activate
Instala las dependencias:

bash

    pip install -r requirements.txt
    
Configura las variables de entorno:

Copia el archivo .env.example a .env y ajusta los valores según tu entorno.

Aplica las migraciones:

bash

    python manage.py migrate
Crea un superusuario (opcional):

bash

    python manage.py createsuperuser
Inicia el servidor de desarrollo:

bash

    python manage.py runserver


Accede a la API:

La API estará disponible en http://localhost:8000

Estructura del proyecto

        DRF
        |   .gitignore
        |   db.sqlite3
        |   estructura.txt
        |   manage.py
        |   README.md
        |   requirements.txt
        |
        +---tutorial
            |  api.http
            |  asgi.py
            |  settings.py
            |  urls.py
            |  wsgi.py
            |   __init__.py
            |  
            +---DRF
                  |  admin.py
                  |  apps.py
                  |  models.py
                  |  receive.py
                  |  send.py
                  |  serializers.py
                  |  tareas_convertidas.csv
                  |  tests.py
                  |  urls.py
                  |  views.py
                  |  __init__.py
                  
Documentación de la API
La documentación interactiva está disponible en las siguientes rutas:

Swagger UI: /swagger/

-  http://127.0.0.1:8000/api/api/docs/redoc/

ReDoc: /redoc/

-  http://127.0.0.1:8000/api/api/docs/swagger/


Contribución
Si deseas contribuir a este proyecto:

Haz un fork del repositorio

Crea una rama para tu feature (git checkout -b feature/nueva-funcionalidad)

Haz commit de tus cambios (git commit -am 'Añade nueva funcionalidad')

Haz push a la rama (git push origin feature/nueva-funcionalidad)

Abre un Pull Request

Licencia
Este proyecto está bajo la licencia MIT. Ver el archivo LICENSE para más detalles.

FUNCIONALIDADES REQUERIDAS DEL NEGOCIO


1. Prioridad de Tareas
Campo priority: Opciones disponibles – LOW, MEDIUM, HIGH, CRITICAL, URGENTE.

Validaciones:

Solo usuarios con rol admin pueden crear tareas con prioridad CRITICAL.

Un usuario no puede tener más de 3 tareas CRITICAL activas simultáneamente.


2. Etiquetas (Tags) y Categorías
Modelo Tag con relación ManyToMany hacia Task.

Reglas:

Una tarea puede tener como máximo 5 etiquetas.

Si una tarea tiene la etiqueta "URGENTE", su due_date no debe ser mayor a 3 días desde su created_at.


3. Historial de Cambios (Auditoría)
Modelo TaskHistory que registra:

Cambios en status, assigned_to y priority.

Usuario que realizó el cambio (updated_by) y el timestamp.

Endpoint:

GET /api/tasks/<id>/history/ – Solo accesible por el creador o un admin.


4. Límites de Asignación
Un usuario no puede tener más de 10 tareas con estado IN_PROGRESS.

Validación:

Si se excede el límite al asignar una nueva tarea, retornar error 429 Too Many Requests.


5. Notificaciones Automáticas
Al cambiar el estado de una tarea a COMPLETED:

Se envía un email al usuario created_by (simulación con Celery o tarea asíncrona).

Si el due_date está a menos de 24 horas y la tarea no está completada:

Enviar notificación por websocket o email (bonus: usar django-channels).


6. Reportes
Endpoint:

GET /api/tasks/metrics/ (solo para admins).

Reporte incluye:

Cantidad de tareas completadas vs. pendientes por usuario.

Promedio de tiempo de completación agrupado por prioridad.


7. Validaciones Avanzadas
Si una tarea es marcada como COMPLETED:

El campo completed_at se autocompleta con la fecha y hora actual.

No se permite revertir una tarea a PENDING si han pasado más de 7 días desde su completación.


8. Integración Externa (Bonus)
Endpoint:

POST /api/tasks/import/ que acepta un archivo CSV para carga masiva de tareas.

Validaciones:

El CSV debe contener máximo 100 registros por solicitud.


Puntos Clave a Evaluar

- Manejo de estados complejos: Validación de transiciones de status y priority.

- Optimización de consultas: Uso de annotate y aggregate en reportes.

- Seguridad: Control de roles para acceso y operaciones sensibles (como prioridades CRITICAL).
