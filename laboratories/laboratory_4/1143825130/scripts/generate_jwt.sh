#!/bin/bash
# generate_jwt.sh
# Genera un JWT válido con algoritmo HS256 y clave 'secret'
# para pruebas locales en la arquitectura de microservicios.

# ====================
# CONFIGURACIÓN BÁSICA
# ====================
SECRET="secret"                              # Clave secreta (usada también en el API Gateway)
HEADER='{"alg":"HS256","typ":"JWT"}'         # Encabezado del JWT
EXPIRATION=$(( $(date +%s) + 3600 ))         # Token válido por 1 hora
PAYLOAD="{\"user\":\"tester\",\"exp\":$EXPIRATION}"

# ====================
# FUNCIONES AUXILIARES
# ====================
base64url_encode() {
  echo -n "$1" | openssl base64 -e | tr -d '=' | tr '+/' '-_' | tr -d '\n'
}

# ====================
# CONSTRUCCIÓN DEL TOKEN
# ====================
HEADER_B64=$(base64url_encode "$HEADER")
PAYLOAD_B64=$(base64url_encode "$PAYLOAD")
SIGNATURE=$(echo -n "$HEADER_B64.$PAYLOAD_B64" | openssl dgst -sha256 -hmac "$SECRET" -binary | openssl base64 -e | tr -d '=' | tr '+/' '-_' | tr -d '\n')

JWT="$HEADER_B64.$PAYLOAD_B64.$SIGNATURE"

# ====================
# SALIDA
# ====================
echo "✅ JWT generado exitosamente:"
echo
echo "$JWT"
echo
echo "Puedes copiar y usar este token como valor del header Authorization:"
echo "Authorization: $JWT"
