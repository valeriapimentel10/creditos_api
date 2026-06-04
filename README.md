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
