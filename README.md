# 🧾 Sistema de Inventario Multi-Tenant

Aplicación SaaS de gestión de inventario desarrollada con Django, con soporte multi-organización, stock por ubicación y lógica de dominio real.

---

## 🚀 Características

* Multi-tenant (organizaciones aisladas)
* Roles: owner, manager, staff
* Stock distribuido por ubicaciones
* Movimientos (entrada, salida, transferencias)
* Pedidos con impacto en stock
* Notificaciones automáticas (stock mínimo y riesgo)
* Dashboard con métricas en tiempo real
* Observabilidad integrada

---

## 🏗️ Stack

* Django 6 + Python 3.12
* PostgreSQL
* Redis (opcional en local)
* Channels (WebSockets)

---

## ⚙️ Instalación rápida (local)

```bash
git clone <URL_DEL_REPO>
cd SistemaInventario

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
./run_demo.sh

python manage.py runserver
```

Abrir: http://127.0.0.1:8000

---

## 🚀 Entorno Demo

El proyecto incluye un script que genera un escenario completo y coherente.

### ▶️ Ejecutar demo en local

```bash
python manage.py migrate
./run_demo.sh
```

---

### ☁️ Ejecutar demo en Railway

Railway no ejecuta seeds automáticamente.

#### 1. Abrir shell en Railway

```bash
railway run python manage.py shell
```

#### 2. Ejecutar seed

```python
from scripts.seed_demo import run
run()
```

---

### ⚠️ Nota importante

Asegúrate de que:

* Estás ejecutando el comando dentro de Railway (`railway run`)
* O tienes correctamente exportado `DATABASE_URL`

---

### 🔁 Reset de datos (solo local)

```bash
python manage.py flush --no-input
./run_demo.sh
```

---

### 🎯 Qué genera el seed

* Organización "Demo Corp"
* Usuarios con distintos roles
* Stock inicial distribuido por ubicaciones
* Movimientos de stock realistas (IN / OUT / TRANSFER)
* Productos bajo mínimo (alertas activas)
* Reposición parcial
* Actividad suficiente para dashboard y métricas

---

## 🔐 Acceso demo

| Usuario      | Password  |
| ------------ | --------- |
| admin        | admin1234 |
| demo_manager | demo1234  |
| demo_staff   | demo1234  |

---

## 🎯 Qué ver primero (recomendado)

1. **Dashboard**

   * KPIs dinámicos
   * Productos bajo mínimo
   * Actividad reciente

2. **Notificaciones**

   * Generadas automáticamente por stock bajo y riesgo

3. **Productos**

   * Stock por ubicación
   * Estados mixtos (normal / bajo mínimo)

4. **Almacenes**

   * Incidencias activas

---

## 🧪 Datos demo

El script `seed_demo` genera un escenario realista orientado a demostración funcional del sistema.

---

## 🧠 Arquitectura

* Multi-tenant por organización
* Service layer para lógica de negocio
* Dominio desacoplado (no CRUD simple)
* Sistema orientado a eventos (notificaciones, auditoría)
* Observabilidad integrada

---

## 📌 Notas

* PostgreSQL requerido (no SQLite)
* Redis no necesario en local (fallback automático)
* En producción se usa Redis para cache y WebSockets
* Seed idempotente y seguro para múltiples ejecuciones
* En Railway, ejecutar seed manualmente tras deploy

---

## 👨‍💻 Autor

ASCiiLex
GitHub: https://github.com/ASCiiLex
