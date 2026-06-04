# Guía Completa — Sistema de Créditos

---

## ¿Qué es este proyecto?

Una aplicación web fullstack para gestionar créditos. Permite crear, consultar, editar y eliminar créditos, además de visualizar estadísticas con gráficas interactivas.

Tiene dos caras:
- **Interfaz web** → para que el usuario navegue con el browser
- **API REST** → para que otras aplicaciones consuman los datos en formato JSON

---

## Stack tecnológico

| Tecnología | Versión | Para qué se usa |
|---|---|---|
| Python | 3.x | Lenguaje principal del servidor |
| Flask | 3.1.2 | Framework web, maneja rutas y peticiones HTTP |
| Flask-SQLAlchemy | 3.1.1 | Conecta Python con la base de datos |
| SQLite | — | Base de datos, se guarda en `creditos.db` |
| Marshmallow | 3.14.1 | Valida y serializa datos de la API |
| Jinja2 | — | Motor de templates, mete datos Python en HTML |
| Bootstrap | 5.3.0 | Estilos y componentes visuales |
| Chart.js | 4.4.0 | Dibuja las gráficas interactivas en el browser |
| python-dotenv | 1.2.1 | Lee variables de entorno desde un archivo `.env` |
| Werkzeug | 3.1.3 | Dependencia interna de Flask |

---

## Estructura de carpetas

```
creditos_api/
│
├── run.py                    ← Arranca el servidor en puerto 5000
├── config.py                 ← Configuración general de la app
├── requirements.txt          ← Dependencias Python
│
└── app/
    ├── __init__.py           ← Fábrica: construye y conecta toda la app
    ├── models.py             ← Clase Credit (tabla de la base de datos)
    │
    ├── credits/              ← Blueprint API REST  →  prefijo /api/credits
    │   ├── __init__.py       ← Registra el blueprint "credits"
    │   ├── routes.py         ← Endpoints que devuelven JSON
    │   └── schemas.py        ← Validación de datos con Marshmallow
    │
    ├── web/                  ← Blueprint Web  →  prefijo /credits
    │   ├── __init__.py       ← Registra el blueprint "web"
    │   └── routes.py         ← Rutas que devuelven páginas HTML
    │
    ├── templates/            ← Archivos HTML (Jinja2)
    │   ├── base.html         ← Layout base: navbar + estructura
    │   └── credits/
    │       ├── list.html     ← Tabla de todos los créditos
    │       ├── form.html     ← Formulario crear / editar
    │       ├── detail.html   ← Detalle de un crédito
    │       └── charts.html   ← Página de gráficas
    │
    └── static/               ← Archivos que el browser descarga directamente
        ├── css/style.css     ← Estilos personalizados
        └── js/main.js        ← JavaScript general
```

---

## Arquitectura general

```
┌─────────────────────────────────────────────────────┐
│                     BROWSER                         │
│                                                     │
│   HTML + CSS + JavaScript + Chart.js                │
│   Templates: list, form, detail, charts             │
└───────────────────────┬─────────────────────────────┘
                        │  HTTP (peticiones y respuestas)
┌───────────────────────▼─────────────────────────────┐
│                  FLASK (Servidor)                   │
│                                                     │
│   Blueprint "web"          Blueprint "credits"      │
│   /credits/...             /api/credits/...         │
│   devuelve HTML            devuelve JSON            │
└───────────────────────┬─────────────────────────────┘
                        │  SQLAlchemy (ORM)
┌───────────────────────▼─────────────────────────────┐
│                 BASE DE DATOS                       │
│                                                     │
│   SQLite → archivo creditos.db                      │
│   Tabla: credits                                    │
└─────────────────────────────────────────────────────┘
```

---

## Archivos explicados uno por uno

---

### `run.py`

```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
```

El punto de entrada. Solo importa `create_app`, construye la app y la arranca.
Se ejecuta con `python run.py` y levanta el servidor en `http://localhost:5000`.

---

### `config.py`

```python
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///creditos.db")
    SQLALCHEMY_ENGINE_OPTIONS = {"poolclass": NullPool}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
```

Una clase con variables de configuración. Flask la lee al arrancar.

| Variable | Qué hace |
|---|---|
| `SECRET_KEY` | Llave para firmar sesiones y cookies |
| `SQLALCHEMY_DATABASE_URI` | Dirección de la base de datos |
| `NullPool` | Evita problemas de conexiones colgadas |
| `TRACK_MODIFICATIONS` | Desactiva una función que consume memoria innecesaria |

`os.getenv("X", "valor_default")` significa: busca la variable de entorno `X`, si no existe usa el valor default. Así en producción puedes configurar todo sin tocar el código.

---

### `app/__init__.py`

```python
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")   # carga la configuración
    db.init_app(app)                          # conecta la base de datos

    from app.credits import bp as credits_bp
    from app.web import bp as web_bp

    app.register_blueprint(credits_bp, url_prefix="/api/credits")
    app.register_blueprint(web_bp,     url_prefix="/credits")

    with app.app_context():
        db.create_all()    # crea las tablas si no existen

    return app
```

La fábrica de la app. Cada vez que se llama, construye la app desde cero y registra los dos blueprints con sus prefijos de URL. `db` se declara aquí afuera para que todos los módulos puedan importarlo.

---

### `app/models.py`

```python
class Credit(db.Model):
    __tablename__ = "credits"

    id          = db.Column(db.Integer,     primary_key=True)
    client_id   = db.Column(db.String(50),  nullable=False, unique=True)
    client_name = db.Column(db.String(120), nullable=False)
    amount      = db.Column(db.Float,       nullable=False)
    interest    = db.Column(db.Float,       nullable=False)
    term_months = db.Column(db.Integer,     nullable=False)
    status      = db.Column(db.String(20),  default="ACTIVO")
    created_at  = db.Column(db.DateTime,    default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)
```

La clase que representa la tabla `credits` en la base de datos. Cada atributo es una columna.

| Campo | Tipo | Restricción |
|---|---|---|
| `id` | Entero | Clave primaria, se genera automáticamente |
| `client_id` | Texto (50) | Obligatorio, no puede repetirse |
| `client_name` | Texto (120) | Obligatorio |
| `amount` | Decimal | Obligatorio |
| `interest` | Decimal | Obligatorio |
| `term_months` | Entero | Obligatorio |
| `status` | Texto | Por defecto `"ACTIVO"` |
| `created_at` | Fecha/hora | Se llena solo al crear |
| `updated_at` | Fecha/hora | Se actualiza solo al editar |

SQLAlchemy traduce automáticamente entre objetos Python y filas en la BD:

```
Fila en la BD                   Objeto Python
─────────────────               ──────────────────────
id=1, amount=5000   →           credit.id = 1
status="ACTIVO"     →           credit.amount = 5000
                                credit.status = "ACTIVO"
```

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

credit_schema  = CreditSchema()          # para un solo crédito
credits_schema = CreditSchema(many=True) # para una lista de créditos
```

El guardia de la API. Antes de guardar cualquier dato valida que todo esté correcto.

| Término | Qué significa |
|---|---|
| `required=True` | El campo es obligatorio, si falta → error 422 |
| `dump_only=True` | Solo se incluye al leer (output), nunca al escribir (input) |
| `load_default` | Valor por defecto si no viene en el JSON |
| `validate.Length` | El texto debe tener entre X y Y caracteres |
| `validate.Range` | El número debe estar entre min y max |

---

## Los Blueprints

Un Blueprint es un módulo de rutas independiente. Esta app tiene dos con propósitos distintos:

```
Blueprint "credits"  →  /api/credits/...  →  responde JSON  →  para código/APIs
Blueprint "web"      →  /credits/...      →  responde HTML  →  para el browser
```

---

### `app/credits/routes.py` — API REST

#### `list_credits` — Listar créditos
```python
@bp.get("/")
def list_credits():
    status = request.args.get("status")
    query = Credit.query
    if status:
        query = query.filter_by(status=status)
    credits = query.order_by(Credit.created_at.desc()).all()
    return jsonify(credits_schema.dump(credits))
```
Acepta un parámetro opcional `?status=ACTIVO` para filtrar. Devuelve la lista en JSON ordenada por fecha descendente.

---

#### `create_credit` — Crear crédito
```python
@bp.post("/")
def create_credit():
    try:
        data = credit_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({"errors": e.messages}), 422

    credit = Credit(**data)
    db.session.add(credit)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"errors": {"client_id": ["Ya existe"]}}), 409

    return jsonify(credit_schema.dump(credit)), 201
```
Valida con Marshmallow → si falla devuelve 422 → si el `client_id` ya existe devuelve 409 → si todo está bien devuelve el crédito creado con código 201.

---

#### `get_credit` — Obtener uno
```python
@bp.get("/<int:id>")
def get_credit(id):
    credit = Credit.query.get_or_404(id)
    return jsonify(credit_schema.dump(credit))
```
`get_or_404` devuelve el crédito si existe, o automáticamente responde con error 404 si no.

---

#### `update_credit` — Actualizar
```python
@bp.put("/<int:id>")
def update_credit(id):
    credit = Credit.query.get_or_404(id)
    data = credit_schema.load(request.get_json())
    for key, value in data.items():
        setattr(credit, key, value)
    db.session.commit()
    return jsonify(credit_schema.dump(credit))
```
`setattr(credit, key, value)` actualiza cada campo dinámicamente sin tener que escribir cada campo a mano.

---

#### `delete_credit` — Eliminar
```python
@bp.delete("/<int:id>")
def delete_credit(id):
    credit = Credit.query.get_or_404(id)
    db.session.delete(credit)
    db.session.commit()
    return "", 204
```
Código 204 significa "éxito, sin contenido que devolver".

---

#### `monthly_stats` — Datos para gráfica de barras
```python
@bp.get("/stats/monthly")
def monthly_stats():
    from collections import defaultdict
    credits = Credit.query.all()
    counts = defaultdict(int)
    for c in credits:
        counts[c.created_at.strftime("%Y-%m")] += 1
    result = [{"month": k, "total": v} for k, v in sorted(counts.items())]
    return jsonify(result)
```
Trae todos los créditos, los agrupa por mes (`"2025-06"`) contando cuántos hay en cada uno, y devuelve la lista ordenada cronológicamente.

**Ejemplo de respuesta:**
```json
[
  { "month": "2025-01", "total": 3 },
  { "month": "2025-06", "total": 7 }
]
```

---

#### `amount_ranges` — Datos para pie chart
```python
@bp.get("/stats/amount-ranges")
def amount_ranges():
    ranges = [
        {"label": "$0 - $5,000",      "min": 0,     "max": 5000},
        {"label": "$5,001 - $20,000",  "min": 5001,  "max": 20000},
        {"label": "$20,001 - $50,000", "min": 20001, "max": 50000},
        {"label": "$50,001+",          "min": 50001, "max": float("inf")},
    ]
    credits = Credit.query.with_entities(Credit.amount).all()
    for r in ranges:
        r["total"] = sum(1 for (a,) in credits if r["min"] <= a <= r["max"])
    return jsonify([{"label": r["label"], "total": r["total"]} for r in ranges])
```
Solo trae los montos de la BD (más eficiente que traer todo), cuenta cuántos caen en cada rango y devuelve el resultado.

**Ejemplo de respuesta:**
```json
[
  { "label": "$0 - $5,000",     "total": 4 },
  { "label": "$5,001 - $20,000", "total": 9 }
]
```

---

### `app/web/routes.py` — Interfaz Web

Todas las funciones usan `render_template()` en vez de `jsonify()`, lo que significa que devuelven una página HTML completa al browser.

| Función | Método | URL | Qué hace |
|---|---|---|---|
| `list_credits` | GET | `/credits/` | Muestra la tabla de créditos |
| `new_credit` | GET | `/credits/new` | Muestra el formulario vacío |
| `create_credit` | POST | `/credits/new` | Guarda el nuevo crédito |
| `detail_credit` | GET | `/credits/<id>` | Muestra detalle de uno |
| `edit_credit` | GET | `/credits/<id>/edit` | Formulario pre-llenado |
| `update_credit` | POST | `/credits/<id>/edit` | Guarda los cambios |
| `delete_credit` | POST | `/credits/<id>/delete` | Elimina y redirige |
| `charts` | GET | `/credits/charts` | Página de gráficas |

**Ejemplo de flujo web al crear un crédito:**
```
1. Usuario llena el formulario y hace clic en Guardar
2. POST /credits/new  →  create_credit()
3. Lee los campos con request.form.get(...)
4. Crea objeto Credit y lo guarda en la BD
5. flash("Crédito creado correctamente", "success")
6. redirect → /credits/  (regresa a la lista)
```

---

## Los Templates

### `base.html` — El esqueleto compartido

Todos los templates heredan de este. Define la estructura visual común.

```
┌────────────────────────────────────┐
│  <nav> navbar con links            │  ← siempre visible
├────────────────────────────────────┤
│  mensajes flash (si los hay)       │  ← notificaciones temporales
├────────────────────────────────────┤
│  {% block content %}               │  ← cada página mete su contenido aquí
│  {% endblock %}                    │
├────────────────────────────────────┤
│  <script> Bootstrap                │  ← siempre al final
│  <script> main.js                  │
└────────────────────────────────────┘
```

Para heredarlo, cada template empieza con:
```html
{% extends "base.html" %}
{% block content %}
  ... contenido de la página ...
{% endblock %}
```

---

### `list.html` — La tabla

Recibe la variable `credits` desde Python y la recorre con Jinja2:
```html
{% for credit in credits %}
<tr>
    <td>{{ credit.client_name }}</td>
    <td>{{ credit.amount }}</td>
    <td>{{ credit.status }}</td>
</tr>
{% endfor %}
```

---

### `form.html` — El formulario

Se reutiliza para crear Y editar. Si recibe `credit=None` → formulario vacío. Si recibe un objeto `credit` → lo pre-llena en los inputs.

---

### `charts.html` — Las gráficas

No recibe datos de Python. El JavaScript hace sus propios `fetch()` para obtener los datos después de que el HTML cargó.

---

## Las Gráficas — Flujo completo

### ¿Cómo se comunican Python y Chart.js?

```
PYTHON                           JAVASCRIPT
──────                           ──────────
Consulta la BD              ←→   fetch(url)
Agrupa los datos                 recibe JSON
Devuelve JSON               →    new Chart(canvas, datos)
                                 Chart.js dibuja
```

Python nunca dibuja nada. Solo calcula y manda JSON.
JavaScript nunca toca la base de datos. Solo dibuja.

---

### Paso a paso desde que abres `/credits/charts`

```
① Browser pide GET /credits/charts
            ↓
② Flask ejecuta charts() → render_template("charts.html")
   Devuelve HTML con dos <canvas> vacíos, sin datos
            ↓
③ Browser muestra el HTML y ejecuta el JavaScript
            ↓
④ JavaScript lanza dos fetch() al mismo tiempo:
   ├── GET /api/credits/stats/monthly
   └── GET /api/credits/stats/amount-ranges
            ↓
⑤ Flask ejecuta monthly_stats() y amount_ranges()
   Consultan la BD, cuentan, agrupan, devuelven JSON
            ↓
⑥ JavaScript recibe los JSON
   Extrae labels y valores
            ↓
⑦ new Chart() dibuja cada gráfica en su <canvas>
   El usuario ve las gráficas en pantalla
```

---

### Gráfica 1 — Barras: créditos por mes

**Endpoint:** `GET /api/credits/stats/monthly`

El JavaScript en `charts.html`:
```javascript
fetch("{{ url_for('credits.monthly_stats') }}")
    .then(r => r.json())
    .then(data => {
        const labels = data.map(d => d.month)   // ["2025-01", "2025-06"]
        const totals = data.map(d => d.total)   // [3, 7]

        new Chart(document.getElementById("monthlyChart"), {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{ data: totals, backgroundColor: "rgba(13,110,253,0.7)" }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 1, precision: 0 } }
                }
            }
        })
    })
    .catch(err => { /* muestra error en pantalla */ })
```

---

### Gráfica 2 — Pie: distribución por rango de monto

**Endpoint:** `GET /api/credits/stats/amount-ranges`

```javascript
fetch("{{ url_for('credits.amount_ranges') }}")
    .then(r => r.json())
    .then(data => {
        new Chart(document.getElementById("amountChart"), {
            type: "pie",
            data: {
                labels: data.map(d => d.label),
                datasets: [{
                    data: data.map(d => d.total),
                    backgroundColor: ["azul", "verde", "amarillo", "rojo"]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: "bottom" } }
            }
        })
    })
```

---

### `static/js/main.js`

```javascript
document.querySelectorAll(".alert").forEach(el => {
    setTimeout(() => el.classList.remove("show"), 4000);
});
```

Auto-oculta los mensajes flash (notificaciones verdes/rojas) después de 4 segundos. Se ejecuta en todas las páginas porque está incluido en `base.html`.

---

## Todas las URLs disponibles

### Interfaz web

| URL | Qué muestra |
|---|---|
| `http://localhost:5000/credits/` | Lista de créditos |
| `http://localhost:5000/credits/new` | Formulario nuevo crédito |
| `http://localhost:5000/credits/<id>` | Detalle de un crédito |
| `http://localhost:5000/credits/<id>/edit` | Formulario editar |
| `http://localhost:5000/credits/charts` | Gráficas |

### API REST (devuelve JSON)

| URL | Método | Qué hace |
|---|---|---|
| `/api/credits/` | GET | Lista todos los créditos |
| `/api/credits/` | POST | Crea un crédito nuevo |
| `/api/credits/<id>` | GET | Obtiene uno por ID |
| `/api/credits/<id>` | PUT | Actualiza uno |
| `/api/credits/<id>` | DELETE | Elimina uno |
| `/api/credits/stats/monthly` | GET | Totales por mes (gráfica barras) |
| `/api/credits/stats/amount-ranges` | GET | Distribución por monto (pie chart) |

---

## Cómo correr el proyecto

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Arrancar el servidor
python run.py

# 3. Abrir en el browser
http://localhost:5000/credits/
```

La base de datos `creditos.db` se crea automáticamente la primera vez.

---

## Diagrama final de la arquitectura

```
                        BROWSER
             ┌──────────────────────────────┐
             │  list.html / form.html       │
             │  detail.html / charts.html   │
             │                              │
             │  Chart.js (gráficas)         │
             │  Bootstrap (estilos)         │
             │  main.js (alerts)            │
             └──────────┬───────────────────┘
                        │ HTTP
             ┌──────────▼───────────────────┐
             │         FLASK                │
             │                              │
             │  Blueprint web               │
             │  /credits/ → HTML            │
             │                              │
             │  Blueprint credits           │
             │  /api/credits/ → JSON        │
             └──────────┬───────────────────┘
                        │ SQLAlchemy ORM
             ┌──────────▼───────────────────┐
             │  models.py → class Credit    │
             └──────────┬───────────────────┘
                        │
             ┌──────────▼───────────────────┐
             │  creditos.db (SQLite)        │
             │  tabla: credits              │
             └──────────────────────────────┘
```
