# HApy3 — Documentación del Proyecto

## ¿Qué es este proyecto?

Una aplicación web para la **gestión de riesgo financiero**. Permite cargar archivos de datos (insumos), procesarlos mediante pipelines ETL, generar reportes regulatorios (26 reportes), y visualizar estadísticas en dashboards interactivos.

Está organizada en tres áreas de riesgo:

| Área | Código | Tipo de riesgo |
|---|---|---|
| Riesgo de Crédito | RC | Morosidad, clasificación, bureau |
| Riesgo de Mercado | RM | VaR, tasas, posiciones |
| Riesgo Operacional | RO | Otros riesgos |

---

## Tecnologías utilizadas

| Tecnología | Para qué se usa |
|---|---|
| Python 3 | Lenguaje principal |
| Flask 3.1 | Framework web — maneja rutas y peticiones HTTP |
| SQLAlchemy 2.0 | Conecta Python con las bases de datos |
| SQLite | Base de datos (4 archivos .db separados) |
| pandas / numpy | Manipulación y transformación de datos |
| scikit-learn / lightgbm | Modelos de machine learning (scoring, clasificación) |
| openpyxl | Lectura y escritura de archivos Excel |
| pdfplumber | Extracción de datos desde PDFs |
| oracledb / pyodbc | Conexión a bases de datos Oracle (opcional) |
| reportlab | Generación de PDFs |
| Jinja2 | Motor de templates — mete datos de Python en el HTML |
| Bootstrap | Estilos y componentes visuales |
| Font Awesome | Iconos |
| Choices.js / Tom-Select | Componentes de selección interactivos en el frontend |
| Claude API | Generador de consultas SQL por lenguaje natural |

---

## Estructura de carpetas

```
HApy3/
│
├── run.py                        ← Punto de entrada, arranca el servidor (localhost:7000)
├── run_batch.py                  ← Procesador batch para cargas programadas
├── config.py                     ← Configuración general (bases de datos, claves)
├── requirements.txt              ← Lista de dependencias Python
├── .env                          ← Variables de entorno (SECRET_KEY, APP_BRAND)
│
├── MIDr/                         ← Paquete Flask principal
│   ├── __init__.py               ← Fábrica de la app, registra blueprints y configuraciones globales
│   ├── models.py                 ← Modelos SQLAlchemy (12+ tablas)
│   ├── a_external.py             ← Blueprint: autenticación (login/logout)
│   ├── b_portal.py               ← Blueprint: dashboard principal
│   ├── c_account.py              ← Blueprint: cuenta y perfil de usuario
│   ├── d_docs.py                 ← Blueprint: carga y gestión de insumos
│   ├── e_reports.py              ← Blueprint: generación y descarga de reportes
│   ├── z1_general_functions.py   ← Utilidades de consulta a la BD
│   ├── z2_graph_functions.py     ← Funciones de gráficas del dashboard
│   │
│   ├── branding/                 ← Sistema multi-marca
│   │   ├── default/              ← Marca por defecto (textos.json + imágenes)
│   │   └── delta_data/           ← Marca alternativa
│   │
│   ├── static/                   ← Archivos estáticos
│   │   └── assets/
│   │       ├── css/              ← Estilos personalizados por módulo
│   │       ├── js/               ← JavaScript general
│   │       └── plugins/          ← Librerías de terceros (Bootstrap, Chart.js, etc.)
│   │
│   ├── templates/                ← Archivos HTML (Jinja2)
│   │   ├── base.html             ← Layout base con navbar
│   │   └── [módulo]/             ← Templates por blueprint
│   │
│   └── data_processing/          ← Pipeline ETL y reportes (independiente de Flask)
│       ├── A_Statics/            ← Catálogos maestros (30+ archivos CSV/Excel)
│       ├── B_ETL_Insumos/        ← Pipeline de carga de archivos
│       ├── D_Reportes/           ← 26 reportes (R01–R25)
│       └── F_Query_Builder/      ← Generador de consultas con IA
│
├── utilerias/                    ← Scripts de soporte y exploración
│   ├── notebooks/                ← Jupyter notebooks
│   ├── scripts/                  ← Scripts batch y utilidades
│   └── model_llm/                ← Integración con modelos de lenguaje
│
└── logs/                         ← Logs diarios de consola (app_console_YYYY_MM_DD.log)
```

---

## Archivos principales explicados

### `run.py` — El botón de encender

```python
from MIDr import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=7000)
```

Inicia el servidor en `http://localhost:7000`. Solo existe para arrancar la aplicación.

---

### `run_batch.py` — El procesador automático

Permite ejecutar cargas de insumos sin abrir el browser. Se integra con el Programador de Tareas de Windows para correr automáticamente a ciertas horas.

Modos de uso:
- **Por tiempo:** carga los insumos configurados para una hora específica
- **Por ID:** fuerza la carga de un insumo específico
- **Bulk:** carga todos los archivos de una carpeta

---

### `config.py` — La configuración

```python
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")         # clave para sesiones
    SQLALCHEMY_DATABASE_URI = SQLITE_SYS         # BD principal del sistema
    SQLALCHEMY_BINDS = {                         # BDs secundarias por área
        'dbR':    SQLITE_REPORTS_RC,             # Riesgo de Crédito
        'dbR_RM': SQLITE_REPORTS_RM,             # Riesgo de Mercado
        'dbR_RO': SQLITE_REPORTS_RO,             # Riesgo Operacional
    }
    MAX_CONTENT_LENGTH = 15 * 1024 * 1024 * 1024  # 15 GB máximo por archivo
    BRAND = os.getenv("APP_BRAND", "default")     # marca visual activa
```

Define cuatro bases de datos SQLite separadas — una para el sistema y una por cada área de riesgo. Si en el futuro se quisiera usar PostgreSQL, solo se cambia `SQLALCHEMY_DATABASE_URI`.

---

### `MIDr/__init__.py` — La fábrica de la app

```python
def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)

    # Registra blueprints
    app.register_blueprint(a_external.bp)
    app.register_blueprint(b_portal.bp)
    app.register_blueprint(c_account.bp)
    app.register_blueprint(d_docs.bp)
    app.register_blueprint(e_reports.bp)
    app.register_blueprint(query_bp)

    with app.app_context():
        db.create_all()   # crea tablas si no existen

    return app
```

Además del núcleo anterior, hace cosas extra que este proyecto necesita:

| Bloque | Para qué sirve |
|---|---|
| `_TeeStream` + `_setup_console_tee()` | Guarda todo lo que aparece en consola también en un archivo `.log` diario |
| WAL en SQLite (`PRAGMA journal_mode=WAL`) | Permite que varios procesos lean la BD al mismo tiempo sin bloquearse |
| `max_form_parts = 10000` | Los insumos tienen cientos de columnas — Flask por defecto solo acepta 1000 campos en un formulario |
| `inject_branding()` | Inyecta el logo y textos de la marca en todos los templates automáticamente |
| `filtro_fecha` | Filtro Jinja2 para mostrar fechas como `03/06/2026` en lugar de `2026-06-03` |
| `add_no_cache_headers` | En desarrollo, obliga al browser a no guardar CSS/JS en caché |
| `branding_files` | Ruta especial para servir imágenes del tema activo |

---

### `MIDr/models.py` — Los moldes de los datos

Define las tablas de la base de datos como clases Python. SQLAlchemy traduce automáticamente entre objetos Python y filas en la base de datos.

| Modelo | Tabla | Qué representa |
|---|---|---|
| `a_sys_user` | usuarios | Email, contraseña hasheada, área (RC/RM/RO) |
| `a_sys_notifications` | notificaciones | Avisos por usuario |
| `a_sys_input_list` | insumos | Metadata de cada archivo (ruta, tipo, frecuencia, configuración batch) |
| `a_sys_input_list_status` | estado de insumos | Estado actual (1=ok, 0=error, 2=warning), fecha, comentarios |
| `a_sys_input_resume` | historial de insumos | Conteo de registros por insumo por fecha |
| `A_SYS_input_columns` | columnas de insumos | Definición de columnas, formatos, catálogos, reglas de validación |
| `a_sys_input_group` | grupos de insumos | Agrupaciones para carga masiva |
| `a_sys_report_list` | reportes | Metadata de cada reporte (área, frecuencia, clase Python que lo ejecuta) |
| `a_sys_report_list_status` | estado de reportes | Estado de ejecución |
| `a_sys_report_subprocess_status` | sub-procesos | Estado de etapas dentro de reportes complejos |
| `A_SYS_report_input` | insumos requeridos | Qué insumos necesita cada reporte (con restricciones de rezago) |
| `a_sys_data_catalog` | catálogo de datos | Metadata de columnas para el query builder |

---

## Los Blueprints (módulos de rutas)

Un Blueprint es un módulo de rutas independiente. Flask los junta al arrancar. Cada uno atiende un dominio diferente:

```
Blueprint         Prefijo URL    Qué maneja
──────────────    ───────────    ──────────────────────────────
a_external        /              Login y logout
b_portal          /portal        Dashboard con gráficas
c_account         /cuenta        Perfil y notificaciones del usuario
d_docs            /docs          Subir y gestionar insumos
e_reports         /reportes      Generar y descargar reportes
query_builder     /query         Consultas SQL por lenguaje natural
```

### Blueprint `a_external` — Autenticación

| Función | Método | URL | Qué hace |
|---|---|---|---|
| `login` | GET/POST | `/` | Muestra el formulario de login y valida credenciales |
| `logout` | GET | `/logout` | Cierra la sesión y redirige al login |

Usa `check_password_hash` de Werkzeug para verificar contraseñas — nunca se guarda la contraseña en texto plano.

**Flujo de login:**
```
Usuario llena email + contraseña
    → POST /
    → busca usuario en BD por email
    → verifica contraseña con check_password_hash()
    → si es correcto: guarda user_id en session{}
    → redirige al portal
```

### Blueprint `b_portal` — Dashboard

Muestra las gráficas del área del usuario (RC, RM o RO) usando datos de `z2_graph_functions.py`.

### Blueprint `c_account` — Cuenta

Permite al usuario ver y editar su perfil y ver sus notificaciones.

### Blueprint `d_docs` — Insumos

| Función | Qué hace |
|---|---|
| Lista de insumos | Muestra todos los insumos con su estado actual |
| Detalle de insumo | Columnas, historial, configuración |
| Subir archivo | Lanza el pipeline ETL en un hilo separado y muestra progreso |
| Configurar columnas | Define formato y validación por columna |

El progreso de carga se rastrea en un diccionario en memoria (`_input_progress`) que el frontend consulta por polling.

### Blueprint `e_reports` — Reportes

| Función | Qué hace |
|---|---|
| Lista de reportes | Muestra todos los reportes del área con su estado |
| Ejecutar reporte | Lanza la clase del reporte en un hilo separado |
| Descargar | Devuelve el archivo generado (Excel, PDF) |
| Gráficas | Muestra visualizaciones del resultado |

Los reportes se ejecutan dinámicamente: la BD guarda el nombre de la clase Python y el método a llamar, y el sistema lo carga con `importlib` en tiempo de ejecución.

---

## El Pipeline ETL (data_processing/B_ETL_Insumos/)

ETL = **Extract, Transform, Load**. Es el proceso de mover datos desde un archivo externo hasta la base de datos.

```
Archivo del usuario (Excel / CSV / PDF / ZIP)
        ↓ Extract
A1_get_file.py          ← localiza y lee el archivo
        ↓ Transform
C1_Input_Validation.py  ← valida columnas, tipos, valores nulos
D1_Processing_Input.py  ← transforma y enriquece los datos
        ↓ Load
B1_Update_Table.py      ← guarda en SQLite
        ↓
a_sys_input_list_status ← actualiza el estado del insumo en BD
```

Archivos especiales:

| Archivo | Para qué |
|---|---|
| `B2_Update_TXT_Buro.py` | Procesa archivos de buró de crédito en formato TXT |
| `B3_Update_PDF_EECC.py` | Extrae datos de estados de cuenta en PDF |
| `B4_Update_WB_ZIP.py` | Procesa archivos ZIP con múltiples Excel |
| `A_main_docs.py` | Orquestador principal — decide qué módulo usar según el tipo de archivo |

Códigos de estado del insumo:

| Código | Significado |
|---|---|
| 1 | Carga exitosa |
| 0 | Error |
| 2 | Advertencia (cargó pero con observaciones) |

---

## Los Reportes (data_processing/D_Reportes/)

26 reportes organizados por área. Cada uno sigue la misma estructura interna:

```
R##_NombreReporte/
├── A_NombreReporte_main.py    ← orquestador: coordina los demás
├── B_Pre_Processing.py        ← prepara y filtra los datos
├── C_Table_Aggregation.py     ← hace los cálculos y agrupaciones
└── D_Evaluate_Model.py        ← genera el output (Excel, tablas, gráficas)
```

Reportes por área:

**Riesgo de Crédito (RC)**
| ID | Nombre | Qué calcula |
|---|---|---|
| R01 | SMART | Modelo de scoring crediticio |
| R02 | Buro_Mensual | Reporte mensual de buró |
| R03 | Buro_Semanal | Reporte semanal de buró |
| R04 | Clasificacion | Clasificación estándar de cartera |
| R05 | Mora_Balance | Análisis de morosidad y saldos |
| R06 | Seguro | Reporte de seguros |
| R07 | Costo_Fondeo | Costo de fondeo |
| R08 | Provisiones | Cálculo de provisiones |
| R09 | Model_Lab | Laboratorio de prueba de modelos |
| R12 | EECC | Estados de cuenta |
| R25 | Clasificacion_IFRS9 | Clasificación bajo norma IFRS9 |

**Riesgo de Mercado (RM)**
| ID | Nombre | Qué calcula |
|---|---|---|
| R10 | VaR | Value at Risk |
| R23 | VaR_Alt | Versión alternativa de VaR |

**Otros**
| ID | Nombre | Qué calcula |
|---|---|---|
| R11 | AMR | Gestión de activos |
| R13, R15, R21, R22, R24 | Reportes de cumplimiento | Varios reportes regulatorios |
| R16, R18, R99 | Grandes exposiciones y saldos | Concentración y balances |

---

## El Query Builder (data_processing/F_Query_Builder/)

Permite hacer preguntas en lenguaje natural y obtener resultados de la base de datos sin escribir SQL.

```
Usuario escribe: "¿Cuántos créditos vencidos hay por estado?"
        ↓
ai_engine.py  ← envía la pregunta a Claude API
        ↓
Claude genera la consulta SQL
        ↓
routes.py valida que sea solo SELECT (bloquea INSERT, UPDATE, DELETE)
        ↓
Ejecuta la consulta en la BD
        ↓
Devuelve los resultados en tabla
```

Límite de seguridad: solo acepta consultas `SELECT`. Cualquier intento de modificar datos es rechazado.

---

## Los Catálogos (data_processing/A_Statics/)

30+ archivos CSV/Excel con datos maestros que no cambian frecuentemente:

- `CAT_*` — tablas de catálogo (estados, tipos, clasificaciones)
- `ETIQUETAS_*` — mapeos de etiquetas para reportes
- Subcarpetas con datos históricos, datos especiales y modelos

---

## Sistema de Branding (multi-marca)

La aplicación puede mostrar diferentes logos, colores y textos según la marca configurada en `.env`:

```
.env → APP_BRAND=delta_data

MIDr/branding/
├── default/
│   ├── texts.json    ← textos de la interfaz
│   └── logo.png      ← imágenes
└── delta_data/
    ├── texts.json
    └── logo.png
```

`load_branding()` en `__init__.py` lee la marca activa y la inyecta en todos los templates via `{{ texts.nombre_texto }}` e `{{ images.logo }}`.

---

## Las bases de datos

El proyecto usa 4 bases de datos SQLite separadas:

| Archivo | Bind | Contenido |
|---|---|---|
| `MONEX_MID.db` | principal | Sistema: usuarios, insumos, reportes, configuración |
| `MONEX_MID_RC.db` | `dbR` | Datos de reportes de Riesgo de Crédito |
| `MONEX_MID_RM.db` | `dbR_RM` | Datos de reportes de Riesgo de Mercado |
| `MONEX_MID_RO.db` | `dbR_RO` | Datos de reportes de Riesgo Operacional |

La separación existe para que los datos de cada área no se mezclen y para que las escrituras de un área no bloqueen las lecturas de otra.

**WAL (Write-Ahead Logging):** activado en todas las conexiones. Permite que mientras un proceso escribe datos, otros procesos puedan leer sin bloquearse — crítico cuando un reporte puede tardar varios minutos procesando datos.

---

## Flujo completo de la aplicación

```
[1] Usuario abre http://localhost:7000/
        ↓
[2] Flask ejecuta login() en a_external.py
    → muestra formulario de login
        ↓
[3] Usuario ingresa credenciales → POST /
    → verifica en BD → guarda sesión
    → redirige al dashboard
        ↓
[4] Dashboard (b_portal.py)
    → z2_graph_functions.py consulta la BD
    → devuelve HTML con gráficas del área del usuario
        ↓
[5] Usuario sube un insumo (d_docs.py)
    → archivo → pipeline ETL en hilo separado
    → frontend hace polling del progreso
    → estado actualizado en BD al terminar
        ↓
[6] Usuario genera un reporte (e_reports.py)
    → sistema carga la clase del reporte con importlib
    → ejecuta en hilo separado
    → resultado guardado en BD del área (RC/RM/RO)
        ↓
[7] Usuario descarga el reporte (Excel / PDF)
    o lo visualiza en el dashboard
```

---

## Diagrama de arquitectura

```
                            BROWSER
          ┌──────────────────────────────────────────┐
          │  Templates Jinja2 (HTML)                 │
          │  Bootstrap + Chart.js + Choices.js       │
          └──────────────────┬───────────────────────┘
                             │ HTTP
                    SERVIDOR FLASK (puerto 7000)
          ┌──────────────────┴───────────────────────┐
          │  MIDr/__init__.py  (fábrica)              │
          │                                           │
          │  a_external.py  ← autenticación           │
          │  b_portal.py    ← dashboard               │
          │  c_account.py   ← usuario                 │
          │  d_docs.py      ← insumos                 │
          │  e_reports.py   ← reportes                │
          │  query_builder/ ← consultas IA            │
          └──────────────────┬───────────────────────┘
                             │
                    DATA PROCESSING
          ┌──────────────────┴───────────────────────┐
          │  B_ETL_Insumos/   ← pipeline de carga    │
          │  D_Reportes/      ← 26 reportes           │
          │  A_Statics/       ← catálogos maestros    │
          │  F_Query_Builder/ ← IA + SQL              │
          └──────────────────┬───────────────────────┘
                             │
                       BASES DE DATOS
          ┌──────────────────┴───────────────────────┐
          │  MONEX_MID.db        ← sistema           │
          │  MONEX_MID_RC.db     ← Riesgo Crédito    │
          │  MONEX_MID_RM.db     ← Riesgo Mercado    │
          │  MONEX_MID_RO.db     ← Riesgo Operacional│
          └──────────────────────────────────────────┘
```

---

## URLs disponibles

### Interfaz web

| URL | Qué muestra |
|---|---|
| `http://localhost:7000/` | Pantalla de login |
| `http://localhost:7000/portal` | Dashboard principal con gráficas |
| `http://localhost:7000/cuenta` | Perfil del usuario |
| `http://localhost:7000/docs` | Lista de insumos y su estado |
| `http://localhost:7000/reportes` | Lista de reportes disponibles |
| `http://localhost:7000/query` | Query builder con IA |

---

## Cómo correr el proyecto

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Crear el archivo .env con las variables necesarias
# SECRET_KEY=una-clave-secreta
# APP_BRAND=default

# 3. Correr el servidor
python run.py

# 4. Abrir en el browser
# http://localhost:7000/
```

Las bases de datos se crean automáticamente en la primera ejecución.

### Correr el batch (carga automática)

```bash
python run_batch.py                   # carga insumos según su hora configurada
python run_batch.py --force-id 3      # fuerza la carga del insumo con ID 3
```

---

## Patrones de diseño que usa el proyecto

| Patrón | Dónde se ve | Por qué |
|---|---|---|
| Application Factory | `create_app()` en `__init__.py` | Permite crear múltiples instancias con distinta config (testing, producción) |
| Blueprint por dominio | `a_external`, `b_portal`, etc. | Cada área de negocio vive en su propio archivo independiente |
| ETL separado de Flask | `data_processing/` | Los reportes pueden correr sin servidor web (desde batch) |
| Dynamic dispatch | `importlib` para cargar reportes | Agregar un reporte nuevo solo requiere crear el archivo y una fila en BD |
| Thread + progress dict | `_input_progress`, `_report_progress` | El frontend puede consultar el progreso sin bloquear Flask |
| Multi-bind SQLAlchemy | 4 BDs con binds | Segrega datos por área y evita bloqueos cruzados |
| WAL en SQLite | `PRAGMA journal_mode=WAL` | Lecturas concurrentes mientras se escriben datos pesados |
| Context processor | `inject_branding()` | Variables disponibles en todos los templates sin pasarlas manualmente |
