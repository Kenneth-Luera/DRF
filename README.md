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

        Pracitca2
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
