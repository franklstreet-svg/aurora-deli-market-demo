from __future__ import annotations

import json
import mimetypes
import os
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from urllib.parse import parse_qs, unquote, urlparse

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from backend.storage import DATA_DIR, append_audit, ensure_data_files, read_json, write_json
else:
    from .storage import DATA_DIR, append_audit, ensure_data_files, read_json, write_json


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORT = 8126


class AuroraDeliHandler(BaseHTTPRequestHandler):
    server_version = "AuroraDeliBackend/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self.send_json(
                {
                    "status": "ok",
                    "service": "aurora-deli-market",
                    "data_dir": str(DATA_DIR.relative_to(PROJECT_ROOT)),
                }
            )
            return

        if parsed.path == "/api/products":
            products = read_json("products")
            query = parse_qs(parsed.query)
            category = query.get("category", [None])[0]
            if category:
                products = [item for item in products if item.get("category") == category]
            self.send_json({"products": products})
            return

        if parsed.path.startswith("/api/products/"):
            product_id = parsed.path.rsplit("/", 1)[-1]
            product = self.find_record("products", product_id)
            if not product:
                self.send_json({"error": "Product not found"}, HTTPStatus.NOT_FOUND)
                return
            self.send_json({"product": product})
            return

        if parsed.path == "/api/orders":
            self.send_json({"orders": read_json("orders")})
            return

        if parsed.path.startswith("/api/orders/"):
            order_id = parsed.path.rsplit("/", 1)[-1]
            order = self.find_record("orders", order_id)
            if not order:
                self.send_json({"error": "Order not found"}, HTTPStatus.NOT_FOUND)
                return
            self.send_json({"order": order})
            return

        if parsed.path == "/api/catering":
            self.send_json({"catering_requests": read_json("catering_requests")})
            return

        if parsed.path.startswith("/api/catering/"):
            request_id = parsed.path.rsplit("/", 1)[-1]
            catering = self.find_record("catering_requests", request_id)
            if not catering:
                self.send_json({"error": "Catering request not found"}, HTTPStatus.NOT_FOUND)
                return
            self.send_json({"catering_request": catering})
            return

        if parsed.path == "/api/inventory":
            self.send_json({"inventory": read_json("inventory")})
            return

        if parsed.path.startswith("/api/inventory/"):
            item_id = parsed.path.rsplit("/", 1)[-1]
            item = self.find_record("inventory", item_id)
            if not item:
                self.send_json({"error": "Inventory item not found"}, HTTPStatus.NOT_FOUND)
                return
            self.send_json({"inventory_item": item})
            return

        if parsed.path == "/api/staff":
            self.send_json({"staff_schedule": read_json("staff_schedule")})
            return

        if parsed.path.startswith("/api/staff/"):
            shift_id = parsed.path.rsplit("/", 1)[-1]
            shift = self.find_record("staff_schedule", shift_id)
            if not shift:
                self.send_json({"error": "Staff shift not found"}, HTTPStatus.NOT_FOUND)
                return
            self.send_json({"shift": shift})
            return

        if parsed.path == "/api/messages":
            self.send_json({"messages": read_json("customer_messages")})
            return

        if parsed.path.startswith("/api/messages/"):
            message_id = parsed.path.rsplit("/", 1)[-1]
            message = self.find_record("customer_messages", message_id)
            if not message:
                self.send_json({"error": "Message not found"}, HTTPStatus.NOT_FOUND)
                return
            self.send_json({"message": message})
            return

        if parsed.path == "/api/reports":
            self.send_json({"report": self.build_report()})
            return

        if parsed.path == "/api/settings":
            self.send_json({"settings": read_json("business_settings")})
            return

        if parsed.path == "/api/audit-log":
            self.send_json({"audit_log": read_json("audit_log")})
            return

        if parsed.path == "/api/system-status":
            self.send_json({"system_status": self.build_system_status()})
            return

        self.serve_static(parsed.path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/orders":
            payload = self.read_json_body()
            if payload is None:
                return
            order = self.create_order(payload)
            if not order:
                return
            orders = read_json("orders")
            orders.append(order)
            write_json("orders", orders)
            append_audit("Order desk", "order.create", f"Created order {order['id']}.")
            self.send_json({"order": order}, HTTPStatus.CREATED)
            return

        if parsed.path == "/api/catering":
            payload = self.read_json_body()
            if payload is None:
                return
            catering = self.create_catering_request(payload)
            if not catering:
                return
            requests = read_json("catering_requests")
            requests.append(catering)
            write_json("catering_requests", requests)
            append_audit("Catering desk", "catering.create", f"Created catering request {catering['id']}.")
            self.send_json({"catering_request": catering}, HTTPStatus.CREATED)
            return

        if parsed.path == "/api/staff":
            payload = self.read_json_body()
            if payload is None:
                return
            shift = self.create_shift(payload)
            if not shift:
                return
            shifts = read_json("staff_schedule")
            shifts.append(shift)
            write_json("staff_schedule", shifts)
            append_audit("Schedule desk", "staff.create", f"Created shift {shift['id']}.")
            self.send_json({"shift": shift}, HTTPStatus.CREATED)
            return

        if parsed.path == "/api/messages":
            payload = self.read_json_body()
            if payload is None:
                return
            message = self.create_message(payload)
            if not message:
                return
            messages = read_json("customer_messages")
            messages.append(message)
            write_json("customer_messages", messages)
            append_audit("Customer desk", "message.create", f"Created message {message['id']}.")
            self.send_json({"message": message}, HTTPStatus.CREATED)
            return

        self.send_json({"error": "Endpoint not found"}, HTTPStatus.NOT_FOUND)

    def do_PATCH(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/products/"):
            product_id = parsed.path.rsplit("/", 1)[-1]
            payload = self.read_json_body()
            if payload is None:
                return
            allowed = {"available", "price"}
            updates = {key: payload[key] for key in allowed if key in payload}
            if not updates:
                self.send_json({"error": "No supported product fields supplied"}, HTTPStatus.BAD_REQUEST)
                return
            if "price" in updates:
                try:
                    updates["price"] = round(float(updates["price"]), 2)
                except (TypeError, ValueError):
                    self.send_json({"error": "Price must be numeric"}, HTTPStatus.BAD_REQUEST)
                    return
            if "available" in updates:
                updates["available"] = bool(updates["available"])
            product = self.update_record("products", product_id, updates)
            if not product:
                self.send_json({"error": "Product not found"}, HTTPStatus.NOT_FOUND)
                return
            append_audit("Store manager", "product.update", f"Updated {product['name']} product fields.")
            self.send_json({"product": product})
            return

        if parsed.path.startswith("/api/orders/"):
            order_id = parsed.path.rsplit("/", 1)[-1]
            payload = self.read_json_body()
            if payload is None:
                return
            allowed = {"status", "pickup_time", "notes", "type"}
            updates = {key: payload[key] for key in allowed if key in payload}
            if not updates:
                self.send_json({"error": "No supported order fields supplied"}, HTTPStatus.BAD_REQUEST)
                return
            order = self.update_record("orders", order_id, updates)
            if not order:
                self.send_json({"error": "Order not found"}, HTTPStatus.NOT_FOUND)
                return
            append_audit("Order desk", "order.update", f"Updated order {order_id}.")
            self.send_json({"order": order})
            return

        if parsed.path.startswith("/api/catering/"):
            request_id = parsed.path.rsplit("/", 1)[-1]
            payload = self.read_json_body()
            if payload is None:
                return
            allowed = {"status", "priority", "assigned_staff", "notes", "estimated_total"}
            updates = {key: payload[key] for key in allowed if key in payload}
            if not updates:
                self.send_json({"error": "No supported catering fields supplied"}, HTTPStatus.BAD_REQUEST)
                return
            if "estimated_total" in updates:
                try:
                    updates["estimated_total"] = round(float(updates["estimated_total"]), 2)
                except (TypeError, ValueError):
                    self.send_json({"error": "Estimated total must be numeric"}, HTTPStatus.BAD_REQUEST)
                    return
            catering = self.update_record("catering_requests", request_id, updates)
            if not catering:
                self.send_json({"error": "Catering request not found"}, HTTPStatus.NOT_FOUND)
                return
            append_audit("Catering desk", "catering.update", f"Updated catering request {request_id}.")
            self.send_json({"catering_request": catering})
            return

        if parsed.path.startswith("/api/inventory/"):
            item_id = parsed.path.rsplit("/", 1)[-1]
            payload = self.read_json_body()
            if payload is None:
                return
            allowed = {"quantity", "par", "supplier", "reorder_status", "expires"}
            updates = {key: payload[key] for key in allowed if key in payload}
            if not updates:
                self.send_json({"error": "No supported inventory fields supplied"}, HTTPStatus.BAD_REQUEST)
                return
            for numeric_field in ("quantity", "par"):
                if numeric_field in updates:
                    try:
                        updates[numeric_field] = max(0, int(updates[numeric_field]))
                    except (TypeError, ValueError):
                        self.send_json({"error": f"{numeric_field} must be numeric"}, HTTPStatus.BAD_REQUEST)
                        return
            item = self.update_record("inventory", item_id, updates)
            if not item:
                self.send_json({"error": "Inventory item not found"}, HTTPStatus.NOT_FOUND)
                return
            append_audit("Inventory desk", "inventory.update", f"Updated inventory item {item['name']}.")
            self.send_json({"inventory_item": item})
            return

        if parsed.path.startswith("/api/staff/"):
            shift_id = parsed.path.rsplit("/", 1)[-1]
            payload = self.read_json_body()
            if payload is None:
                return
            allowed = {"employee", "role", "date", "start", "end", "coverage"}
            updates = {key: payload[key] for key in allowed if key in payload}
            if not updates:
                self.send_json({"error": "No supported staff fields supplied"}, HTTPStatus.BAD_REQUEST)
                return
            shift = self.update_record("staff_schedule", shift_id, updates)
            if not shift:
                self.send_json({"error": "Staff shift not found"}, HTTPStatus.NOT_FOUND)
                return
            append_audit("Schedule desk", "staff.update", f"Updated shift {shift_id}.")
            self.send_json({"shift": shift})
            return

        if parsed.path.startswith("/api/messages/"):
            message_id = parsed.path.rsplit("/", 1)[-1]
            payload = self.read_json_body()
            if payload is None:
                return
            allowed = {"source", "status", "priority", "assigned_staff", "notes", "subject", "customer_name"}
            updates = {key: payload[key] for key in allowed if key in payload}
            if not updates:
                self.send_json({"error": "No supported message fields supplied"}, HTTPStatus.BAD_REQUEST)
                return
            message = self.update_record("customer_messages", message_id, updates)
            if not message:
                self.send_json({"error": "Message not found"}, HTTPStatus.NOT_FOUND)
                return
            append_audit("Customer desk", "message.update", f"Updated message {message_id}.")
            self.send_json({"message": message})
            return

        if parsed.path == "/api/settings":
            payload = self.read_json_body()
            if payload is None:
                return
            if not isinstance(payload, dict):
                self.send_json({"error": "Settings body must be an object"}, HTTPStatus.BAD_REQUEST)
                return
            settings = read_json("business_settings")
            settings = self.deep_merge(settings, payload)
            write_json("business_settings", settings)
            append_audit("Settings desk", "settings.update", "Updated business settings.")
            self.send_json({"settings": settings})
            return

        self.send_json({"error": "Endpoint not found"}, HTTPStatus.NOT_FOUND)

    def serve_static(self, raw_path: str) -> None:
        request_path = unquote(raw_path).lstrip("/")
        if not request_path:
            request_path = "index.html"

        target = (PROJECT_ROOT / request_path).resolve()
        if PROJECT_ROOT not in target.parents and target != PROJECT_ROOT:
            self.send_error(HTTPStatus.FORBIDDEN)
            return

        if target.is_dir():
            target = target / "index.html"

        if not target.exists() or not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        content = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(content)

    def do_HEAD(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            content = json.dumps({"status": "ok"}).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            return
        self.serve_static(parsed.path)

    def send_json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        content = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def read_json_body(self) -> object | None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_json({"error": "Invalid content length"}, HTTPStatus.BAD_REQUEST)
            return None
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self.send_json({"error": "Invalid JSON body"}, HTTPStatus.BAD_REQUEST)
            return None

    def find_record(self, store: str, record_id: str) -> dict[str, object] | None:
        records = read_json(store)
        for record in records:
            if record.get("id") == record_id:
                return record
        return None

    def update_record(self, store: str, record_id: str, updates: dict[str, object]) -> dict[str, object] | None:
        records = read_json(store)
        for record in records:
            if record.get("id") == record_id:
                record.update(updates)
                write_json(store, records)
                return record
        return None

    def create_order(self, payload: object) -> dict[str, object] | None:
        if not isinstance(payload, dict):
            self.send_json({"error": "Order body must be an object"}, HTTPStatus.BAD_REQUEST)
            return None
        items = payload.get("items")
        if not isinstance(items, list) or not items:
            self.send_json({"error": "Order requires at least one item"}, HTTPStatus.BAD_REQUEST)
            return None
        clean_items = []
        subtotal = 0.0
        for item in items:
            if not isinstance(item, dict):
                self.send_json({"error": "Each order item must be an object"}, HTTPStatus.BAD_REQUEST)
                return None
            name = str(item.get("name", "")).strip()
            if not name:
                self.send_json({"error": "Each order item requires a name"}, HTTPStatus.BAD_REQUEST)
                return None
            try:
                quantity = max(1, int(item.get("quantity", 1)))
                price = round(float(item.get("price", 0)), 2)
            except (TypeError, ValueError):
                self.send_json({"error": "Order item quantity and price must be numeric"}, HTTPStatus.BAD_REQUEST)
                return None
            clean_items.append({"name": name, "quantity": quantity, "price": price})
            subtotal += quantity * price
        subtotal = round(subtotal, 2)
        tax = round(subtotal * 0.08265, 2)
        orders = read_json("orders")
        order_id = f"ADM-{1000 + len(orders) + 1}"
        return {
            "id": order_id,
            "customer_name": str(payload.get("customer_name", "Customer")).strip() or "Customer",
            "phone": str(payload.get("phone", "")).strip(),
            "type": str(payload.get("type", "pickup")).strip() or "pickup",
            "status": str(payload.get("status", "received")).strip() or "received",
            "pickup_time": str(payload.get("pickup_time", "")).strip(),
            "items": clean_items,
            "subtotal": subtotal,
            "tax": tax,
            "total": round(subtotal + tax, 2),
            "notes": str(payload.get("notes", "")).strip(),
        }

    def create_catering_request(self, payload: object) -> dict[str, object] | None:
        if not isinstance(payload, dict):
            self.send_json({"error": "Catering body must be an object"}, HTTPStatus.BAD_REQUEST)
            return None
        customer_name = str(payload.get("customer_name", "")).strip()
        phone = str(payload.get("phone", "")).strip()
        email = str(payload.get("email", "")).strip()
        package = str(payload.get("package", "")).strip()
        if not customer_name or not phone or not email or not package:
            self.send_json({"error": "Catering request requires name, phone, email, and package"}, HTTPStatus.BAD_REQUEST)
            return None
        try:
            guest_count = max(1, int(payload.get("guest_count", 1)))
            estimated_total = round(float(payload.get("estimated_total", 0)), 2)
        except (TypeError, ValueError):
            self.send_json({"error": "Guest count and estimated total must be numeric"}, HTTPStatus.BAD_REQUEST)
            return None
        requests = read_json("catering_requests")
        request_id = f"CAT-{2200 + len(requests) + 1}"
        return {
            "id": request_id,
            "customer_name": customer_name,
            "phone": phone,
            "email": email,
            "package": package,
            "guest_count": guest_count,
            "event_time": str(payload.get("event_time", "")).strip(),
            "service_type": str(payload.get("service_type", "pickup")).strip() or "pickup",
            "status": str(payload.get("status", "new")).strip() or "new",
            "priority": str(payload.get("priority", "normal")).strip() or "normal",
            "estimated_total": estimated_total,
            "notes": str(payload.get("notes", "")).strip(),
        }

    def create_shift(self, payload: object) -> dict[str, object] | None:
        if not isinstance(payload, dict):
            self.send_json({"error": "Shift body must be an object"}, HTTPStatus.BAD_REQUEST)
            return None
        required = ("employee", "role", "date", "start", "end")
        missing = [field for field in required if not str(payload.get(field, "")).strip()]
        if missing:
            self.send_json({"error": f"Shift missing fields: {', '.join(missing)}"}, HTTPStatus.BAD_REQUEST)
            return None
        shifts = read_json("staff_schedule")
        shift_id = f"shift-{len(shifts) + 1:03d}"
        return {
            "id": shift_id,
            "employee": str(payload.get("employee")).strip(),
            "role": str(payload.get("role")).strip(),
            "date": str(payload.get("date")).strip(),
            "start": str(payload.get("start")).strip(),
            "end": str(payload.get("end")).strip(),
            "coverage": str(payload.get("coverage", "general")).strip() or "general",
        }

    def create_message(self, payload: object) -> dict[str, object] | None:
        if not isinstance(payload, dict):
            self.send_json({"error": "Message body must be an object"}, HTTPStatus.BAD_REQUEST)
            return None
        customer_name = str(payload.get("customer_name", "")).strip()
        subject = str(payload.get("subject", "")).strip()
        if not customer_name or not subject:
            self.send_json({"error": "Message requires customer_name and subject"}, HTTPStatus.BAD_REQUEST)
            return None
        messages = read_json("customer_messages")
        message_id = f"MSG-{3100 + len(messages) + 1}"
        return {
            "id": message_id,
            "customer_name": customer_name,
            "source": str(payload.get("source", "web")).strip() or "web",
            "subject": subject,
            "status": str(payload.get("status", "new")).strip() or "new",
            "priority": str(payload.get("priority", "normal")).strip() or "normal",
            "assigned_staff": str(payload.get("assigned_staff", "Unassigned")).strip() or "Unassigned",
            "notes": str(payload.get("notes", "")).strip(),
        }

    def build_report(self) -> dict[str, object]:
        orders = read_json("orders")
        catering = read_json("catering_requests")
        inventory = read_json("inventory")
        staff = read_json("staff_schedule")
        messages = read_json("customer_messages")

        order_sales = round(sum(float(order.get("total", 0)) for order in orders), 2)
        catering_revenue = round(sum(float(item.get("estimated_total", 0)) for item in catering), 2)
        low_stock = [
            item for item in inventory
            if int(item.get("quantity", 0)) < int(item.get("par", 0))
        ]
        item_counts: dict[str, int] = defaultdict(int)
        item_revenue: dict[str, float] = defaultdict(float)
        for order in orders:
            for item in order.get("items", []):
                name = str(item.get("name", "Unknown item"))
                quantity = int(item.get("quantity", 0))
                price = float(item.get("price", 0))
                item_counts[name] += quantity
                item_revenue[name] += quantity * price

        top_items = [
            {"name": name, "units": item_counts[name], "revenue": round(item_revenue[name], 2)}
            for name in sorted(item_counts, key=lambda key: (-item_counts[key], key))[:5]
        ]
        lead_count = len([msg for msg in messages if "lead" in str(msg.get("subject", "")).lower() or msg.get("priority") == "high"])
        converted_count = len([item for item in catering if item.get("status") in {"confirmed", "fulfilled", "quote_sent"}])
        labor_hours = round(sum(self.shift_hours(shift.get("start"), shift.get("end")) for shift in staff), 2)
        return {
            "daily_sales": round(order_sales + catering_revenue, 2),
            "order_sales": order_sales,
            "order_volume": len(orders),
            "catering_revenue": catering_revenue,
            "catering_requests": len(catering),
            "inventory": {
                "total_items": len(inventory),
                "low_stock_count": len(low_stock),
                "low_stock_items": [{"id": item["id"], "name": item["name"], "quantity": item["quantity"], "par": item["par"]} for item in low_stock],
            },
            "staff": {
                "shift_count": len(staff),
                "scheduled_hours": labor_hours,
            },
            "messages": {
                "total": len(messages),
                "high_priority": len([msg for msg in messages if msg.get("priority") == "high"]),
                "unresolved": len([msg for msg in messages if msg.get("status") in {"new", "unresolved", "awaiting_quote"}]),
            },
            "top_items": top_items,
            "lead_conversion": {
                "lead_count": lead_count,
                "converted_count": converted_count,
                "conversion_rate": round((converted_count / lead_count) * 100, 1) if lead_count else 0,
            },
        }

    def shift_hours(self, start: object, end: object) -> float:
        try:
            start_dt = datetime.strptime(str(start), "%H:%M")
            end_dt = datetime.strptime(str(end), "%H:%M")
        except ValueError:
            return 0.0
        hours = (end_dt - start_dt).seconds / 3600
        return hours if hours <= 16 else 0.0

    def build_system_status(self) -> dict[str, object]:
        return {
            "status": "ok",
            "stores": {
                "products": len(read_json("products")),
                "inventory": len(read_json("inventory")),
                "orders": len(read_json("orders")),
                "catering_requests": len(read_json("catering_requests")),
                "staff_schedule": len(read_json("staff_schedule")),
                "customer_messages": len(read_json("customer_messages")),
                "audit_log": len(read_json("audit_log")),
            },
            "storage": {
                "data_dir": str(DATA_DIR.relative_to(PROJECT_ROOT)),
                "mode": "json",
            },
        }

    def deep_merge(self, base: object, updates: object) -> object:
        if not isinstance(base, dict) or not isinstance(updates, dict):
            return updates
        merged = dict(base)
        for key, value in updates.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = self.deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged

    def log_message(self, fmt: str, *args: object) -> None:
        print("%s - - %s" % (self.address_string(), fmt % args))


def ensure_storage() -> None:
    ensure_data_files()
    marker = DATA_DIR / ".gitkeep"
    marker.touch(exist_ok=True)


def run(port: int = DEFAULT_PORT, host: str = '127.0.0.1') -> None:
 ensure_storage()
 server = ThreadingHTTPServer((host, port), AuroraDeliHandler)
 print(f'Aurora Deli backend running at http://{host}:{port}')
 server.serve_forever()


if __name__ == '__main__':
 deployment_port = int(os.environ.get('PORT', os.environ.get('AURORA_DELI_PORT', DEFAULT_PORT)))
 deployment_host = os.environ.get('AURORA_DELI_HOST', '0.0.0.0' if os.environ.get('PORT') else '127.0.0.1')
 run(deployment_port, deployment_host)
