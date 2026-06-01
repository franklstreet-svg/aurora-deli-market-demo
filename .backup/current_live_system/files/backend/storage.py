from __future__ import annotations

import json
import os
import tempfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


SEED_DATA: dict[str, Any] = {
    "products": [
        {"id": "sandwich-sierra-turkey", "name": "Sierra Turkey Club", "category": "sandwiches", "price": 12.95, "available": True, "description": "Turkey, bacon, avocado, romaine, tomato, and pepper aioli."},
        {"id": "sandwich-truckee-italian", "name": "Truckee Italian", "category": "sandwiches", "price": 13.50, "available": True, "description": "Ham, salami, capicola, provolone, pepper relish, lettuce, tomato, and oregano vinaigrette."},
        {"id": "sandwich-roast-beef", "name": "Reno Roast Beef", "category": "sandwiches", "price": 14.25, "available": True, "description": "Roast beef, cheddar, horseradish cream, onion, arugula, and toasted roll."},
        {"id": "soup-chicken-wild-rice", "name": "Chicken & Wild Rice Soup", "category": "soups", "price": 8.50, "available": True, "description": "Chicken, vegetables, wild rice, thyme, and deli broth."},
        {"id": "salad-market-chopped", "name": "Market Chopped Salad", "category": "salads", "price": 11.75, "available": True, "description": "Romaine, cucumber, tomato, chickpeas, provolone, salami, olives, and red wine vinaigrette."},
        {"id": "side-pasta-salad", "name": "Deli Pasta Salad Pint", "category": "sides", "price": 6.50, "available": True, "description": "Rotini, roasted peppers, mozzarella pearls, olives, parsley, and house Italian dressing."},
        {"id": "drink-house-tea", "name": "House Iced Tea", "category": "drinks", "price": 3.25, "available": True, "description": "Unsweetened black tea, peach tea, or lemonade tea."},
        {"id": "market-kettle-chips", "name": "Tahoe Kettle Chips", "category": "market", "price": 2.95, "available": True, "description": "Sea salt, jalapeno, barbecue, or vinegar."},
        {"id": "bakery-cookie-box", "name": "House Cookie Box", "category": "bakery", "price": 8.95, "available": True, "description": "Six rotating bakery cookies packed to go."},
    ],
    "inventory": [
        {"id": "inv-turkey", "name": "Roasted Turkey Breast", "category": "Deli meats", "quantity": 18, "unit": "lb", "par": 30, "supplier": "Sierra Provisions", "reorder_status": "needed", "expires": "2026-05-12"},
        {"id": "inv-salami", "name": "Genoa Salami", "category": "Deli meats", "quantity": 11, "unit": "lb", "par": 18, "supplier": "Sierra Provisions", "reorder_status": "needed", "expires": "2026-05-18"},
        {"id": "inv-sourdough", "name": "Sourdough Loaves", "category": "Bakery", "quantity": 42, "unit": "loaves", "par": 40, "supplier": "Truckee River Bakery", "reorder_status": "hold", "expires": "2026-05-11"},
        {"id": "inv-tomato-bisque", "name": "Tomato Basil Bisque", "category": "Soup", "quantity": 8, "unit": "qt", "par": 10, "supplier": "In-house prep", "reorder_status": "prep", "expires": "2026-05-10"},
        {"id": "inv-kettle-chips", "name": "Tahoe Kettle Chips", "category": "Market", "quantity": 22, "unit": "bags", "par": 48, "supplier": "Tahoe Snacks", "reorder_status": "needed", "expires": "2026-09-01"},
        {"id": "inv-cookie-trays", "name": "Catering Cookie Trays", "category": "Catering", "quantity": 3, "unit": "trays", "par": 8, "supplier": "In-house bakery", "reorder_status": "prep", "expires": "2026-05-11"},
    ],
    "orders": [
        {"id": "ADM-1048", "customer_name": "Janelle Price", "phone": "(775) 555-0188", "type": "pickup", "status": "ready", "pickup_time": "2026-05-10T12:30:00-07:00", "items": [{"product_id": "sandwich-sierra-turkey", "name": "Sierra Turkey Club", "quantity": 2, "price": 12.95}], "subtotal": 25.90, "tax": 2.14, "total": 28.04, "notes": "Add napkins."}
    ],
    "catering_requests": [
        {"id": "CAT-2201", "customer_name": "Reno Design Co.", "phone": "(775) 555-0137", "email": "events@example.com", "package": "Classic Sandwich Tray", "guest_count": 42, "event_time": "2026-05-15T11:30:00-07:00", "service_type": "delivery", "status": "quote_sent", "priority": "high", "estimated_total": 567.00}
    ],
    "staff_schedule": [
        {"id": "shift-001", "employee": "Maya Chen", "role": "Manager", "date": "2026-05-10", "start": "06:30", "end": "15:00", "coverage": "opening"},
        {"id": "shift-002", "employee": "Luis Ortega", "role": "Kitchen lead", "date": "2026-05-10", "start": "07:00", "end": "15:30", "coverage": "prep"},
        {"id": "shift-003", "employee": "Priya Shah", "role": "Deli counter", "date": "2026-05-10", "start": "10:00", "end": "18:00", "coverage": "lunch"},
        {"id": "shift-004", "employee": "Theo Martin", "role": "Closer", "date": "2026-05-10", "start": "12:00", "end": "20:30", "coverage": "closing"},
    ],
    "customer_messages": [
        {"id": "MSG-3101", "customer_name": "Nora Bell", "source": "web", "subject": "Boxed lunches for 42", "status": "awaiting_quote", "priority": "high", "assigned_staff": "Maya Chen", "notes": "Needs vegetarian count by Wednesday."},
        {"id": "MSG-3102", "customer_name": "Janelle Price", "source": "phone", "subject": "Missing chips from pickup", "status": "unresolved", "priority": "medium", "assigned_staff": "Theo Martin", "notes": "Offer replacement on next visit."},
    ],
    "reports_metrics": {
        "daily_sales": 5428.75,
        "order_volume": 186,
        "catering_revenue": 1326.00,
        "labor_hours": 73.0,
        "top_items": ["Sierra Turkey Club", "Truckee Italian", "Tomato Basil Bisque"],
    },
    "business_settings": {
        "business_name": "PurBlum",
        "category": "Deli, grocery market, catering",
        "phone": "(775) 555-0194",
        "address": "1842 Sierra Market Lane, Reno, NV 89501",
        "hours": {"mon_fri": "6:30 AM-8:00 PM", "saturday": "7:00 AM-8:00 PM", "sunday": "8:00 AM-5:00 PM"},
        "notifications": {"catering_sms": True, "order_issue_email": True, "inventory_warning": True, "staff_coverage": True},
        "operations": {"online_ordering": True, "catering_requests": True, "after_hours_leads": True},
    },
    "tax_fee_settings": {
        "enabled": False,
        "sales_tax_percent": 0.0,
        "local_tax_percent": 0.0,
        "service_fee_enabled": False,
        "service_fee": 0.0,
        "delivery_fee_enabled": False,
        "delivery_fee": 0.0,
        "updated_at": "",
    },
    "business_users": [
        {"username": "owner", "role": "owner", "display_name": "Owner Access", "access_code": "owner-2468"},
        {"username": "manager", "role": "manager", "display_name": "Manager Access", "access_code": "manager-1357"},
        {"username": "staff", "role": "staff", "display_name": "Staff Access", "access_code": "staff-8642"},
    ],
    "legal_terms": {
        "version": "orbi-terms-draft-2026-05-11",
        "status": "Acceptance required before setup continues.",
    },
    "legal_acceptances": [],
    "audit_log": [
        {"id": "AUD-1001", "timestamp": "2026-05-10T08:12:00Z", "actor": "Maya Chen", "action": "settings.update", "detail": "Catering cutoff changed to 24 hours."},
        {"id": "AUD-1002", "timestamp": "2026-05-10T09:05:00Z", "actor": "Luis Ortega", "action": "inventory.update", "detail": "Tomato basil bisque marked for prep."},
    ],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def data_file(name: str) -> Path:
    if name not in SEED_DATA:
        raise KeyError(f"Unknown data store: {name}")
    return DATA_DIR / f"{name}.json"


def ensure_data_files() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name, payload in SEED_DATA.items():
        path = data_file(name)
        if not path.exists():
            write_json(name, deepcopy(payload))


def read_json(name: str) -> Any:
    ensure_data_files()
    path = data_file(name)
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(name: str, payload: Any) -> Any:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = data_file(name)
    fd, temp_name = tempfile.mkstemp(prefix=f".{name}.", suffix=".tmp", dir=DATA_DIR)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    return payload


def append_audit(actor: str, action: str, detail: str) -> dict[str, Any]:
    entries = read_json("audit_log")
    entry = {
        "id": f"AUD-{len(entries) + 1001}",
        "timestamp": utc_now(),
        "actor": actor,
        "action": action,
        "detail": detail,
    }
    entries.append(entry)
    write_json("audit_log", entries)
    return entry
