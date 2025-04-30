#!/bin/bash
# test_all.sh
# Ejecuta una serie de pruebas automáticas usando curl y muestra la salida JSON completa de cada respuesta.

# ========================
# VALIDACIÓN DEL ARGUMENTO
# ========================
if [ -z "$1" ]; then
  echo "❌ Error: Debes proporcionar un JWT como argumento."
  echo "Uso: ./test_all.sh <jwt_token>"
  exit 1
fi

JWT_TOKEN="$1"
ENDPOINT="http://localhost:8000"
CACHE_ENDPOINT="http://localhost:5004"
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

echo -e "$SEPARATOR"

# =====================
# PRUEBA 0: GET /bussiness (microservicio sincrónico)
# =====================
echo "📡 [0] GET /bussiness (microservicio sincrónico)"
RESPONSE=$(curl -s -H "Authorization: $JWT_TOKEN" $ENDPOINT/business)
pretty_json "$RESPONSE"
echo -e "$SEPARATOR"

# =====================
# PRUEBA 1: GET /data (desde DB)
# =====================
echo "📡 [1] GET /data (esperado: respuesta desde DB)"
RESPONSE=$(curl -s -H "Authorization: $JWT_TOKEN" $ENDPOINT/data)
pretty_json "$RESPONSE"
echo -e "$SEPARATOR"

# =====================
# PRUEBA 2: GET /data (desde caché)
# =====================
echo "📡 [2] GET /data (esperado: respuesta desde caché)"
RESPONSE=$(curl -s -H "Authorization: $JWT_TOKEN" $ENDPOINT/data)
pretty_json "$RESPONSE"
echo -e "$SEPARATOR"

# =====================
# PRUEBA 3: POST /longtask (10 tareas livianas)
# =====================
echo "🧵 [3] POST /longtask (10 tareas livianas)"

for i in $(seq 1 10); do
  echo "➡️  Enviando tarea liviana #$i"
  RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
       -H "Authorization: $JWT_TOKEN" \
       -d "{\"task\": \"generar_informe_$i\"}" \
       $ENDPOINT/longtask)
  pretty_json "$RESPONSE"
done
echo -e "$SEPARATOR"

# =====================
# PRUEBA 4: POST /longtask (10 tareas pesadas)
# =====================
echo "🧠 [4] POST /longtask (10 tareas pesadas)"

for i in $(seq 1 10); do
  echo "➡️  Enviando tarea pesada #$i"
  RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
       -H "Authorization: $JWT_TOKEN" \
       -d "{\"task\": \"recalcular_modelo_$i\", \"heavy\": true}" \
       $ENDPOINT/longtask)
  pretty_json "$RESPONSE"
done
echo -e "$SEPARATOR"

# =====================
# PRUEBA 5: GET /tasks (total de tareas en cola)
# =====================
echo "📄 [5] GET /tasks (listado de todas las tareas en cola)"
RESPONSE=$(curl -s -H "Authorization: $JWT_TOKEN" $ENDPOINT/tasks)
pretty_json "$RESPONSE"
echo -e "$SEPARATOR"

# Espera 10 segundos
echo "Espera por 10 segundos..."
echo -e "$SEPARATOR"
sleep 10

# =====================
# PRUEBA 6: GET /tasks (total de tareas en cola)
# =====================
echo "📄 [6] GET /tasks (listado de todas las tareas en cola)"
RESPONSE=$(curl -s -H "Authorization: $JWT_TOKEN" $ENDPOINT/tasks)
pretty_json "$RESPONSE"
echo -e "$SEPARATOR"

# =====================
# PRUEBA 7: POST /cache/temp_key
# =====================
echo "📦 [7] POST /cache/temp_key"
RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
     -d '{"value": "dato temporal"}' \
     $CACHE_ENDPOINT/cache/temp_key)
pretty_json "$RESPONSE"
echo -e "$SEPARATOR"

# =====================
# PRUEBA 8: GET /cache/temp_key
# =====================
echo "🔍 [8] GET /cache/temp_key"
RESPONSE=$(curl -s $CACHE_ENDPOINT/cache/temp_key)
pretty_json "$RESPONSE"
echo -e "$SEPARATOR"

# =====================
# PRUEBA 9: DELETE /cache/temp_key
# =====================
echo "❌ [9] DELETE /cache/temp_key"
RESPONSE=$(curl -s -X DELETE $CACHE_ENDPOINT/cache/temp_key)
pretty_json "$RESPONSE"
echo -e "$SEPARATOR"

echo "✅ Todas las pruebas han finalizado."
