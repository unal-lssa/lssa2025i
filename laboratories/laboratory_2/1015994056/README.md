# Implementación del Balanceador de Carga – LSSA Lab 2

## Objetivo
Agregar soporte para un nuevo tipo de componente arquitectónico: `load_balancer`, usando un enfoque de Model-Driven Software Engineering (MDE). El balanceador enruta el tráfico desde el `frontend` hacia uno o varios `backend` mediante `nginx`.

## Archivos modificados

### 1. `arch.tx`

Se extendió la gramática del DSL para soportar el nuevo tipo de componente:

```txt
ComponentType:
    'frontend' | 'backend' | 'database' | 'load_balancer';
```

**¿Por qué?**  
Para que la definición del modelo acepte componentes del tipo `load_balancer`.

---

### 2. `transformations.py`

- Se agregó la función `generate_load_balancer()` para generar un contenedor con `nginx` configurado como balanceador.
- Se modificó `apply_transformations()` para:
  - Detectar si hay un `load_balancer` en el modelo.
  - Enviar al `frontend` hacia el balanceador si está presente.
  - Configurar dinámicamente los destinos (`upstream`) en `nginx` usando los backends detectados.

**¿Por qué?**  
Para automatizar la generación de un proxy inverso con `nginx` que distribuya las peticiones del frontend.

---

### 3. `model.arch`

Se incluyó un nuevo componente `load_balancer` en el modelo y se definieron los conectores correspondientes:

```txt
component load_balancer lssa_lb
connector http lssa_fe -> lssa_lb
connector http lssa_lb -> lssa_be
```

**¿Por qué?**  
Para modelar explícitamente la arquitectura con balanceo de carga entre frontend y backend.

---

### 4. `docker-compose.yml`

Se agregó el servicio `lssa_lb` y se ajustaron los puertos expuestos de los servicios:

```yaml
lssa_lb:
  build: ./lssa_lb
  ports:
    - "8001:80"

lssa_fe:
  build: ./lssa_fe
  ports:
    - "8002:80"
```

**¿Por qué?**  
Para exponer el balanceador y el frontend en diferentes puertos locales, permitiendo el flujo `frontend → balanceador → backend`.

---

## Resultado final
- Se generó automáticamente un contenedor `nginx` que actúa como balanceador de carga.
- El frontend ahora se conecta al balanceador (`lssa_lb`), que enruta hacia el backend (`lssa_be`).
- La arquitectura es extensible a múltiples backends agregando más componentes y conectores.
