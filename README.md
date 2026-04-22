# 🧾 Sistema de Inventario Multi-Tenant

Aplicación SaaS de gestión de inventario desarrollada con Django, con soporte multi-organización, stock por ubicación y lógica de dominio real.

---

## 🚀 Características

* Multi-tenant (organizaciones aisladas)
* Roles: owner, admin, manager, staff
* Stock distribuido por ubicaciones
* Movimientos (entrada, salida, transferencias)
* Pedidos con impacto en stock
* Notificaciones automáticas (stock mínimo)
* Dashboard + métricas + observabilidad

---

## 🏗️ Stack

* Django 6 + Python 3.12
* PostgreSQL
* Redis + Channels
* Docker

---

## ⚙️ Instalación

```bash
git clone <URL_DEL_REPO>
cd SistemaInventario
docker compose up -d
python manage.py migrate
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

| Usuario      | Password |
| ------------ | -------- |
| demo_admin   | demo1234 |
| demo_manager | demo1234 |
| demo_staff   | demo1234 |

---

## 🧭 Qué probar

* Dashboard (actividad y métricas)
* Productos → stock por ubicación
* Movimientos → trazabilidad real
* Transferencias → validación de dominio
* Pedidos → impacto en stock
* Notificaciones automáticas
* Observabilidad (`/metrics`)

---

## 🧠 Arquitectura

* Multi-tenant por organización
* Service layer para lógica de negocio
* Dominio centralizado (no CRUD simple)
* Event-driven (notificaciones y auditoría)
* Observabilidad integrada

---

## 🧪 Datos demo

El script `seed_demo` genera:

* Organización Demo Corp
* Usuarios demo
* Productos, stock y movimientos
* Pedidos y transferencias

---

## 📌 Notas

* PostgreSQL obligatorio (no SQLite)
* Redis requerido (cache + WebSockets)
* Seed no destructivo

---

## 👨‍💻 Autor

ASCiiLex
GitHub: https://github.com/ASCiiLex
