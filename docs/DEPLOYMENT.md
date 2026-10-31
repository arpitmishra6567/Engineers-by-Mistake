# RepairForge AI / Forge Command — Deployment Guide
## Deploying Backend to Railway & Frontend to Vercel

Forge Command is built with a cloud-native, decoupled architecture:
- **Frontend**: High-performance React 18 + Vite + Tailwind CSS SPA deployed to **Vercel** Edge Network.
- **Backend**: FastAPI ASGI service + RepairForge AI Harness containerized on **Railway** with dynamic port binding, health monitoring, and test reproduction capabilities.

---

## Architecture Overview

```
                      ┌────────────────────────────────────────────────┐
                      │                 USER BROWSER                   │
                      └──────────────────────┬─────────────────────────┘
                                             │
                       HTTPS Request         │  API Fetch calls
                       for Static SPA Assets │  (VITE_API_URL)
                                             ▼
                        ┌──────────────────────────────┐
                        │        VERCEL (SPA)          │
                        │  React 18 + Vite Production  │
                        │  Clean URLs & SPA Rewrites   │
                        │  Edge CDN Cache Control      │
                        └──────────────┬───────────────┘
                                       │
                                       │ HTTPS / JSON
                                       ▼
                        ┌──────────────────────────────┐
                        │       RAILWAY (BACKEND)      │
                        │  FastAPI + Uvicorn ASGI      │
                        │  Docker / Linux (Python 3.11)│
                        │  Dynamic $PORT Binding       │
                        │  RepairForge AI Core Harness │
                        │  Safe Isolation / Pytest     │
                        └──────────────────────────────┘
```

---

## 1. Deploy Backend to Railway

### Prerequisites
- A [Railway account](https://railway.app).
- The GitHub repository [`arpitmishra6567/Engineers-by-Mistake`](https://github.com/arpitmishra6567/Engineers-by-Mistake).

### Step-by-Step Instructions

1. **Create New Project in Railway**:
   - Navigate to the [Railway Dashboard](https://railway.app/dashboard).
   - Click **+ New Project** &rarr; Select **Deploy from GitHub repo**.
   - Choose `arpitmishra6567/Engineers-by-Mistake`.

2. **Automatic Build Detection**:
   - Railway automatically detects `railway.toml`, `railway.json`, and the root `Dockerfile`.
   - The deployment will use Python 3.11 with system `git` and test runners installed.

3. **Configure Environment Variables in Railway**:
   Go to the service's **Variables** tab in Railway and add the following:

   | Variable | Recommended Value | Description |
   |---|---|---|
   | `PORT` | *(Provided by Railway)* | Railway injects this automatically. The app dynamically binds to `${PORT:-8000}`. |
   | `HOST` | `0.0.0.0` | Listens on all interfaces within the container. |
   | `REPAIRFORGE_PROVIDER` | `mock` | Default deterministic provider (`mock` or `openai_compatible`). |
   | `REPAIRFORGE_MODEL` | `mock-repair-model` | Target model identifier. |
   | `CORS_ORIGINS` | `https://<your-app>.vercel.app` | Comma-separated list of custom frontend origins (optional; all `*.vercel.app` domains are allowed automatically). |
   | `REPAIRFORGE_API_KEY` | *(Optional)* | API Key if using `openai_compatible` model provider. |
   | `REPAIRFORGE_BASE_URL` | *(Optional)* | Model endpoint URL (e.g. `https://api.openai.com/v1`). |

4. **Generate Public Domain**:
   - In your Railway service settings, navigate to **Networking** &rarr; **Public Networking**.
   - Click **Generate Domain** (e.g. `https://engineers-by-mistake-production.up.railway.app`).

5. **Verify Backend Health**:
   - Check the health check endpoint:
     ```bash
     curl https://<your-railway-backend>.up.railway.app/api/health
     ```
     Expected response:
     ```json
     {
       "status": "ok",
       "version": "0.1.0",
       "app_name": "Forge Command",
       "project": "RepairForge AI"
     }
     ```
   - Interactive OpenAPI documentation is accessible at:
     `https://<your-railway-backend>.up.railway.app/docs`

---

## 2. Deploy Frontend to Vercel

### Prerequisites
- A [Vercel account](https://vercel.com).
- Your deployed Railway backend URL (from Section 1).

### Step-by-Step Instructions

1. **Import Project into Vercel**:
   - Go to the [Vercel Dashboard](https://vercel.com/dashboard).
   - Click **Add New...** &rarr; **Project**.
   - Select your GitHub repository `arpitmishra6567/Engineers-by-Mistake`.

2. **Configure Project Settings**:
   Vercel provides two deployment approaches (both are fully pre-configured):

   - **Approach A: Monorepo Root (Recommended)**:
     - Leave **Root Directory** as `./`.
     - Vercel will detect root `vercel.json` and automatically run:
       - Build Command: `cd frontend && npm install && npm run build`
       - Output Directory: `frontend/dist`
       - Framework: `Vite`

   - **Approach B: Frontend Directory**:
     - Set **Root Directory** to `frontend`.
     - Vercel will detect `frontend/vercel.json` and `frontend/package.json`.
     - Build Command: `npm run build`
     - Output Directory: `dist`

3. **Set Environment Variables in Vercel**:
   In the **Environment Variables** section of the Vercel setup screen, add:

   | Variable | Example Value | Description |
   |---|---|---|
   | `VITE_API_URL` | `https://<your-railway-backend>.up.railway.app` | The public URL of your Railway backend. Trailing slashes are automatically sanitized. |

4. **Deploy**:
   - Click **Deploy**.
   - Vercel will build TypeScript assets and deploy to the global Edge Network in ~30 seconds.

5. **Verify Frontend**:
   - Open your Vercel URL (e.g. `https://engineers-by-mistake.vercel.app`).
   - The **System Status** pill in the sidebar should glow green with **Core API: Online** and **Latency: XXms**.
   - Verify client-side SPA routing by navigating to `/new`, `/dashboard`, `/repairs`, `/evaluations` and refreshing the page.

---

## 3. Environment Variables Reference

### Backend (Railway)

| Key | Type | Default | Description |
|---|---|---|---|
| `PORT` | Integer | `8000` | Port for Uvicorn ASGI server (Railway overrides automatically). |
| `HOST` | String | `0.0.0.0` | Bind host IP address. |
| `CORS_ORIGINS` | String | `""` | Comma-separated list of explicitly permitted CORS origins. |
| `CORS_ORIGIN_REGEX` | String | `^https://.*\.vercel\.app$` | Regex matching permitted origins (enables all Vercel preview and production URLs). |
| `CORS_ALLOW_ALL` | Boolean | `false` | Set `true` to allow all origins (`*`). |
| `REPAIRFORGE_PROVIDER` | String | `mock` | Active model adapter (`mock` or `openai_compatible`). |
| `REPAIRFORGE_MODEL` | String | `mock-repair-model` | Active model identifier. |
| `REPAIRFORGE_API_KEY` | String | `""` | Optional LLM API key. Never exposed in API responses. |
| `REPAIRFORGE_BASE_URL` | String | `https://api.openai.com/v1` | Optional OpenAI-compatible endpoint URL. |
| `REPAIRFORGE_TIMEOUT` | Float | `30.0` | LLM HTTP request timeout in seconds. |
| `REPAIRFORGE_TEMPERATURE` | Float | `0.0` | LLM generation temperature. |
| `REPAIRFORGE_TIMEOUT_SECONDS`| Float | `60.0` | Subprocess test execution timeout. |
| `REPAIRFORGE_USE_DOCKER` | Boolean | `false` | Whether to isolate repairs inside container instances. |

### Frontend (Vercel)

| Key | Type | Default | Description |
|---|---|---|---|
| `VITE_API_URL` | String | `""` | Target backend URL (e.g. `https://your-backend.up.railway.app`). When empty, defaults to relative `/api` paths with local dev proxy. |

---

## 4. Local Development vs. Production Matrix

| Environment | Frontend URL | Backend URL | How API Requests are Routed |
|---|---|---|---|
| **Local Dev** | `http://localhost:5173` | `http://127.0.0.1:8000` | Vite dev proxy routes `/api/*` to `127.0.0.1:8000`. |
| **Production** | `https://<app>.vercel.app` | `https://<backend>.up.railway.app` | Direct client-to-backend HTTPS via `VITE_API_URL` with auto-permitted CORS. |
| **Unified Container** | `http://localhost:8000` | `http://localhost:8000` | FastAPI static files mount serves `frontend/dist` directly at root `/`. |

---

## 5. Pre-Flight Verification Checklist

Before pushing to production:

- [x] Backend tests pass: `pytest` (34/34 passing).
- [x] Frontend tests pass: `vitest run` (2/2 passing).
- [x] Frontend production build compiles: `tsc && vite build` (zero errors).
- [x] `Dockerfile` syntax verified with minimal layer caching and health check.
- [x] `railway.toml` and `railway.json` configured with healthcheck `/api/health`.
- [x] `Procfile` configured for alternative PaaS buildpacks.
- [x] `vercel.json` configured at both repository root and `frontend/` directory with SPA rewrites.
- [x] Dynamic `$PORT` binding in place (`${PORT:-8000}`).
- [x] Automatic Vercel CORS regex configured (`^https://.*\.vercel\.app$`).

