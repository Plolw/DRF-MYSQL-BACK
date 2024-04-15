# GUÍA RUTAS API

 Todas las rutas van precedidas de http://127.0.0.1:8000/
## Tokens:
```
POST http://127.0.0.1:800/token/
{"username": "", "password": ""}

Returns: {"token": "", "refresh": ""}

----------------------------------------------------------------
POST http://127.0.0.1:800/token/refresh/
{"refresh": ""}

Returns: {"token": "", "refresh": ""}
```

## User auth:

```
POST http://127.0.0.1:8000/register/
{
    "username": "", "last_name": "", "email": "", "password": "", "is_professor": ""
}

Returns: {}

----------------------------------------------------------------
POST http://127.0.0.1:8000/logout/
{"refresh_token": ""}

Returns: {}

----------------------------------------------------------------
GET http://127.0.0.1:8000/user/

Returns: 
{
    "user": {
        "id": "",
        "username": "",
        "first_name": "",
        "last_name": "",
        "email": "",
        "password": "" (contraseña encriptada por seguridad)
    }
    "is_professor": ""
}
```

### A partir de este punto (y incluyendo el POST a logout y GET a user) todas las requests tendrán que tener un token en ellas para que sean autorizadas. El formato de la request será en todas:
```
POST http://127.0.0.1:8000/...
Authorization: bearer <token aquí>
{...(todos los datos mandados en el request)}
```

### Proyectos:
```
POST http://127.0.0.1:8000/projects/
{"name": "", "description": ""}


----------------------------------------------------------------
GET http://127.0.0.1:8000/projects/<id de proyecto que se quiera obtener>

Returns: (una lista de proyectos)
{
    [
    {
        "id": "",
        "name": "",
        "description": "",
        "collaborators": [(lista usuarios)],
        "teachers": [(lista usuarios)],
        "creator": {(usuario)}
    }
    ]
}


----------------------------------------------------------------
DELETE http://127.0.0.1:8000/projects/<id de proyecto que se quiera eliminar>/


----------------------------------------------------------------
PUT http://127.0.0.1:8000/projects/<id proyecto>/teachers/
(añade al usuario que haga la request a los profesores del proyecto especificado si es un profesor)
```

### Tareas

```
POST http://127.0.0.1:8000/projects/<id proyecto>/tasks/
{
    "name": "",
    "description": "",
    "start_date": "",
    "story_points": "",
    "state": "",
    "estimated_hours": ""
} (solo funciona si eres un colaborador del proyecto)


----------------------------------------------------------------
GET http://127.0.0.1:8000/projects/<id proyecto>/tasks/

Returns: [ (lista de tareas del proyecto si colaboras en el)
    {
    "id": "",
    "name": "",
    "description": "",
    "start_date": "",
    "finish_date": "",
    "story_points": "",
    "state": "",
    "estimated_hours": "",
    "total_hours": "",
    "creator": {(usuario)},
    "collaborators": [(lista usuarios)]
    }
]


----------------------------------------------------------------
PUT http://127.0.0.1:8000/projects/<id tarea>/tasks/
{"state": "(AN, CU, RE, DE)"} (acepta cualquiera de estas opciones) (solo se acepta si eres un colaborador del proyecto)


----------------------------------------------------------------
DELETE http://127.0.0.1:8000/projects/<id tarea>/tasks/
(elimina la tarea especificada solo si eres un colaborador del proyecto)


----------------------------------------------------------------
PUT http://127.0.0.1:8000/projects/tasks/<id tarea>/collaborators/
(añade al usuario que haga la request a los colaboradores de la tarea)
```

### Puntos:
```
GET http://127.0.0.1:8000/projects/<id proyecto>/points/

Returns: [ (lista de cada usuario y los puntos que tiene en el proyecto)
    {
        "username": "",
        "project_id": "",
        "points": ""
    }
]
```

### Invitaciones:
```
POST http://127.0.0.1:8000/invitations/<id proyecto>/
{"username": "(nombre de la persona que deseas invitar ya sea un alumno o un profesor)"}


----------------------------------------------------------------
GET http://127.0.0.1:8000/invitations/

Returns: [ (lista de invitaciones)
    {
        "id": "",
        "sender": {(usuario)},
        "receiver": {(usuario)},
        "project": {(proyecto)}
        "state": ""
    }
]


----------------------------------------------------------------
PUT http://127.0.0.1:8000/invitations/<id proyecto>/
{"state": "(elegir entre AC(aceptada), WA(esperando), DE(rechazada))"}

(Si se acepta se añadirá al usuario a los colaboradores del proyecto)
```

