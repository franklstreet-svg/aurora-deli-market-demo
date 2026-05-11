# Aurora Deli & Market Source Of Truth

Last updated: May 10, 2026 - Vercel frontend verified against Render backend

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

- Frontend: verified live on Vercel at `https://aurora-deli-market-demo.vercel.app`.
- Backend: verified live on Render at `https://aurora-deli-market-demo.onrender.com`.
- Current Render issue addressed in code: backend now reads Render `PORT` first and binds to `0.0.0.0` when `PORT` is present.
- Render `/health` verified with HTTP 200 JSON.
- Render `/api/system-status` verified with HTTP 200 JSON.
- Render CORS preflight to `/api/orders` verified with HTTP 204.
- Live Vercel pages verified with HTTP 200: order, catering, reports, and admin.
- Live Vercel connected pages load `assets/js/deployment-config.js` before `assets/js/business-api.js`.
- Live Vercel to Render API verification created order `ADM-1004` and catering request `CAT-2204`.
- Local backend port: `8126`
- Current local server command binds to `127.0.0.1` and reads `AURORA_DELI_PORT`, defaulting to `8126`.
- Backend deployment config: `render.yaml`
- Frontend/backend API config: same-origin by default; deployed frontend now uses `assets/js/deployment-config.js` to set `window.AURORA_DELI_API_BASE` to the verified Render backend URL.

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
      deployment-config.js
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
- `assets/js/deployment-config.js` sets the deployed backend base URL to `https://aurora-deli-market-demo.onrender.com`.
- Connected pages load `deployment-config.js` before `business-api.js`: order, catering, reports, and admin.

## Live Deployment Verification Guidance

Render backend:

- Expected service name from `render.yaml`: `aurora-deli-market-demo`
- Verified backend URL: `https://aurora-deli-market-demo.onrender.com`
- Render start command: `python3 backend/server.py`
- Render health check path: `/health`
- Manual Render account setup if needed:
  1. Create a new Render Web Service from `https://github.com/franklstreet-svg/aurora-deli-market-demo`.
  2. Use branch `main`.
  3. Use environment `Python`.
  4. Use start command `python3 backend/server.py`.
  5. Use health check path `/health`.
  6. Confirm Render provides `PORT`; do not hardcode `8126` in Render.
  7. After deploy, verify `https://aurora-deli-market-demo.onrender.com/health`.

Vercel frontend:

- Verified production URL: `https://aurora-deli-market-demo.vercel.app`
- No Vercel environment variable is required for the current static deployment.
- Static frontend backend URL is committed in `assets/js/deployment-config.js`.
- If the Render URL changes, update `assets/js/deployment-config.js`, then commit and push.
- If replacing static config with Vercel environment variables later, add a real build-time injection step first; plain static HTML will not consume Vercel environment variables by itself.
- After Vercel redeploys from GitHub, verify the connected pages load `assets/js/deployment-config.js` before `assets/js/business-api.js`.

Final deployment checklist status:

1. Confirm GitHub `main` contains the latest deployment commit - done.
2. Confirm Render redeployed from GitHub `main` - done.
3. Check `https://aurora-deli-market-demo.onrender.com/health` - done, HTTP 200 JSON.
4. Check `https://aurora-deli-market-demo.onrender.com/api/system-status` - done, HTTP 200 JSON.
5. Check CORS preflight for `/api/orders` from the frontend origin - done, HTTP 204.
6. Confirm Vercel redeployed from GitHub `main` - done; production pages return HTTP 200.
7. Open Vercel frontend order page and submit a test pickup order - API equivalent done with Vercel origin; created `ADM-1004`.
8. Open Vercel frontend catering page and submit a test catering request - API equivalent done with Vercel origin; created `CAT-2204`.
9. Open Vercel reports page and confirm metrics hydrate from Render - page scripts verified and `/api/reports` returned live data from Render.
10. Open Vercel admin page and confirm backend status details hydrate from Render - page scripts verified and `/api/system-status` returned live data from Render.
11. Confirm no Orbi/AI/receptionist/controller wording appears in customer-facing pages - done.
12. Record the Vercel production URL here once provided or verified - done: `https://aurora-deli-market-demo.vercel.app`.

Note: local browser automation was not available in this environment (`playwright` and `puppeteer` are not installed). Verification used live HTTP page fetches, live frontend asset checks, CORS preflight, and live Render API calls with `Origin: https://aurora-deli-market-demo.vercel.app`.

## Files Changed In Deployment Readiness Pass

- `backend/server.py` - normalized startup formatting, Render `PORT` handling, public host binding for deployment, CORS/preflight support, and invalid port validation.
- `render.yaml` - added Render web service config with `python3 backend/server.py` and `/health` health check.
- `assets/js/business-api.js` - added configurable backend base URL handling and shared API helper export.
- `pages/order.html` - loaded shared API helper and routed order submit calls through configurable API URL handling.
- `pages/catering.html` - loaded shared API helper and routed catering submit calls through configurable API URL handling.
- `assets/js/deployment-config.js` - added verified Render backend URL for the static Vercel frontend.
- `pages/reports.html` - loads deployment config before the shared API helper.
- `pages/admin.html` - loads deployment config before the shared API helper.
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
- Live Render `/health` returned HTTP 200 JSON at `https://aurora-deli-market-demo.onrender.com/health`.
- Live Render `/api/system-status` returned HTTP 200 JSON.
- Live Render CORS preflight to `/api/orders` returned HTTP 204 with expected allow headers.
- `assets/js/deployment-config.js` syntax check passed.
- Connected page asset resolver passed after adding deployment config script tags.
- Live Vercel production URL verified: `https://aurora-deli-market-demo.vercel.app`.
- Live Vercel pages returned HTTP 200 for order, catering, reports, and admin.
- Live Vercel `assets/js/deployment-config.js` returns the verified Render backend URL.
- Live order page contains `deployment-config.js`, `business-api.js`, and configurable `/api/orders` submit logic.
- Live catering, reports, and admin pages contain the expected deployment/backend scripts.
- Live Render order create from Vercel origin succeeded and persisted as `ADM-1004`.
- Live Render catering create from Vercel origin succeeded and persisted as `CAT-2204`.
- Live Render reports API returned updated report data.
- Live Render system-status API confirmed orders and catering counts after live verification.

## Current Known Deployment Issue

Render backend deployment previously needed environment port binding work; code now supports Render-style `PORT` and public host binding, and the Render backend URL has been verified live.

Inspect and fix only when explicitly requested:

- Render usually provides `PORT`.
- Current code reads `PORT`, then `AURORA_DELI_PORT`, then defaults to `8126`.
- Current code binds `0.0.0.0` when `PORT` exists and `127.0.0.1` for local default runs.
- Remaining deployment verification: optional manual visual browser pass on the Vercel production site. Automated browser tooling was not installed locally.

## Next Steps

1. Commit and push this final frontend verification source-of-truth update to `origin main`.
2. Optionally run a manual visual browser pass on `https://aurora-deli-market-demo.vercel.app`.
3. Keep all customer-facing pages free of Orbi/AI/receptionist/controller language.
4. Do not connect this project to Orbi until an explicit external attach phase begins.
