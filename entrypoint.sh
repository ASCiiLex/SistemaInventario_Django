#!/bin/bash
set -e

echo "🚀 ENTRYPOINT: iniciando"

python manage.py migrate

echo "🚀 ENTRYPOINT: ejecutando seed"
python manage.py seed

echo "🚀 ENTRYPOINT: collectstatic"
python manage.py collectstatic --noinput

echo "🚀 ENTRYPOINT: arrancando gunicorn"
exec gunicorn sistema_inventario.wsgi:application --bind 0.0.0.0:$PORT --workers 3