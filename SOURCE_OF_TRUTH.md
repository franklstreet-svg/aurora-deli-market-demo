# PurBlum Source Of Truth

Last updated: May 11, 2026 - Public storefront deploy source fixed

## Core Architecture

PurBlum is a standalone customer-owned and customer-operated business website and operations system.

It is not connected to Orbi yet. It is not an Orbi-owned site, not an Orbi runtime, and not an Orbi-controlled business system. Treat it as the realistic customer business environment that existed before buying any outside automation product.

Do not touch Orbi core brain code while working in this project. Do not add Orbi, AI, receptionist, controller, scan, scanning, setup, or powered wording to customer-facing pages.

Current public website scope: storefront home, menu/products, pickup order request, catering request, contact/location/hours, customer help, and safe public availability language only. Internal business OS pages remain in the repo for future gated/admin products, but they are removed from public navigation and visually gated when opened directly.

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

- Phase 1 rebrand status: customer-facing frontend and business display name changed from Aurora Deli to `PurBlum`; functionality, backend routes, API paths, deployment URLs, and local project path were kept unchanged.
- Frontend: verified live on Vercel at `https://aurora-deli-market-demo.vercel.app`.
- Planned custom domain: `purblum.com`.
- Planned `www` custom domain: `www.purblum.com`.
- Custom domain connection status: manual Vercel and GoDaddy steps still required.
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
- Current live Vercel/Render service names still contain the legacy `aurora-deli-market-demo` slug; this is deployment naming only and was intentionally not changed in Phase 1.

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
    contact.html
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

The site now loads as a static public storefront. Internal operations pages still exist in the repo, but they are not public storefront surfaces.

Minimal backend wiring exists only where it was added safely:

- `pages/order.html` submits demo orders to `/api/orders` when the backend is available, with static fallback behavior if unavailable.
- `pages/catering.html` submits catering requests to `/api/catering` when the backend is available, with static fallback behavior if unavailable.
- `pages/reports.html` and `pages/admin.html` remain in the repo, but are visually gated as private workspace pages and no longer hydrate internal APIs while gated.
- `assets/js/business-api.js` exposes `window.AuroraDeliAPI.url(path)` and `window.AuroraDeliAPI.getJSON(path)`.
- `pages/order.html` and `pages/catering.html` now use the shared API URL helper while keeping local same-origin fallback.
- `assets/js/deployment-config.js` sets the deployed backend base URL to `https://aurora-deli-market-demo.onrender.com`.
- Connected pages load `deployment-config.js` before `business-api.js`: order, catering, reports, and admin.

## Public Storefront Refocus

Completed May 11, 2026:

- Public navigation now exposes only `Home`, `Menu`, `Order`, `Catering`, and `Contact`.
- Public footer links now expose only customer-facing pages.
- The homepage business-systems section was replaced with customer help links for menu, pickup order request, catering request, and store contact.
- Added `pages/contact.html` for customer help, hours, location, phone/email, pickup help, catering help, and public availability questions.
- Internal pages are not deleted, but are hidden/gated from public UI:
  - `pages/admin.html`
  - `pages/settings.html`
  - `pages/reports.html`
  - `pages/staff.html`
  - `pages/messages.html`
  - `pages/inventory.html`
- Internal pages now include `noindex,nofollow`, a private-workspace notice, public navigation only, public footer links only, and hidden dashboard `<main>` content for public/direct browser visits.
- `assets/js/business-api.js` now skips report/admin hydration on gated internal pages so direct public visits do not call internal report/admin status APIs.
- Backend routes, JSON data, internal modules, and business API behavior were not deleted. They remain available for future gated admin/business product work.

Files changed in public storefront refocus:

- `index.html`
- `pages/menu.html`
- `pages/order.html`
- `pages/catering.html`
- `pages/contact.html`
- `pages/inventory.html`
- `pages/staff.html`
- `pages/messages.html`
- `pages/reports.html`
- `pages/settings.html`
- `pages/admin.html`
- `assets/css/styles.css`
- `assets/js/business-api.js`
- `SOURCE_OF_TRUTH.md`

Public storefront refocus verification:

- Public header/footer scan passed: no public header/footer links to `admin`, `settings`, `reports`, `staff`, `messages`, or `inventory`.
- Local link/asset resolver passed across all HTML pages.
- `node --check assets/js/business-api.js` passed.
- `python3 -m py_compile backend/server.py backend/storage.py` passed.
- HTTP checks on temporary port `8128` returned `200 OK` for `/`, `pages/menu.html`, `pages/order.html`, `pages/catering.html`, `pages/contact.html`, and `assets/css/styles.css`.
- Temporary server on port `8128` was stopped after testing.
- `ss -tlnp` confirmed port `8128` was not listening after shutdown.
- Generated `__pycache__` folders were removed after compile checks.

## Live Public UI Source Fix

Completed May 11, 2026:

- Inspected the PurBlum project source at `/home/frank/projects/ORBI_AI_SOLUTIONS/Orbi_AI_ChatBrain/aurora_deli_market_demo`.
- Inspected the Orbi marketing export at `/home/frank/projects/bridge_website_factory/13_EXPORTS/orbi_ai/live`; that folder is the Orbi AI Solutions marketing site, not the PurBlum storefront deploy source.
- Confirmed the PurBlum Vercel deployment source is the GitHub repo root for `https://github.com/franklstreet-svg/aurora-deli-market-demo`; there is no separate local `dist`, `public`, `vercel.json`, or build output folder in this project.
- Identified the remaining live issue: the storefront refocus existed locally but had not yet been committed and pushed to `origin/main`, so Vercel could still serve the previous committed version after refresh.
- Cleaned `assets/js/business-api.js` so public order/catering pages no longer load report/admin hydration code.

Files changed in live public UI source fix:

- `assets/js/business-api.js`
- `SOURCE_OF_TRUTH.md`
- `/home/frank/projects/ORBI_AI_SOLUTIONS/ORBI_HANDOFF.md`

Verification:

- Source public HTML scan passed: no `href` links or visible nav/footer tabs for `admin`, `settings`, `reports`, `staff`, `messages`, or `inventory` in `index.html`, `pages/menu.html`, `pages/order.html`, `pages/catering.html`, or `pages/contact.html`.
- Source public HTML/JS scan passed for internal UI words; the only remaining public-page matches were `POST` request methods in order/catering scripts, a false positive for the `POS` substring.
- `node --check assets/js/business-api.js` passed.
- `node --check assets/js/deployment-config.js` passed.
- `python3 -m py_compile backend/server.py backend/storage.py` passed.
- Local link/asset resolver passed across all HTML pages.
- Temporary static server on port `8128` returned `200 OK` for `/`, `pages/menu.html`, `pages/order.html`, `pages/catering.html`, `pages/contact.html`, and `assets/js/business-api.js`.
- Temporary server was stopped; `ss -tlnp` confirmed no listener on `8128`.

## Phase 1 PurBlum Rebrand

Completed scope:

- Rebranded customer-facing visible frontend text across all 10 HTML pages from Aurora Deli / Aurora Deli & Market to `PurBlum`.
- Updated page titles, meta descriptions, header brand labels, footer labels, aria homepage labels, catering confirmation text, and the visible brand mark from `A` to `P`.
- Updated `data/business_settings.json` business display name to `PurBlum`.
- Kept deli/market/catering operations language where it describes the business type or products.
- Kept backend routes, API paths, order ID prefixes, deployment service names, Render URL, Vercel URL, and `AURORA_DELI_API_BASE` internal variable names unchanged to avoid breaking deployment behavior.

Files changed in Phase 1:

- `index.html`
- `pages/menu.html`
- `pages/order.html`
- `pages/catering.html`
- `pages/inventory.html`
- `pages/staff.html`
- `pages/messages.html`
- `pages/reports.html`
- `pages/settings.html`
- `pages/admin.html`
- `data/business_settings.json`
- `SOURCE_OF_TRUTH.md`

Phase 1 verification:

- `python3 -m py_compile backend/server.py backend/storage.py backend/__init__.py` passed.
- `node --check assets/js/business-api.js` and `node --check assets/js/deployment-config.js` passed.
- Local link/asset resolver passed across all 10 HTML files.
- Customer-facing forbidden wording scan passed across all 10 HTML files.
- Customer-facing old-brand scan passed across all 10 HTML files and `data/business_settings.json`.
- Local HTTP checks returned `200 OK` for all 10 HTML pages and `assets/css/styles.css` on port `8126`.
- Local `/api/settings` returned `"business_name": "PurBlum"`.
- Local backend server was stopped after testing; port `8126` was confirmed not listening.
- Live Render `/health` returned HTTP 200 JSON.
- Git diff review confirmed Phase 1 changes are limited to frontend HTML, `data/business_settings.json`, and this source-of-truth file.

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
- Planned production custom domains: `https://purblum.com` and `https://www.purblum.com`
- No Vercel environment variable is required for the current static deployment.
- Static frontend backend URL is committed in `assets/js/deployment-config.js`.
- If the Render URL changes, update `assets/js/deployment-config.js`, then commit and push.
- If replacing static config with Vercel environment variables later, add a real build-time injection step first; plain static HTML will not consume Vercel environment variables by itself.
- After Vercel redeploys from GitHub, verify the connected pages load `assets/js/deployment-config.js` before `assets/js/business-api.js`.

Custom domain connection for `purblum.com`:

Vercel dashboard steps:

1. Open Vercel dashboard.
2. Open the PurBlum project that currently serves `https://aurora-deli-market-demo.vercel.app`.
3. Go to `Settings` -> `Domains`.
4. Add `purblum.com`.
5. Add `www.purblum.com`.
6. In the Vercel domain settings, choose which domain is primary:
   - Recommended: make `purblum.com` primary and redirect `www.purblum.com` to it.
   - Acceptable alternative: make `www.purblum.com` primary and redirect `purblum.com` to it.
7. Use Vercel's domain screen to verify the exact DNS values. Vercel's current general-purpose values are listed below, but if the dashboard shows project-specific values, use the dashboard values.

Expected GoDaddy DNS records:

| Type | Name / Host | Value / Points to | TTL |
|------|-------------|-------------------|-----|
| A | `@` | `76.76.21.21` | Default / 1 hour |
| CNAME | `www` | `cname.vercel-dns-0.com` | Default / 1 hour |

Important DNS cleanup:

- Remove any conflicting `A`, `AAAA`, or `CNAME` records for `@`.
- Remove any conflicting `A`, `AAAA`, or `CNAME` records for `www`.
- Do not change nameservers unless intentionally moving DNS hosting to Vercel.
- If GoDaddy has CAA records on the domain, allow Let's Encrypt by adding or preserving a CAA record: `0 issue "letsencrypt.org"`.

GoDaddy steps:

1. Sign in to GoDaddy.
2. Open `My Products`.
3. Find `purblum.com`.
4. Open `DNS` or `Manage DNS`.
5. In `Records`, edit or add the apex/root record:
   - Type: `A`
   - Name: `@`
   - Value: `76.76.21.21`
   - TTL: default or 1 hour
6. Edit or add the `www` record:
   - Type: `CNAME`
   - Name: `www`
   - Value: `cname.vercel-dns-0.com`
   - TTL: default or 1 hour
7. Save the DNS changes.
8. Return to Vercel `Settings` -> `Domains` and click refresh/check if available.

Expected propagation:

- Often visible in 5-30 minutes.
- Can take up to 24-48 hours depending on DNS cache and previous records.
- Vercel SSL certificate provisioning usually starts automatically after DNS verifies and typically completes within a few minutes.

Expected final behavior:

- `https://purblum.com` should serve the PurBlum Vercel frontend.
- `https://www.purblum.com` should also work if both domains are added in Vercel.
- One of root or `www` should be configured as the primary domain in Vercel, with the other redirecting to it to avoid duplicate content.

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
13. Add `purblum.com` and `www.purblum.com` in Vercel project domain settings - manual step pending.
14. Add GoDaddy DNS records for apex and `www` - manual step pending.
15. Verify Vercel marks both custom domains valid and provisions SSL - manual step pending.
16. Test `https://purblum.com` and `https://www.purblum.com` after propagation - manual step pending.

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
- Vercel custom-domain DNS guidance recorded for `purblum.com`.

## Current Known Deployment Issue

Render backend deployment previously needed environment port binding work; code now supports Render-style `PORT` and public host binding, and the Render backend URL has been verified live.

Inspect and fix only when explicitly requested:

- Render usually provides `PORT`.
- Current code reads `PORT`, then `AURORA_DELI_PORT`, then defaults to `8126`.
- Current code binds `0.0.0.0` when `PORT` exists and `127.0.0.1` for local default runs.
- Remaining deployment verification: optional manual visual browser pass on the Vercel production site. Automated browser tooling was not installed locally.
- Remaining custom-domain work: manually add `purblum.com` and `www.purblum.com` to the Vercel project, update GoDaddy DNS, wait for propagation, then verify both HTTPS domains.

## Next Steps

1. Commit and push this final frontend verification source-of-truth update to `origin main`.
2. Add `purblum.com` and `www.purblum.com` to the Vercel project.
3. Add the required DNS records in GoDaddy.
4. Wait for DNS propagation and Vercel SSL provisioning.
5. Verify `https://purblum.com` and `https://www.purblum.com`.
6. Optionally run a manual visual browser pass on `https://aurora-deli-market-demo.vercel.app` and the custom domain.
7. Keep all customer-facing pages free of Orbi/AI/receptionist/controller language.
8. Do not connect this project to Orbi until an explicit external attach phase begins.
