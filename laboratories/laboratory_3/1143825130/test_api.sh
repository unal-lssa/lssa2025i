#!/bin/bash

#
# Script para pruebas de API REST
#

# === jq para formatear JSON ===
# Instalar jq si no está instalado
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

# === Configuración de Docker ===
# Solo si el usuario lo indica por parametro -c
if [ "$1" == "-c" ]; then
    echo "🧹 Limpiando contenedores y volúmenes..."
    docker compose down --remove-orphans
    docker compose build
    docker compose up -d
fi

# === Configuración de Pruebas ===
GATEWAY_URL="http://localhost:5000"
USER="user1"
USER_PASSWORD="password123"
ADMIN="admin"
ADMIN_PASSWORD="adminpass"

echo "🔐 Obteniendo token de usuario..."
USER_TOKEN=$(curl -s -X POST "$GATEWAY_URL/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USER\", \"password\": \"$USER_PASSWORD\"}" | jq -r '.token')

if [ "$USER_TOKEN" == "null" ]; then
  echo "❌ Falló la autenticación del usuario."
  exit 1
else
  echo "✅ Token de usuario obtenido."
fi

echo "🔐 Obteniendo token de admin..."
ADMIN_TOKEN=$(curl -s -X POST "$GATEWAY_URL/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$ADMIN\", \"password\": \"$ADMIN_PASSWORD\"}" | jq -r '.token')

if [ "$ADMIN_TOKEN" == "null" ]; then
  echo "❌ Falló la autenticación del admin."
  exit 1
else
  echo "✅ Token de admin obtenido."
fi

echo "🧪 Creando nueva orden..."
curl -s -X POST "$GATEWAY_URL/order" \
  -H "Authorization: Bearer $USER_TOKEN" | jq -r '.message'

echo "📦 Consultando órdenes..."
curl -s "$GATEWAY_URL/orders" \
  -H "Authorization: Bearer $USER_TOKEN" | jq

echo "📦 Consultando inventario..."
curl -s "$GATEWAY_URL/inventory" \
  -H "Authorization: Bearer $USER_TOKEN" | jq

echo "📊 Consultando reporte con usuario (esperado: error 403)..."
curl -s -w "\n[Status: %{http_code}]\n" "$GATEWAY_URL/report" \
  -H "Authorization: Bearer $USER_TOKEN"

echo "📊 Consultando reporte con admin..."
curl -s "$GATEWAY_URL/report" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

echo "✅ Pruebas completas."
