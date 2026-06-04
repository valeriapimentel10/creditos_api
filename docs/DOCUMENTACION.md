# Sistema de Créditos — Documentación del Proyecto

## ¿Qué es este proyecto?

Una aplicación web para gestionar créditos. Permite crear, consultar, editar y eliminar créditos, y visualizar estadísticas mediante gráficas interactivas.

Está construida con **Python + Flask** en el servidor y **HTML + JavaScript** en el browser.

---

## Tecnologías utilizadas

| Tecnología | Para qué se usa |
|---|---|
| Python 3 | Lenguaje principal del servidor |
| Flask | Framework web que maneja las rutas y peticiones HTTP |
| SQLAlchemy | Conecta Python con la base de datos sin escribir SQL directo |
| SQLite | Base de datos, se guarda en un archivo `creditos.db` |
| Marshmallow | Valida que los datos que llegan por la API estén bien formados |
| Jinja2 | Motor de templates — mete datos de Python en el HTML |
| Bootstrap 5 | Estilos y componentes visuales (navbar, cards, botones) |
| Chart.js | Librería JavaScript que dibuja las gráficas en el browser |

---

## Estructura de carpetas

```
creditos_api/
│
├── run.py                   ← Punto de entrada, arranca el servidor
├── config.py                ← Configuración general (base de datos, clave secreta)
├── requirements.txt         ← Lista de dependencias Python
│
└── app/
    ├── __init__.py          ← Fábrica de la app, registra los blueprints
    ├── models.py            ← Modelo de la base de datos (clase Credit)
    │
    ├── credits/             ← Módulo API REST (devuelve JSON)
    │   ├── __init__.py
    │   ├── routes.py        ← Endpoints /api/credits/...
    │   └── schemas.py       ← Validación de datos con Marshmallow
    │
    ├── web/                 ← Módulo Web (devuelve HTML)
    │   ├── __init__.py
    │   └── routes.py        ← Rutas /credits/...
    │
    ├── templates/           ← Archivos HTML
    │   ├── base.html        ← Layout base con navbar
    │   └── credits/
    │       ├── list.html    ← Tabla de todos los créditos
    │       ├── form.html    ← Formulario para crear y editar
    │       ├── detail.html  ← Detalle de un crédito
    │       └── charts.html  ← Página de gráficas
    │
    └── static/              ← Archivos estáticos
        ├── css/style.css    ← Estilos personalizados
        └── js/main.js       ← JavaScript general
```

---

## Archivos principales explicados

### `run.py` — El botón de encender

```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
```

Solo existe para iniciar la aplicación. Se ejecuta con `python run.py` y levanta el servidor en `http://localhost:5000`.

---

### `config.py` — La configuración

```python
class Config:
    SECRET_KEY = "dev-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///creditos.db"
```

Una clase con las variables de configuración. Flask la lee al iniciar para saber dónde está la base de datos y otros ajustes. Si en el futuro se quisiera usar PostgreSQL, solo se cambia `SQLALCHEMY_DATABASE_URI` aquí.

---

### `app/__init__.py` — La fábrica de la app

```python
def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)

    app.register_blueprint(credits_bp, url_prefix="/api/credits")
    app.register_blueprint(web_bp,     url_prefix="/credits")

    db.create_all()
    return app
```

Es una función que construye y conecta todas las piezas de la aplicación:
1. Crea la app Flask
2. Carga la configuración
3. Conecta la base de datos
4. Registra los dos blueprints (módulos de rutas)
5. Crea las tablas si no existen

---

### `app/models.py` — El molde de los datos

```python
class Credit(db.Model):
    __tablename__ = "credits"

    id          = db.Column(db.Integer,  primary_key=True)
    client_id   = db.Column(db.String(50),  nullable=False, unique=True)
    client_name = db.Column(db.String(120), nullable=False)
    amount      = db.Column(db.Float,       nullable=False)
    interest    = db.Column(db.Float,       nullable=False)
    term_months = db.Column(db.Integer,     nullable=False)
    status      = db.Column(db.String(20),  default="ACTIVO")
    created_at  = db.Column(db.DateTime,    default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime,    default=datetime.utcnow)
```

Una clase que representa la tabla `credits` en la base de datos. Cada atributo es una columna. SQLAlchemy traduce automáticamente entre objetos Python y filas en la base de datos.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | Entero | Identificador único, se genera solo |
| `client_id` | Texto | ID del cliente, no puede repetirse |
| `client_name` | Texto | Nombre del cliente |
| `amount` | Decimal | Monto del crédito |
| `interest` | Decimal | Tasa de interés |
| `term_months` | Entero | Plazo en meses |
| `status` | Texto | Estado: ACTIVO / PAGADO / VENCIDO |
| `created_at` | Fecha | Se llena automáticamente al crear |
| `updated_at` | Fecha | Se actualiza automáticamente al editar |

---

### `app/credits/schemas.py` — La validación

```python
class CreditSchema(Schema):
    client_id   = fields.Str(required=True)
    client_name = fields.Str(required=True)
    amount      = fields.Float(required=True)
    interest    = fields.Float(required=True)
    term_months = fields.Int(required=True)
```

Una clase que funciona como guardia de entrada para la API. Antes de guardar cualquier dato en la base de datos, Marshmallow revisa que todos los campos requeridos existan y tengan el tipo correcto. Si algo está mal, devuelve un error 422 con el detalle del problema.

---

## Los dos módulos de rutas (Blueprints)

Un **Blueprint** es un módulo de rutas independiente. Esta app tiene dos:

```
Blueprint "credits"  →  prefijo /api/credits  →  devuelve JSON
Blueprint "web"      →  prefijo /credits      →  devuelve HTML
```

### ¿Por qué dos?

Porque tienen propósitos distintos:
- El módulo **web** está pensado para usuarios navegando con el browser
- El módulo **credits** (API) está pensado para consumirse desde código externo: otras apps, mobile, Postman, etc.

---

### `app/credits/routes.py` — Rutas de la API

Todas las funciones reciben una petición HTTP y devuelven JSON.

| Función | Método | URL | Qué hace |
|---|---|---|---|
| `list_credits` | GET | `/api/credits/` | Devuelve todos los créditos en JSON |
| `create_credit` | POST | `/api/credits/` | Crea un crédito nuevo con validación |
| `get_credit` | GET | `/api/credits/<id>` | Devuelve un crédito por su ID |
| `update_credit` | PUT | `/api/credits/<id>` | Actualiza todos los campos de un crédito |
| `delete_credit` | DELETE | `/api/credits/<id>` | Elimina un crédito |
| `monthly_stats` | GET | `/api/credits/stats/monthly` | Datos para la gráfica de barras |
| `amount_ranges` | GET | `/api/credits/stats/amount-ranges` | Datos para el pie chart |

**Ejemplo de flujo para crear un crédito por API:**

```
POST /api/credits/
Body: { "client_id": "C001", "amount": 10000, ... }
        ↓
CreditSchema.load() valida los datos
        ↓
Si hay error  → devuelve {"errors": {...}} con código 422
Si está bien  → Credit(**data) crea el objeto
        ↓
db.session.add() + db.session.commit() guarda en BD
        ↓
Devuelve el crédito creado en JSON con código 201
```

---

### `app/web/routes.py` — Rutas de la interfaz web

Todas las funciones reciben una petición HTTP y devuelven una página HTML renderizada.

| Función | Método | URL | Qué hace |
|---|---|---|---|
| `list_credits` | GET | `/credits/` | Muestra la tabla de créditos |
| `new_credit` | GET | `/credits/new` | Muestra el formulario vacío |
| `create_credit` | POST | `/credits/new` | Guarda el crédito del formulario |
| `detail_credit` | GET | `/credits/<id>` | Muestra el detalle de un crédito |
| `edit_credit` | GET | `/credits/<id>/edit` | Muestra el formulario pre-llenado |
| `update_credit` | POST | `/credits/<id>/edit` | Guarda los cambios del formulario |
| `delete_credit` | POST | `/credits/<id>/delete` | Elimina y redirige a la lista |
| `charts` | GET | `/credits/charts` | Muestra la página de gráficas |

**Ejemplo de flujo para crear un crédito desde el formulario web:**

```
Usuario llena el formulario y hace clic en Guardar
        ↓
POST /credits/new con los datos del formulario
        ↓
create_credit() lee los campos con request.form.get(...)
        ↓
Crea objeto Credit y lo guarda en la BD
        ↓
flash("Crédito creado correctamente")
redirect → /credits/  (regresa a la lista)
```

---

## Los Templates (HTML)

### `base.html` — El esqueleto

Todos los demás templates heredan de este. Contiene el navbar y los scripts de Bootstrap. Define un bloque `content` vacío que cada página llena con su propio contenido.

```html
<nav>...</nav>               ← navbar con los links

{% block content %}          ← aquí cada página mete lo suyo
{% endblock %}

<script Bootstrap></script>
<script main.js></script>
```

### `list.html` — La tabla

Hereda `base.html`. Recibe la variable `credits` que viene de Python y la recorre con Jinja2 para generar filas de tabla:

```html
{% for credit in credits %}
<tr>
    <td>{{ credit.client_name }}</td>
    <td>{{ credit.amount }}</td>
    ...
</tr>
{% endfor %}
```

### `form.html` — El formulario

Se reutiliza tanto para crear como para editar. Si recibe un objeto `credit` con datos, los pre-llena en los inputs. Si recibe `None`, el formulario aparece vacío.

### `charts.html` — Las gráficas

No recibe datos de Python directamente. En cambio, el JavaScript dentro del template hace sus propias peticiones al servidor para obtener los datos.

---

## Las Gráficas — Explicación completa

### ¿Cómo funciona Chart.js?

Chart.js es una librería de JavaScript que dibuja gráficas dentro de un elemento `<canvas>` de HTML. Solo necesita que le pases las etiquetas (labels) y los valores (data), y hace todo el dibujo solo.

```html
<canvas id="miGrafica"></canvas>

<script>
new Chart(document.getElementById("miGrafica"), {
    type: "bar",
    data: {
        labels: ["Enero", "Febrero", "Marzo"],
        data:   [5,       8,         3]
    }
})
</script>
```

### La separación de responsabilidades

```
PYTHON (servidor)          JAVASCRIPT (browser)
──────────────────         ────────────────────
Consulta la BD        →    Recibe los datos en JSON
Cuenta y agrupa       →    Se los pasa a Chart.js
Devuelve JSON         →    Chart.js dibuja la gráfica
```

Python nunca dibuja nada. Solo provee los datos. JavaScript nunca toca la base de datos. Solo dibuja.

---

### Gráfica 1 — Créditos otorgados por mes (barras)

**Endpoint que la alimenta:** `GET /api/credits/stats/monthly`

**Función en Python:**

```python
def monthly_stats():
    from collections import defaultdict
    credits = Credit.query.all()         # trae todos los créditos
    counts = defaultdict(int)
    for c in credits:
        key = c.created_at.strftime("%Y-%m")  # "2025-01", "2025-06"...
        counts[key] += 1                      # cuenta cuántos hay por mes
    result = [{"month": k, "total": v} for k, v in sorted(counts.items())]
    return jsonify(result)
```

**Ejemplo de respuesta JSON:**

```json
[
  { "month": "2025-01", "total": 3 },
  { "month": "2025-04", "total": 7 },
  { "month": "2026-06", "total": 2 }
]
```

**JavaScript que la dibuja:**

```javascript
fetch("/api/credits/stats/monthly")
    .then(r => r.json())
    .then(data => {
        const labels = data.map(d => d.month)   // ["2025-01", "2025-04", ...]
        const totals = data.map(d => d.total)   // [3, 7, 2]

        new Chart(canvas, {
            type: "bar",
            data: { labels, datasets: [{ data: totals }] }
        })
    })
```

---

### Gráfica 2 — Distribución por rango de monto (pie)

**Endpoint que la alimenta:** `GET /api/credits/stats/amount-ranges`

**Función en Python:**

```python
def amount_ranges():
    ranges = [
        {"label": "$0 - $5,000",      "min": 0,     "max": 5000},
        {"label": "$5,001 - $20,000",  "min": 5001,  "max": 20000},
        {"label": "$20,001 - $50,000", "min": 20001, "max": 50000},
        {"label": "$50,001+",          "min": 50001, "max": float("inf")},
    ]
    credits = Credit.query.with_entities(Credit.amount).all()  # solo trae montos
    for r in ranges:
        r["total"] = sum(1 for (a,) in credits if r["min"] <= a <= r["max"])
    return jsonify([{"label": r["label"], "total": r["total"]} for r in ranges])
```

**Ejemplo de respuesta JSON:**

```json
[
  { "label": "$0 - $5,000",      "total": 4 },
  { "label": "$5,001 - $20,000",  "total": 9 },
  { "label": "$20,001 - $50,000", "total": 2 },
  { "label": "$50,001+",          "total": 1 }
]
```

**JavaScript que la dibuja:**

```javascript
fetch("/api/credits/stats/amount-ranges")
    .then(r => r.json())
    .then(data => {
        new Chart(canvas, {
            type: "pie",
            data: {
                labels: data.map(d => d.label),
                datasets: [{ data: data.map(d => d.total) }]
            }
        })
    })
```

---

### Flujo completo de las gráficas paso a paso

```
[1] Usuario abre http://localhost:5000/credits/charts
              ↓
[2] Flask ejecuta charts() en web/routes.py
    → render_template("credits/charts.html")
    → devuelve HTML con dos <canvas> vacíos
              ↓
[3] Browser recibe el HTML y lo muestra
    → ejecuta el JavaScript del template
              ↓
[4] JavaScript lanza dos fetch() en paralelo:
    ├── fetch("/api/credits/stats/monthly")
    └── fetch("/api/credits/stats/amount-ranges")
              ↓
[5] Flask ejecuta monthly_stats() y amount_ranges()
    → cada función consulta la base de datos
    → cuentan y agrupan los datos
    → devuelven JSON
              ↓
[6] JavaScript recibe los JSON
    → extrae labels y totales
    → llama a new Chart() con esos datos
              ↓
[7] Chart.js dibuja las gráficas en los <canvas>
    → el usuario ve las gráficas en pantalla
```

---

## Diagrama general de la arquitectura

```
                         BROWSER
              ┌────────────────────────────┐
              │   charts.html              │
              │   ┌──────────────────────┐ │
              │   │  Gráfica de barras   │ │
              │   │  (Chart.js)          │ │
              │   └──────────────────────┘ │
              │   ┌──────────────────────┐ │
              │   │  Pie chart           │ │
              │   │  (Chart.js)          │ │
              │   └──────────────────────┘ │
              └───────────┬────────────────┘
                          │  fetch (JSON)
                     SERVIDOR (Flask)
              ┌───────────┴────────────────┐
              │   app/credits/routes.py    │
              │   monthly_stats()          │
              │   amount_ranges()          │
              └───────────┬────────────────┘
                          │  Credit.query
              ┌───────────┴────────────────┐
              │   app/models.py            │
              │   class Credit             │
              └───────────┬────────────────┘
                          │
              ┌───────────┴────────────────┐
              │   creditos.db (SQLite)     │
              │   tabla: credits           │
              └────────────────────────────┘
```

---

## URLs disponibles en la app

### Interfaz web (para el browser)

| URL | Qué muestra |
|---|---|
| `http://localhost:5000/credits/` | Lista de todos los créditos |
| `http://localhost:5000/credits/new` | Formulario para crear un crédito |
| `http://localhost:5000/credits/<id>` | Detalle de un crédito |
| `http://localhost:5000/credits/<id>/edit` | Formulario para editar |
| `http://localhost:5000/credits/charts` | Página de gráficas |

### API REST (devuelve JSON)

| URL | Método | Qué devuelve |
|---|---|---|
| `http://localhost:5000/api/credits/` | GET | Lista de créditos en JSON |
| `http://localhost:5000/api/credits/` | POST | Crear crédito nuevo |
| `http://localhost:5000/api/credits/<id>` | GET | Un crédito en JSON |
| `http://localhost:5000/api/credits/<id>` | PUT | Actualizar crédito |
| `http://localhost:5000/api/credits/<id>` | DELETE | Eliminar crédito |
| `http://localhost:5000/api/credits/stats/monthly` | GET | Totales por mes |
| `http://localhost:5000/api/credits/stats/amount-ranges` | GET | Distribución por monto |

---

## Cómo correr el proyecto

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Correr la app
python run.py

# 3. Abrir en el browser
http://localhost:5000/credits/
```

La base de datos `creditos.db` se crea automáticamente en la primera ejecución.
