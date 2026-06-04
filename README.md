# Sistema de Créditos

Aplicación web para gestionar créditos. Permite crear, consultar, editar y eliminar créditos, y visualizar estadísticas con gráficas interactivas.

---

## Funcionalidades

- Crear, editar y eliminar créditos
- Filtrar créditos por estado (ACTIVO / PAGADO / VENCIDO)
- Ver el detalle de cada crédito
- Gráfica de barras: créditos otorgados por mes
- Gráfica de pie: distribución por rango de monto
- API REST para consumo externo

---

## Tecnologías

- **Python 3** + **Flask 3.1.2**
- **SQLAlchemy** + **SQLite**
- **Marshmallow** para validación
- **Bootstrap 5** + **Chart.js 4**

---

## Requisitos previos

Antes de instalar, asegúrate de tener:

- Python 3.9 o superior → [python.org](https://www.python.org/downloads/)
- pip (viene incluido con Python)

Verifica tu versión con:

```bash
python --version
pip --version
```

---

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd creditos_api
```

### 2. Crear un entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python -m venv venv
source venv/bin/activate
```

> El entorno virtual aísla las dependencias del proyecto para que no interfieran con otros proyectos de Python en tu máquina.

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Correr la aplicación

```bash
python run.py
```

### 5. Abrir en el browser

```
http://localhost:5000/credits/
```

La base de datos `creditos.db` se crea automáticamente en la primera ejecución. No necesitas hacer ninguna migración.

---

## Variables de entorno (opcional)

Por defecto la app funciona sin ninguna configuración extra. Si quieres personalizar algo, crea un archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=tu-clave-secreta-aqui
DATABASE_URL=sqlite:///creditos.db
```

| Variable | Default | Descripción |
|---|---|---|
| `SECRET_KEY` | `dev-secret-key` | Llave para firmar sesiones. Cámbiala en producción |
| `DATABASE_URL` | `sqlite:///creditos.db` | URL de conexión a la base de datos |

---

## Estructura del proyecto

```
creditos_api/
├── run.py                  ← Punto de entrada
├── config.py               ← Configuración general
├── requirements.txt        ← Dependencias
└── app/
    ├── __init__.py         ← Fábrica de la app
    ├── models.py           ← Modelo Credit (base de datos)
    ├── credits/            ← API REST  →  /api/credits/
    │   ├── routes.py
    │   └── schemas.py
    ├── web/                ← Interfaz web  →  /credits/
    │   └── routes.py
    ├── templates/          ← HTML (Jinja2)
    └── static/             ← CSS y JS
```

---

## URLs principales

### Interfaz web

| URL | Descripción |
|---|---|
| `/credits/` | Lista de créditos |
| `/credits/new` | Crear nuevo crédito |
| `/credits/<id>` | Detalle de un crédito |
| `/credits/<id>/edit` | Editar crédito |
| `/credits/charts` | Gráficas estadísticas |

### API REST

| Método | URL | Descripción |
|---|---|---|
| GET | `/api/credits/` | Lista todos los créditos |
| POST | `/api/credits/` | Crea un crédito nuevo |
| GET | `/api/credits/<id>` | Obtiene uno por ID |
| PUT | `/api/credits/<id>` | Actualiza un crédito |
| DELETE | `/api/credits/<id>` | Elimina un crédito |
| GET | `/api/credits/stats/monthly` | Totales por mes |
| GET | `/api/credits/stats/amount-ranges` | Distribución por monto |

#### Ejemplo de request a la API

```bash
# Crear un crédito
curl -X POST http://localhost:5000/api/credits/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "C001",
    "client_name": "Ana García",
    "amount": 15000,
    "interest": 12.5,
    "term_months": 24
  }'
```

---

## Solución de problemas comunes

**`ModuleNotFoundError`** — Las dependencias no están instaladas.
```bash
pip install -r requirements.txt
```

**`Address already in use`** — El puerto 5000 está ocupado.
```bash
# Cambia el puerto en run.py
app.run(debug=True, port=5001)
```

**La base de datos no se crea** — Asegúrate de correr `python run.py` desde la raíz del proyecto, no desde dentro de `app/`.

---

## Documentación adicional

- [`GUIA_COMPLETA.md`](GUIA_COMPLETA.md) — Arquitectura, módulos y explicación detallada del código
