#!/bin/bash

echo "🚀 Inicializando entorno demo..."

python manage.py flush --no-input
python manage.py migrate

echo "📦 Generando datos demo..."

python manage.py shell <<EOF
from scripts.seed_demo import run
run()
EOF

echo "✅ Demo lista"
echo "👉 Accede con: admin / admin1234"