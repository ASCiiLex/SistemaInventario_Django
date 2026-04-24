# 🧾 Sistema de Inventario Multi-Tenant

Aplicación SaaS de gestión de inventario desarrollada con Django, con soporte multi-organización, stock por ubicación y lógica de dominio real.

---

## 🚀 Características

* Multi-tenant (organizaciones aisladas)
* Roles: owner, manager, staff
* Stock distribuido por ubicaciones
* Movimientos (entrada, salida, transferencias)
* Pedidos con impacto en stock
* Notificaciones automáticas (stock mínimo)
* Dashboard con métricas en tiempo real
* Observabilidad integrada

---

## 🏗️ Stack

* Django 6 + Python 3.12
* PostgreSQL
* Redis + Channels
* Docker

---

## ⚙️ Instalación rápida (demo)

```bash
git clone <URL_DEL_REPO>
cd SistemaInventario
docker compose up -d
python manage.py migrate
python manage.py flush
python manage.py shell
```

```python
from scripts.seed_demo import run
run()
```

```bash
daphne sistema_inventario.asgi:application
```

Abrir: http://127.0.0.1:8000

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

   * Generadas automáticamente por stock bajo

3. **Productos**

   * Stock por ubicación
   * Estados mixtos (normal / bajo mínimo)

4. **Almacenes**

   * Incidencias activas

---

## 🧪 Datos demo

El script `seed_demo` genera un escenario realista:

* Organización "Demo Corp"
* Usuarios con distintos roles
* Productos con stock distribuido
* Movimientos (entrada, salida, transferencias)
* Productos bajo mínimo → disparan alertas
* Actividad suficiente para poblar dashboard y métricas

---

## 🧠 Arquitectura

* Multi-tenant por organización
* Service layer para lógica de negocio
* Dominio desacoplado (no CRUD simple)
* Sistema orientado a eventos (notificaciones, auditoría)
* Observabilidad integrada

---

## 📌 Notas

* PostgreSQL obligatorio (no SQLite)
* Redis requerido (cache + WebSockets)
* Seed idempotente y orientado a demo

---

## 👨‍💻 Autor

ASCiiLex
GitHub: https://github.com/ASCiiLex
