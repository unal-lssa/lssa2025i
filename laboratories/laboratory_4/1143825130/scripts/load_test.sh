#!/bin/bash
# load_test.sh
# Ejecuta una prueba de carga sobre /data utilizando JWT y herramientas wrk o ab.

# ========================
# VALIDACIÓN DEL ARGUMENTO
# ========================
if [ -z "$1" ]; then
  echo "❌ Error: Debes proporcionar un JWT como argumento."
  echo "Uso: ./load_test.sh <jwt_token>"
  exit 1
fi

JWT_TOKEN="$1"
ENDPOINT="http://localhost:8000/data"
DURATION="30s"
THREADS=20
CONCURRENCY=500
REQUESTS=500
SEPARATOR="\n---\n"

# ========================
# Instalar jq si no está presente
# ========================
if ! command -v jq &> /dev/null
then
    echo "🔄 Instalando jq..."
    if [ -f /etc/debian_version ]; then
        sudo apt update && sudo apt install jq -y
    elif [ -f /etc/redhat-release ]; then
        sudo yum install jq -y
    else
        echo "❌ Sistema no soportado para la instalación de jq."
        exit 1
    fi
else
    echo "✅ jq ya está instalado."
fi

# Función para imprimir JSON bonito si existe `jq`
pretty_json() {
  if command -v jq &> /dev/null; then
    echo "$1" | jq
  else
    echo "$1"
  fi
}

# ========================
# Instalar wrk si no está presente (Debian-like)
# ========================
if ! command -v wrk &> /dev/null; then
    echo "🔄 wrk no está instalado. Intentando instalarlo desde fuente..."
    if [ -f /etc/debian_version ]; then
        sudo apt update
        sudo apt install wrk -y
    else
        echo "⚠️ wrk no se puede instalar automáticamente en este sistema"
    fi
else
    echo "✅ wrk ya está instalado."
fi

echo -e "$SEPARATOR"

echo "🚀 Iniciando prueba de carga en $ENDPOINT con autorización JWT"
echo "Token: ${JWT_TOKEN:0:20}..."

# ========================
# WRK
# ========================
if command -v wrk &> /dev/null; then
  echo "✅ Ejecutando con wrk..."
  wrk -t$THREADS -c$CONCURRENCY -d$DURATION \
      -H "Authorization: $JWT_TOKEN" \
      $ENDPOINT

# ========================
# AB
# ========================
elif command -v ab &> /dev/null; then
  echo "✅ Ejecutando con ab..."
  ab -n $REQUESTS -c $CONCURRENCY \
     -H "Authorization: $JWT_TOKEN" \
     $ENDPOINT

# ========================
# ERROR
# ========================
else
  echo "❌ Error: No se encontró ninguna herramienta de carga instalada (wrk o ab)."
  echo "Por favor, instala una de ellas antes de continuar."
  exit 1
fi

echo "🏁 Prueba de carga finalizada."
