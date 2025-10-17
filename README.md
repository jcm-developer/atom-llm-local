# 🤖 Atom LLM Local — Updated Guide

## 📂 Repository Status
- This repository contains only the frontend component (folder `frontend/`) 🎨
- There's no proprietary "backend" in the repo. The expected flow is:
  Frontend (this app) -> Anything LLM (gateway) -> LM Studio (inference service) 🔄

This guide explains how to start the frontend (Docker or development mode) and how to configure Anything LLM / LM Studio as external backend.

## 📋 Table of Contents
- 📋 Requirements
- 🔄 Flow Summary
- 📝 Step by Step: LM Studio + Anything LLM + Frontend
- 🚀 Running the Frontend (Docker or dev)
- 🌍 Environment Variables and Vite Behavior
- 📦 Example Payload and Testing
- ⚙️ Advanced Options (runtime env, dev in-docker)

---

## 📋 Requirements

- 🐳 Docker (optional) — to build/serve the frontend in an nginx container
- 📦 Node.js (v20+) and npm — to run the frontend in development mode or build locally
- 🌐 An Anything LLM instance (gateway) accessible by the app (local or remote)
- 🖥️ An LM Studio instance that Anything LLM can use as inference backend (local or remote)

---

## 🔄 Flow Summary

1. 🚀 Ensure LM Studio is running the inference model you need (note its endpoint and credentials if applicable).
2. ⚙️ Configure Anything LLM to use LM Studio as its inference backend (or register the endpoint/model in Anything LLM according to its guide).
3. ✅ Verify that Anything LLM exposes an API usable by clients (URL and API key).
4. 🎯 Configure the frontend with the API key / URL from Anything LLM and start the frontend (Docker or dev).

---

## 📝 Step by Step

### 1) 🚀 Run LM Studio (model)

- Start your LM Studio instance and load the model you want to use. Note the URL and inference port (e.g. `http://localhost:8080`) and any necessary credentials.

### 2) ⚙️ Configure Anything LLM (gateway)

- In the Anything LLM UI or configuration, register the LM Studio endpoint as the model backend (or configure the appropriate adapter). Make sure Anything LLM can send inference requests to LM Studio.
- Note the URL where Anything LLM exposes its API and the API key (if applicable). Conceptual URL example: `http://localhost:3001`.

### 3) 🧪 Test Anything LLM

Test the Anything LLM endpoint with curl or Postman to validate it responds correctly. Example (adjust according to your gateway):

```bash
curl -X POST 'http://localhost:3001/api/v1/workspace/rag/chat' \
  -H 'Authorization: Bearer YOUR_ANYTHING_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"message":"Hello"}'
```

If you receive a response (JSON), Anything LLM is ready. ✅

### 4) ⚙️ Configure and Start the Frontend

- In `frontend/.env` add the API key that the frontend will use to authenticate against Anything LLM (example):

```
VITE_ANYTHING_LLM_API_KEY=your_anything_api_key_here
VITE_ANYTHING_LLM_URL=http://localhost:3001
```

- Start the frontend (options in the next section). 🚀

---

## 🚀 Running the Frontend

Available options:

- **Option 1** — 🐳 Docker (static build and serve with nginx):

  1. Make sure you have `frontend/.env` with `VITE_ANYTHING_LLM_API_KEY` if you want that key embedded in the build.
  2. From the repo root:

  ```powershell
  docker compose up -d --build frontend
  ```

  3. Open http://localhost:3000 🌐

- **Option 2** — 💻 Local Development (hot-reload, without Docker):

  ```powershell
  cd frontend
  npm install
  npm run dev -- --host
  ```

  Vite's output will show the local URL (default `http://localhost:5173`) — with `--host` it will also be accessible from other machines on the network. 🌍

---

## 🌍 Relevant Environment Variables

- `VITE_ANYTHING_LLM_API_KEY` — key that the frontend will send in the `Authorization: Bearer ...` header to Anything LLM. Must be placed in `frontend/.env` before building when using Docker.
- `VITE_ANYTHING_LLM_URL` — (optional) Base URL of the Anything LLM gateway (by default the frontend fetches to `http://localhost:3001/api/v1/workspace/rag/chat` in the current code). If you change the URL, update the code or define this variable and read `import.meta.env.VITE_ANYTHING_LLM_URL` in the frontend.
- `VITE_OPENAI_API_KEY` — 🆕 OpenAI API key to use ChatGPT as an alternative model. Required only if you want to use the ChatGPT toggle button.

**Note:** Vite injects `VITE_*` variables at build time. If you build the Docker image with `npm run build`, the variables must exist before the build to be embedded in the assets. If you need to change them without rebuild, use the "Advanced Options" section. ⚠️

---

## 🔄 Model Toggle Feature

The frontend now includes a **model toggle button** that allows you to switch between:
- 🌐 **ChatGPT (Open Model)**: Uses OpenAI's API for responses
- 💻 **Local Model (Private)**: Uses your local Anything LLM + LM Studio setup with file support

**How to use:**
1. Click the cloud icon (☁️) button in the prompt area to toggle between models
2. When **active** (blue gradient): Using ChatGPT API
3. When **inactive** (glass effect): Using Local Model
4. The icon changes to reflect the current model (cloud ☁️ for ChatGPT, computer 💻 for local)

**Configuration:**
- Copy `frontend/.env.example` to `frontend/.env`
- Add your `VITE_OPENAI_API_KEY` to enable ChatGPT functionality
- The local model configuration remains unchanged

---

## 📦 Example Payload (what the frontend sends)

The frontend, in the file `frontend/src/views/Home.vue`, sends a POST JSON request to the gateway with the following shape (current):

**Request:**

- URL (example): `http://localhost:3001/api/v1/workspace/rag/chat`
- Headers:
  - `Authorization: Bearer <VITE_ANYTHING_LLM_API_KEY>`
  - `Content-Type: application/json`
- Body (JSON):

```json
{ "message": "user text" }
```

**Expected Response (example):**

```json
{
  "textResponse": "Response generated by the model"
}
```

If your gateway uses different field names, adjust the call in `frontend/src/views/Home.vue` to map the response appropriately. 🔧

---

## 🔍 Quick Debugging

- ✅ Verify LM Studio (model) responds at its endpoint before configuring Anything LLM.
- ✅ Verify Anything LLM with curl/Postman using the API key.
- Common errors:
  - `process is not defined` — use `import.meta.env.VITE_*` in the frontend and define the variables in `frontend/.env` before build.
  - `Cannot read properties of null` — commented or missing elements in the template; check `frontend/src/views/Home.vue`.

---

## ⚙️ Advanced Options

- If you need to change the API key or URL without rebuilding the Docker image (runtime env), I can add an entrypoint that generates a small `config.js` from environment variables and copies it to `usr/share/nginx/html` before starting nginx. Let me know if you want me to implement this. 🛠️
- For development inside Docker (hot-reload) I can add a `frontend-dev` service in `docker-compose.yml` that mounts the code and runs `npm run dev`. 🔄
