Projecto de asignacion de tareas

Se solicita poder generar usuarios con permisos diferentes tal como:
- User
- Administrador
  
Creacion de tareas y asignacion de las mismas con diferentes estados y urgencias tal como

Estados:
- PENDING
- IN_PROGRESS
- COMPLETED

Urgencias:
- LOW
- MEDIUM
- HIGH
- CRITICAL
- URGENTE

Implementar un registro de auditoria por usuario

El sistema puede exportar e importar archivos tipo CSV apuntando a la base de datos


Instalar dependencias

    pip install -r requirements.txt

Se recomienda hacer uso de MySQL usado desde Laragon o algun gestor de datos diferente al que viene por defecto (SQLite3)

TECNOLOGIAS UTILIZADAS
- Python
- Django / DRF
- MySQL -> Laragon
- Rabbitmq
