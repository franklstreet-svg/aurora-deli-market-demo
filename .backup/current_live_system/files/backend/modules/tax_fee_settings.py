from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any


DEFAULT_TAX_FEE_SETTINGS: dict[str, Any] = {
    "enabled": False,
    "sales_tax_percent": 0.0,
    "local_tax_percent": 0.0,
    "service_fee_enabled": False,
    "service_fee": 0.0,
    "delivery_fee_enabled": False,
    "delivery_fee": 0.0,
    "updated_at": "",
}


def money(value: Any) -> float:
    amount = Decimal(str(value or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return float(amount)


class TaxFeeSettings:
    def __init__(self, settings: dict[str, Any] | None):
        self.settings = {**DEFAULT_TAX_FEE_SETTINGS, **(settings or {})}

    def public_payload(self) -> dict[str, Any]:
        return dict(self.settings)

    def calculate(self, subtotal: float, fulfillment_type: str = "pickup") -> dict[str, Any]:
        subtotal = money(subtotal)
        if not self.settings.get("enabled"):
            return {
                "subtotal": subtotal,
                "tax_configured": False,
                "tax": 0.0,
                "sales_tax": 0.0,
                "local_tax": 0.0,
                "service_fee": 0.0,
                "delivery_fee": 0.0,
                "total": subtotal,
                "message": "Subtotal shown before taxes and fees.",
            }

        sales_rate = Decimal(str(self.settings.get("sales_tax_percent") or 0)) / Decimal("100")
        local_rate = Decimal(str(self.settings.get("local_tax_percent") or 0)) / Decimal("100")
        sales_tax = money(Decimal(str(subtotal)) * sales_rate)
        local_tax = money(Decimal(str(subtotal)) * local_rate)
        service_fee = money(self.settings.get("service_fee")) if self.settings.get("service_fee_enabled") else 0.0
        delivery_fee = (
            money(self.settings.get("delivery_fee"))
            if self.settings.get("delivery_fee_enabled") and fulfillment_type == "delivery"
            else 0.0
        )
        tax = money(sales_tax + local_tax)
        total = money(subtotal + tax + service_fee + delivery_fee)
        return {
            "subtotal": subtotal,
            "tax_configured": True,
            "tax": tax,
            "sales_tax": sales_tax,
            "local_tax": local_tax,
            "service_fee": service_fee,
            "delivery_fee": delivery_fee,
            "total": total,
            "message": "Estimated total includes configured taxes and fees.",
        }


def normalize_tax_fee_settings(payload: dict[str, Any], previous: dict[str, Any] | None = None) -> dict[str, Any]:
    base = {**DEFAULT_TAX_FEE_SETTINGS, **(previous or {})}
    out = dict(base)
    for key in ("enabled", "service_fee_enabled", "delivery_fee_enabled"):
        if key in payload:
            out[key] = bool(payload[key])
    for key in ("sales_tax_percent", "local_tax_percent", "service_fee", "delivery_fee"):
        if key in payload:
            try:
                value = float(payload[key])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{key} must be numeric") from exc
            out[key] = money(max(0.0, value))
    if "updated_at" in payload:
        out["updated_at"] = str(payload["updated_at"])
    return out

