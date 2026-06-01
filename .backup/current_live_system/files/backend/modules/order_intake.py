from __future__ import annotations

from typing import Any

from .tax_fee_settings import TaxFeeSettings, money


ORDER_STATUSES = {"new", "accepted", "ready", "completed", "canceled", "rejected"}


class OrderIntake:
    def __init__(self, products: list[dict[str, Any]], tax_settings: dict[str, Any] | None):
        self.products = products
        self.tax_settings = TaxFeeSettings(tax_settings)
        self.by_id = {str(item.get("id")): item for item in products}
        self.by_name = {str(item.get("name", "")).strip().lower(): item for item in products}

    def estimate(self, payload: dict[str, Any]) -> dict[str, Any]:
        clean_items, subtotal = self.clean_items(payload.get("items"))
        fulfillment_type = str(payload.get("type") or payload.get("fulfillment_type") or "pickup").strip() or "pickup"
        totals = self.tax_settings.calculate(subtotal, fulfillment_type=fulfillment_type)
        return {"items": clean_items, **totals}

    def create_order(self, payload: dict[str, Any], existing_count: int) -> dict[str, Any]:
        customer_name = str(payload.get("customer_name", "")).strip()
        phone = str(payload.get("phone", "")).strip()
        email = str(payload.get("email", "")).strip()
        pickup_time = str(payload.get("pickup_time", "")).strip()
        if not customer_name or not (phone or email) or not pickup_time:
            raise ValueError("Order requires customer name, phone or email, and pickup time")

        estimate = self.estimate(payload)
        order_id = f"ADM-{1000 + existing_count + 1}"
        return {
            "id": order_id,
            "customer_name": customer_name,
            "phone": phone,
            "email": email,
            "business_name": str(payload.get("business_name", "")).strip(),
            "business_website": str(payload.get("business_website", "")).strip(),
            "legal_acceptance_id": str(payload.get("legal_acceptance_id", "")).strip(),
            "legal_document_version": str(payload.get("legal_document_version", "")).strip(),
            "legal_text_hash": str(payload.get("legal_text_hash", "")).strip(),
            "legal_acceptance_timestamp": str(payload.get("legal_acceptance_timestamp", "")).strip(),
            "customer_business_id": str(payload.get("customer_business_id", "")).strip(),
            "onboarding_session_id": str(payload.get("onboarding_session_id", "")).strip(),
            "selected_product_module": str(payload.get("selected_product_module", "")).strip(),
            "type": str(payload.get("type", "pickup")).strip() or "pickup",
            "source": str(payload.get("source", "public_order_page")).strip() or "public_order_page",
            "status": "new",
            "pickup_time": pickup_time,
            "items": estimate["items"],
            "subtotal": estimate["subtotal"],
            "tax_configured": estimate["tax_configured"],
            "tax": estimate["tax"],
            "sales_tax": estimate["sales_tax"],
            "local_tax": estimate["local_tax"],
            "service_fee": estimate["service_fee"],
            "delivery_fee": estimate["delivery_fee"],
            "total": estimate["total"],
            "estimate_message": estimate["message"],
            "notes": str(payload.get("notes", "")).strip(),
        }

    def clean_items(self, items: Any) -> tuple[list[dict[str, Any]], float]:
        if not isinstance(items, list) or not items:
            raise ValueError("Order requires at least one item")

        clean_items: list[dict[str, Any]] = []
        subtotal = 0.0
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("Each order item must be an object")
            product = self.resolve_product(item)
            try:
                quantity = max(1, int(item.get("quantity", 1)))
            except (TypeError, ValueError) as exc:
                raise ValueError("Order item quantity must be numeric") from exc
            unit_price = money(product.get("price"))
            line_total = money(quantity * unit_price)
            clean_items.append({
                "product_id": product.get("id", ""),
                "name": product.get("name", ""),
                "quantity": quantity,
                "price": unit_price,
                "line_total": line_total,
                "modifiers": str(item.get("modifiers", "")).strip(),
                "notes": str(item.get("notes", "")).strip(),
            })
            subtotal += line_total
        return clean_items, money(subtotal)

    def resolve_product(self, item: dict[str, Any]) -> dict[str, Any]:
        product_id = str(item.get("product_id", "")).strip()
        name = str(item.get("name", "")).strip()
        product = self.by_id.get(product_id) if product_id else None
        if product is None and name:
            product = self.by_name.get(name.lower())
        if product is None:
            raise ValueError(f"Unknown menu item: {name or product_id}")
        if product.get("available") is False:
            raise ValueError(f"{product.get('name', 'That item')} is not currently available")
        return product
