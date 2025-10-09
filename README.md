# Atom LLM Local — guía actualizada

Estado del repositorio
- En este repositorio el único componente en código es el frontend (carpeta `frontend/`).
- No hay un "backend" propio en el repo. El flujo esperado es:
  Frontend (esta app) -> Anything LLM (gateway) -> LM Studio (servicio de inferencia)

Esta guía explica cómo arrancar el frontend (Docker o modo desarrollo) y cómo configurar Anything LLM / LM Studio como backend externo.

## Índice
- Requisitos
- Resumen del flujo
- Paso a paso: LM Studio + Anything LLM + Frontend
- Ejecutar el frontend (Docker o dev)
- Variables de entorno y comportamiento de Vite
- Payload de ejemplo y pruebas
- Opciones avanzadas (runtime env, dev in-docker)

---

## Requisitos

- Docker (opcional) — para construir/servir el frontend en un contenedor nginx
- Node.js (v20+) y npm — para ejecutar el frontend en modo desarrollo o para construir localmente
- Una instancia de Anything LLM (gateway) accesible por la app (local o remota)
- Una instancia de LM Studio que Anything LLM pueda usar como backend de inferencia (local o remota)

---

## Resumen del flujo

1. Asegúrate de que LM Studio ejecuta el modelo de inferencia que necesitas (anota su endpoint y credenciales si aplica).
2. Configura Anything LLM para usar LM Studio como su backend de inferencia (o registra el endpoint/modelo en Anything LLM según su guía).
3. Verifica que Anything LLM expone una API usable por clientes (URL y API key).
4. Configura el frontend con la API key / URL de Anything LLM y arranca el frontend (Docker o dev).

---

## Paso a paso

### 1) Ejecutar LM Studio (modelo)

- Inicia tu instancia de LM Studio y carga el modelo que quieras usar. Anota la URL y el puerto de inferencia (ej. `http://localhost:8080`) y cualquier credencial necesaria.

### 2) Configurar Anything LLM (gateway)

- En la UI o configuración de Anything LLM registra el endpoint de LM Studio como backend del modelo (o configura el adaptador apropiado). Asegúrate de que Anything LLM puede enviar solicitudes de inferencia a LM Studio.
- Anota la URL donde Anything LLM expone su API y la API key (si aplica). Ejemplo conceptual de URL: `http://localhost:3001`.

### 3) Probar Anything LLM

Prueba el endpoint de Anything LLM con curl o Postman para validar que responde correctamente. Ejemplo (ajusta según tu gateway):

```bash
curl -X POST 'http://localhost:3001/api/v1/workspace/rag/chat' \
  -H 'Authorization: Bearer YOUR_ANYTHING_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"message":"Hola"}'
```

Si recibes respuesta (JSON), Anything LLM está listo.

### 4) Configurar y arrancar el frontend

- En `frontend/.env` añade la API key que el frontend usará para autenticar contra Anything LLM (ejemplo):

```
VITE_ANYTHING_LLM_API_KEY=your_anything_api_key_here
VITE_ANYTHING_LLM_URL=http://localhost:3001
```

- Arrancar el frontend (opciones en la siguiente sección).

---

## Ejecutar el frontend

Opciones disponibles:

- Opción 1 — Docker (build estático y servir con nginx):

  1. Asegúrate de tener `frontend/.env` con `VITE_ANYTHING_LLM_API_KEY` si quieres que esa clave quede embebida en el build.
  2. Desde la raíz del repo:

  ```powershell
  docker compose up -d --build frontend
  ```

  3. Abre http://localhost:3000

- Opción 2 — Desarrollo local (hot-reload, sin Docker):

  ```powershell
  cd frontend
  npm install
  npm run dev -- --host
  ```

  La salida de Vite mostrará la URL local (por defecto `http://localhost:5173`) — con `--host` también será accesible desde otras máquinas en la red.

---

## Variables de entorno relevantes

- `VITE_ANYTHING_LLM_API_KEY` — clave que el frontend enviará en el header `Authorization: Bearer ...` hacia Anything LLM. Debe colocarse en `frontend/.env` antes de construir cuando uses Docker.
- `VITE_ANYTHING_LLM_URL` — (opcional) URL base del gateway Anything LLM (por defecto el frontend hace fetch a `http://localhost:3001/api/v1/workspace/rag/chat` en el código actual). Si cambias la URL, actualiza el código o define esta variable y lee `import.meta.env.VITE_ANYTHING_LLM_URL` en el frontend.

Nota: Vite inyecta variables `VITE_*` en build time. Si construyes la imagen Docker con `npm run build`, las variables deben existir antes del build para quedar embebidas en los assets. Si necesitas cambiarlas sin rebuild, usa la sección "Opciones avanzadas".

---

## Payload de ejemplo (qué envía el frontend)

El frontend, en el archivo `frontend/src/views/Home.vue`, envía una petición POST JSON al gateway con el siguiente shape (actual):

Request:

- URL (ejemplo): `http://localhost:3001/api/v1/workspace/rag/chat`
- Headers:
  - `Authorization: Bearer <VITE_ANYTHING_LLM_API_KEY>`
  - `Content-Type: application/json`
- Body (JSON):

```json
{ "message": "texto del usuario" }
```

Respuesta esperada (ejemplo):

```json
{
  "textResponse": "Respuesta generada por el modelo"
}
```

Si tu gateway usa nombres de campos diferentes, ajusta la llamada en `frontend/src/views/Home.vue` para mapear la respuesta apropiadamente.

---

## Depuración rápida

- Verifica LM Studio (modelo) responde en su endpoint antes de configurar Anything LLM.
- Verifica Anything LLM con curl/Postman usando la API key.
- Errores comunes:
  - `process is not defined` — usa `import.meta.env.VITE_*` en el frontend y define las variables en `frontend/.env` antes del build.
  - `Cannot read properties of null` — elementos comentados o ausentes en la plantilla; revisa `frontend/src/views/Home.vue`.

---

## Opciones avanzadas

- Si necesitas cambiar la API key o URL sin reconstruir la imagen Docker (runtime env), puedo añadir un entrypoint que genere un pequeño `config.js` a partir de variables de entorno y lo copie en `usr/share/nginx/html` antes de arrancar nginx. Dime si lo implemento.
- Para desarrollo dentro de Docker (hot-reload) puedo añadir un servicio `frontend-dev` en `docker-compose.yml` que monte el código y ejecute `npm run dev`.

---

Si quieres, adapto el README con ejemplos exactos de payloads que espera tu Anything LLM (por ejemplo el shape JSON: { message, contents, etc. }) si me pasas la especificación del API o un ejemplo de respuesta.
