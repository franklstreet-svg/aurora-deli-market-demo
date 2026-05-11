# Aurora Deli & Market Source Of Truth

Last updated: May 10, 2026 - deployment readiness fixes

## Core Architecture

Aurora Deli & Market is a standalone customer-owned and customer-operated business website and operations system.

It is not connected to Orbi yet. It is not an Orbi-owned site, not an Orbi runtime, and not an Orbi-controlled business system. Treat it as the realistic customer business environment that existed before buying any outside automation product.

Do not touch Orbi core brain code while working in this project. Do not add Orbi, AI, receptionist, controller, scan, scanning, setup, or powered wording to customer-facing pages.

## Exact Project Root

```bash
/home/frank/projects/ORBI_AI_SOLUTIONS/Orbi_AI_ChatBrain/aurora_deli_market_demo
```

## Git State

- GitHub repo: `https://github.com/franklstreet-svg/aurora-deli-market-demo`
- Local remote: `origin https://github.com/franklstreet-svg/aurora-deli-market-demo.git`
- Current branch inspected: `main`
- Working tree inspected before this document update: clean

## Deployment State

- Frontend: deployed to Vercel and appears live.
- Backend: attempted on Render.
- Current Render issue addressed in code: backend now reads Render `PORT` first and binds to `0.0.0.0` when `PORT` is present.
- Remaining Render task: confirm the actual Render service URL and health result after push/deploy.
- Local backend port: `8126`
- Current local server command binds to `127.0.0.1` and reads `AURORA_DELI_PORT`, defaulting to `8126`.
- Backend deployment config: `render.yaml`
- Frontend/backend API config: same-origin by default; deployed frontend can set `window.AURORA_DELI_API_BASE`, `<meta name="aurora-deli-api-base">`, or `localStorage.auroraDeliApiBase`.

## Current Folders And Files

```text
aurora_deli_market_demo/
  .gitignore
  SOURCE_OF_TRUTH.md
  index.html
  render.yaml
  assets/
    css/
      styles.css
    js/
      business-api.js
  backend/
    __init__.py
    server.py
    storage.py
  data/
    .gitkeep
    audit_log.json
    business_settings.json
    catering_requests.json
    customer_messages.json
    inventory.json
    orders.json
    products.json
    reports_metrics.json
    staff_schedule.json
  pages/
    admin.html
    catering.html
    inventory.html
    menu.html
    messages.html
    order.html
    reports.html
    settings.html
    staff.html
```

## Backend Implementation

- Backend is lightweight Python using `http.server.ThreadingHTTPServer`.
- Main file: `backend/server.py`
- Storage helper: `backend/storage.py`
- Data storage: local JSON files in `data/`
- Static site serving is handled by the same backend when running locally.
- Local JSON writes are routed through `backend/storage.py`.
- `backend/storage.py` only accepts known store names from `SEED_DATA`.
- Atomic JSON writes use a temporary file inside `data/`, then `os.replace`.
- Static file serving resolves paths under the project root and blocks traversal outside the root.
- Deployment startup reads `PORT` first, then `AURORA_DELI_PORT`, then local default `8126`.
- Deployment host defaults to `0.0.0.0` when `PORT` is present and `127.0.0.1` for local runs.
- JSON API responses include CORS headers; API preflight supports `GET`, `POST`, `PATCH`, and `OPTIONS`.

## Run Commands

Run local backend:

```bash
cd /home/frank/projects/ORBI_AI_SOLUTIONS/Orbi_AI_ChatBrain/aurora_deli_market_demo
python3 backend/server.py
```

Run with explicit local port:

```bash
cd /home/frank/projects/ORBI_AI_SOLUTIONS/Orbi_AI_ChatBrain/aurora_deli_market_demo
AURORA_DELI_PORT=8126 python3 backend/server.py
```

Run with deployment-style env locally:

```bash
cd /home/frank/projects/ORBI_AI_SOLUTIONS/Orbi_AI_ChatBrain/aurora_deli_market_demo
PORT=8126 python3 backend/server.py
```

Local health check:

```bash
curl -s http://127.0.0.1:8126/health
```

Stop local foreground server:

```bash
Ctrl-C
```

Confirm local port is stopped:

```bash
ss -tlnp | grep 8126
```

## API Endpoints

- `GET /health`
- `GET /api/products`
- `GET /api/products/{id}`
- `PATCH /api/products/{id}`
- `GET /api/orders`
- `GET /api/orders/{id}`
- `POST /api/orders`
- `PATCH /api/orders/{id}`
- `GET /api/catering`
- `GET /api/catering/{id}`
- `POST /api/catering`
- `PATCH /api/catering/{id}`
- `GET /api/inventory`
- `GET /api/inventory/{id}`
- `PATCH /api/inventory/{id}`
- `GET /api/staff`
- `GET /api/staff/{id}`
- `POST /api/staff`
- `PATCH /api/staff/{id}`
- `GET /api/messages`
- `GET /api/messages/{id}`
- `POST /api/messages`
- `PATCH /api/messages/{id}`
- `GET /api/reports`
- `GET /api/settings`
- `PATCH /api/settings`
- `GET /api/audit-log`
- `GET /api/system-status`

## Frontend Connection State

The site still loads as a static storefront and operations UI.

Minimal backend wiring exists only where it was added safely:

- `pages/order.html` submits demo orders to `/api/orders` when the backend is available, with static fallback behavior if unavailable.
- `pages/catering.html` submits catering requests to `/api/catering` when the backend is available, with static fallback behavior if unavailable.
- `pages/reports.html` uses `assets/js/business-api.js` to hydrate report summary values from `/api/reports` when available.
- `pages/admin.html` uses `assets/js/business-api.js` to hydrate backend status details from `/api/system-status` when available.
- `assets/js/business-api.js` exposes `window.AuroraDeliAPI.url(path)` and `window.AuroraDeliAPI.getJSON(path)`.
- `pages/order.html` and `pages/catering.html` now use the shared API URL helper while keeping local same-origin fallback.

## Files Changed In Deployment Readiness Pass

- `backend/server.py` - normalized startup formatting, Render `PORT` handling, public host binding for deployment, CORS/preflight support, and invalid port validation.
- `render.yaml` - added Render web service config with `python3 backend/server.py` and `/health` health check.
- `assets/js/business-api.js` - added configurable backend base URL handling and shared API helper export.
- `pages/order.html` - loaded shared API helper and routed order submit calls through configurable API URL handling.
- `pages/catering.html` - loaded shared API helper and routed catering submit calls through configurable API URL handling.
- `SOURCE_OF_TRUTH.md` - updated deployment status, changed files, verification results, and next steps.

## Verification State

Completed backend phase verification recorded in the master handoff:

- Python compile checks passed.
- `assets/js/business-api.js` syntax check passed.
- Local link and asset resolver passed across all 10 HTML pages.
- Forbidden customer-facing wording scan passed.
- No-placeholder/TODO/coming-soon scan passed.
- HTTP checks passed for all 10 pages, CSS, JS, and `/health`.
- API read checks passed for all modules.
- Create/list/update curl tests passed for orders, catering, inventory, staff, messages, and settings.
- Persistence after restart was verified against local JSON data.
- Local backend server was stopped after testing.
- Port `8126` was confirmed not listening after shutdown.

Deployment readiness verification completed:

- `python3 -m py_compile backend/server.py backend/storage.py backend/__init__.py` passed.
- `node --check assets/js/business-api.js` passed.
- Local backend started on `127.0.0.1:8126`.
- `/health` returned `200` JSON.
- Static checks returned `200` for `index.html`, `pages/order.html`, `pages/admin.html`, `assets/css/styles.css`, and `assets/js/business-api.js`.
- Representative API reads passed for products, orders, reports, and system status.
- CORS preflight to `/api/orders` returned `204` with `Access-Control-Allow-Origin`, methods, and headers.
- Local link/asset resolver passed across all 10 HTML files.
- Forbidden customer-facing wording scan passed across all 10 HTML files.
- User-facing placeholder/TODO/coming-soon scan passed; the only match was a documentation phrase in this file.
- API write tests passed for creating and updating orders, catering requests, staff shifts, customer messages, inventory, and settings.
- Persistence after restart passed for QA-created order `ADM-1004`, catering request `CAT-2204`, staff shift `shift-007`, and message `MSG-3105`.
- QA-created JSON test records were restored before commit so deployment changes do not include test data.
- Local backend server was stopped after testing; port `8126` was confirmed not listening.

## Current Known Deployment Issue

Render backend deployment previously needed environment port binding work; code now supports Render-style `PORT` and public host binding.

Inspect and fix only when explicitly requested:

- Render usually provides `PORT`.
- Current code reads `PORT`, then `AURORA_DELI_PORT`, then defaults to `8126`.
- Current code binds `0.0.0.0` when `PORT` exists and `127.0.0.1` for local default runs.
- Next required deployment verification is checking the real Render `/health` URL after GitHub push/deploy.

## Next Steps

1. Commit and push deployment readiness changes to `origin main`.
2. Confirm Render redeploys from GitHub and check the real Render `/health` URL.
3. Set the deployed frontend backend base URL only after the Render backend URL is confirmed.
4. Re-test Vercel frontend against the deployed backend after backend health passes.
5. Keep all customer-facing pages free of Orbi/AI/receptionist/controller language.
6. Do not connect this project to Orbi until an explicit external attach phase begins.
