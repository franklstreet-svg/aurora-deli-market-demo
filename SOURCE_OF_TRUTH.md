# Aurora Deli & Market Source Of Truth

Last updated: May 10, 2026

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
- Current Render issue: backend likely needs a `PORT` environment binding check/fix.
- Local backend port: `8126`
- Current local server command binds to `127.0.0.1` and reads `AURORA_DELI_PORT`, defaulting to `8126`.
- No deployment logic was changed during this source-of-truth update.

## Current Folders And Files

```text
aurora_deli_market_demo/
  .gitignore
  SOURCE_OF_TRUTH.md
  index.html
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

## Current Known Deployment Issue

Render backend deployment likely needs environment port binding work.

Inspect and fix only when explicitly requested:

- Render usually provides `PORT`.
- Current local code reads `AURORA_DELI_PORT`.
- Current local code binds `ThreadingHTTPServer(("127.0.0.1", port), AuroraDeliHandler)`.
- The likely deployment fix is to bind to the host/port Render expects, without changing the standalone customer-business architecture.

## Next Steps

1. Inspect Render logs and environment variables.
2. Confirm whether Render is setting `PORT`.
3. Update backend binding only if needed for deployment.
4. Re-test local `8126` behavior after any Render compatibility change.
5. Re-test Vercel frontend against the deployed backend only after backend health passes.
6. Keep all customer-facing pages free of Orbi/AI/receptionist/controller language.
7. Do not connect this project to Orbi until an explicit external attach phase begins.
