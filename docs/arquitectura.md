# Documentación del Proyecto — creditos_api

---

## 1. Arquitectura del Proyecto

El proyecto tiene **dos capas de acceso** a los mismos datos:

```
creditos_api/
├── run.py                     ← punto de entrada
├── config.py                  ← configuración
├── requirements.txt
├── .env
└── app/
    ├── __init__.py            ← app factory (crea Flask, BD, registra blueprints)
    ├── models.py              ← modelo de base de datos
    ├── credits/               ← Blueprint: API REST (JSON)
    │   ├── __init__.py
    │   ├── routes.py
    │   └── schemas.py
    ├── web/                   ← Blueprint: Plataforma web (HTML)
    │   ├── __init__.py
    │   └── routes.py
    └── templates/
        ├── base.html
        ├── credits/
        │   ├── list.html
        │   ├── form.html
        │   └── detail.html
        └── auth/
            └── login.html
```

**App factory pattern:** Flask recomienda este patrón para crear la aplicación dentro de una función (`create_app()`), en lugar de hacerlo directamente al importar el módulo. Esto evita problemas de imports circulares y hace la app más fácil de configurar.

**Blueprint pattern:** Un Blueprint es un grupo de rutas relacionadas que se registra en la app. Este proyecto tiene dos:

- `credits` → rutas de la API REST en `/api/credits/`
- `web` → rutas de la plataforma visual en `/credits/`

Ambos blueprints acceden al **mismo modelo** (`Credit`) y a la **misma base de datos**. Son dos formas distintas de hacer lo mismo.

---

## 2. Configuraciones

### `.env`

Contiene variables de entorno que no deben ir en el código. La más importante:

```
DATABASE_URL=postgresql://usuario:password@localhost:5432/nombre_bd
SECRET_KEY=alguna-clave-secreta
```

### `config.py`

```python
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///creditos.db")
    SQLALCHEMY_ENGINE_OPTIONS = {"poolclass": NullPool}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
```

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave que Flask usa para firmar cookies y sesiones. Si no está en `.env`, usa `"dev-secret-key"` por defecto (solo para desarrollo). |
| `SQLALCHEMY_DATABASE_URI` | Cadena de conexión a la BD. Si no hay `.env`, usa SQLite local como fallback. |
| `NullPool` | Le dice a SQLAlchemy que no mantenga conexiones abiertas en pool. Útil con PostgreSQL en entornos donde las conexiones se cortan. |
| `SQLALCHEMY_TRACK_MODIFICATIONS = False` | Desactiva un sistema de eventos de SQLAlchemy que consume memoria y no se usa. |
| `WTF_CSRF_ENABLED = False` | Residual de una dependencia anterior, ya no tiene efecto. |

### `requirements.txt`

| Librería | Para qué sirve |
|---|---|
| `Flask` | Framework web principal |
| `Flask-SQLAlchemy` | Integración Flask + SQLAlchemy (ORM) |
| `marshmallow` | Validación y serialización de datos en la API |
| `python-dotenv` | Lee el archivo `.env` automáticamente |
| `Werkzeug` | Utilidades HTTP, incluido en Flask |
| `psycopg2-binary` | Driver que conecta Python con PostgreSQL |

---

## 3. Contenido de cada archivo

### `run.py`

```python
from app import create_app
app = create_app()
if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

Punto de entrada. Llama a `create_app()`, guarda la instancia en `app`, y arranca el servidor en el puerto 5000 con modo debug activado (muestra errores detallados y reinicia automáticamente al guardar cambios).

---

### `app/__init__.py`

```python
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    db.init_app(app)
    from app.credits import bp as credits_bp
    from app.web import bp as web_bp
    app.register_blueprint(credits_bp, url_prefix="/api/credits")
    app.register_blueprint(web_bp, url_prefix="/credits")
    with app.app_context():
        db.create_all()
    return app
```

- `db = SQLAlchemy()` — crea el objeto de base de datos **fuera** de la función, para que todos los módulos puedan importarlo sin necesitar la instancia de Flask todavía.
- `app.config.from_object("config.Config")` — carga todas las variables de `Config` en la configuración de Flask.
- `db.init_app(app)` — conecta el objeto `db` con la instancia real de Flask.
- Los imports de blueprints van **dentro** de la función para evitar imports circulares.
- `db.create_all()` — crea las tablas en la BD si no existen. Debe ejecutarse dentro de `app.app_context()`.

---

### `app/models.py`

```python
class Credit(db.Model):
    __tablename__ = "credits"
    id          = db.Column(db.Integer, primary_key=True)
    client_id   = db.Column(db.String(50), nullable=False)
    client_name = db.Column(db.String(120), nullable=False)
    amount      = db.Column(db.Float, nullable=False)
    interest    = db.Column(db.Float, nullable=False)
    term_months = db.Column(db.Integer, nullable=False)
    status      = db.Column(db.String(20), default="ACTIVO")
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | INTEGER | Clave primaria autoincremental |
| `client_id` | VARCHAR(50) | Identificador del cliente |
| `client_name` | VARCHAR(120) | Nombre del cliente |
| `amount` | FLOAT | Monto del crédito |
| `interest` | FLOAT | Tasa de interés (%) |
| `term_months` | INTEGER | Plazo en meses |
| `status` | VARCHAR(20) | ACTIVO, VENCIDO, o LIQUIDADO |
| `created_at` | TIMESTAMP | Fecha de creación (automática) |
| `updated_at` | TIMESTAMP | Fecha de última modificación (automática) |

**Notas importantes:**
- `nullable=False` — la columna no puede quedar vacía en la BD.
- `default=datetime.utcnow` sin paréntesis — se pasa la función como referencia para que SQLAlchemy la llame en el momento del insert, no al definir la clase.
- `onupdate=datetime.utcnow` — SQLAlchemy actualiza este campo automáticamente en cada UPDATE.

---

### `app/credits/schemas.py`

```python
class CreditSchema(Schema):
    id          = fields.Int(dump_only=True)
    client_id   = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    client_name = fields.Str(required=True, validate=validate.Length(min=2, max=120))
    amount      = fields.Float(required=True, validate=validate.Range(min=0.01))
    interest    = fields.Float(required=True, validate=validate.Range(min=0.0, max=100.0))
    term_months = fields.Int(required=True, validate=validate.Range(min=1))
    status      = fields.Str(load_default="ACTIVO")
    created_at  = fields.DateTime(dump_only=True, format="%Y-%m-%d %H:%M")
    updated_at  = fields.DateTime(dump_only=True, format="%Y-%m-%d %H:%M")

credit_schema  = CreditSchema()
credits_schema = CreditSchema(many=True)
```

El schema tiene dos responsabilidades:

**Deserializar — `load()`** convierte JSON entrante en un diccionario Python validado:

| Opción | Qué hace |
|---|---|
| `required=True` | El campo es obligatorio; si no viene, regresa error |
| `dump_only=True` | Solo de salida; se ignora si viene en el JSON de entrada |
| `load_default="ACTIVO"` | Si no se manda el campo, usa este valor por defecto |
| `validate.Length(min=2, max=120)` | Valida longitud de texto |
| `validate.Range(min=0.01)` | Valida que el número esté dentro del rango |

**Serializar — `dump()`** convierte un objeto `Credit` de SQLAlchemy en diccionario JSON:
- `format="%Y-%m-%d %H:%M"` — formatea la fecha como `"2026-06-01 16:00"`.

`credit_schema` — instancia para un solo objeto.
`credits_schema` — instancia para listas (`many=True`).

---

### `app/credits/routes.py` — API REST

Todas las funciones regresan JSON. Blueprint registrado en `/api/credits`.

| Función | Método | Ruta | Descripción |
|---|---|---|---|
| `list_credits` | GET | `/api/credits/` | Lista todos; acepta `?status=` como filtro |
| `create_credit` | POST | `/api/credits/` | Crea un crédito nuevo |
| `get_credit` | GET | `/api/credits/<id>` | Obtiene un crédito por ID |
| `update_credit` | PUT | `/api/credits/<id>` | Actualiza un crédito completo |
| `delete_credit` | DELETE | `/api/credits/<id>` | Elimina un crédito |

**Códigos de respuesta:**
- `200` — OK (lectura o actualización exitosa)
- `201` — Created (creación exitosa)
- `204` — No Content (eliminación exitosa)
- `404` — Not Found (ID no existe)
- `422` — Unprocessable Entity (validación fallida, incluye detalle del error)

---

### `app/web/routes.py` — Plataforma Web

Misma lógica de negocio que la API, pero trabaja con formularios HTML en lugar de JSON.

| Función | Método | Ruta | Descripción |
|---|---|---|---|
| `list_credits` | GET | `/credits/` | Lista todos; acepta `?status=` como filtro |
| `new_credit` | GET | `/credits/new` | Muestra formulario vacío |
| `create_credit` | POST | `/credits/new` | Crea crédito desde formulario |
| `detail_credit` | GET | `/credits/<id>` | Vista de detalle |
| `edit_credit` | GET | `/credits/<id>/edit` | Muestra formulario pre-llenado |
| `update_credit` | POST | `/credits/<id>/edit` | Actualiza desde formulario |
| `delete_credit` | POST | `/credits/<id>/delete` | Elimina (usa POST porque HTML no soporta DELETE) |

Diferencias clave con la API:
- Lee datos con `request.form.get()` en lugar de `request.get_json()`
- Usa `render_template()` para devolver HTML
- Usa `flash()` + `redirect()` en lugar de respuestas JSON
- No pasa por Marshmallow (la validación la hace el HTML con `required` y `type="number"`)

---

## 4. Funcionamiento del CRUD y Base de Datos

### Cómo funciona SQLAlchemy

SQLAlchemy actúa como intermediario entre Python y PostgreSQL. Nunca se escribe SQL directamente — se trabaja con objetos Python y SQLAlchemy los traduce a consultas SQL.

**Sesión (`db.session`):** Es como una canasta de cambios pendientes. Cualquier operación (agregar, modificar, borrar) queda en la sesión hasta que se llama `commit()`. Si algo falla antes del commit, los cambios no se guardan.

---

### Flujo completo de cada operación

#### CREATE — Insertar

```
JSON entrante
  → credit_schema.load()  valida campos y tipos
  → dict Python validado
  → Credit(**dict)         crea objeto en memoria
  → db.session.add()       registra en la sesión
  → db.session.commit()    ejecuta INSERT en PostgreSQL
  → credit_schema.dump()   convierte objeto a JSON
  → respuesta 201
```

#### READ — Leer

```
Credit.query.all()
  → SELECT * FROM credits

Credit.query.filter_by(status="ACTIVO").all()
  → SELECT * FROM credits WHERE status = 'ACTIVO'

Credit.query.get_or_404(id)
  → SELECT * FROM credits WHERE id = ?
  → 404 automático si no hay resultado

  → credit_schema.dump()   convierte a JSON
  → respuesta 200
```

#### UPDATE — Actualizar

```
Credit.query.get_or_404(id)   busca el objeto existente
  → credit_schema.load()       valida el JSON nuevo
  → setattr(credit, k, v)      modifica atributos en memoria
  → db.session.commit()        ejecuta UPDATE en PostgreSQL
    (SQLAlchemy detecta automáticamente qué campos cambiaron)
  → credit_schema.dump()       convierte a JSON
  → respuesta 200
```

#### DELETE — Borrar

```
Credit.query.get_or_404(id)   busca el objeto
  → db.session.delete()        marca para eliminar
  → db.session.commit()        ejecuta DELETE en PostgreSQL
  → respuesta 204 sin cuerpo
```

---

### Creación automática de tablas

Al arrancar la app, `db.create_all()` revisa si la tabla `credits` existe en PostgreSQL. Si no existe, la crea con todas las columnas definidas en el modelo. Si ya existe, no hace nada ni borra datos.

---

### URLs disponibles

| URL | Qué es |
|---|---|
| `http://localhost:5000/credits/` | Plataforma web visual |
| `http://localhost:5000/api/credits/` | API REST (responde JSON) |
