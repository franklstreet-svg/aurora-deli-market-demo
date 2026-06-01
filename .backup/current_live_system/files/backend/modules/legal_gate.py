from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


LEGAL_DOCUMENT_VERSION = "orbi-terms-2026-05-11"

LEGAL_CHECKBOX_KEYS = (
    "terms",
    "ai_supervision",
    "business_responsibility",
    "no_professional_advice",
    "liability_electronic_acceptance",
)


PLAIN_ENGLISH_SUMMARY = [
    "AI can make mistakes, so a person at the business must supervise it.",
    "The business owner remains responsible for operations, orders, pricing, taxes, compliance, and customer outcomes.",
    "Taxes and fees must be configured by the owner; Orbi will not invent tax rates.",
    "Orders and customer messages must be monitored by staff.",
    "Third-party services, payment processors, phone providers, websites, and integrations can fail or be unavailable.",
    "Orbi is an assistant tool, not a guaranteed human replacement.",
    "The owner must comply with local laws, disclosure rules, and industry requirements.",
]


LEGAL_TERMS_SECTIONS = [
    {
        "heading": "1. Acceptance of Terms",
        "body": "By clicking accept, creating an account, purchasing, starting setup, or using Orbi or Aurora services, the customer agrees to these terms. If the customer does not agree, setup and use must stop. The person accepting represents that they have authority to bind the business named in the acceptance record.",
    },
    {
        "heading": "2. Product Nature",
        "body": "Orbi and Aurora are software assistant tools that may support website chat, customer intake, order assistance, scheduling support, business workflows, and related automation. They are not a complete business management replacement, employee, accountant, lawyer, tax adviser, medical professional, financial adviser, or compliance officer.",
    },
    {
        "heading": "3. AI Limitations",
        "body": "AI-generated output may be incorrect, incomplete, delayed, outdated, or inappropriate for a specific business situation. The customer must review and supervise AI activity, especially before relying on information in customer communications, prices, taxes, availability, legal obligations, refunds, health/safety issues, or business operations.",
    },
    {
        "heading": "4. Customer Responsibility",
        "body": "The customer remains solely responsible for its business, employees, products, services, prices, taxes, fees, disclosures, licenses, permits, customer service, order fulfillment, refunds, cancellations, food safety, privacy obligations, and compliance with all applicable laws and platform rules.",
    },
    {
        "heading": "5. Ordering Disclaimer",
        "body": "Any order intake, pickup request, catering request, reservation, appointment, or customer message handled by Orbi or Aurora must be reviewed by the business. The business is responsible for confirming availability, accepting or rejecting orders, preparing items correctly, handling substitutions, collecting payment, and resolving customer issues.",
    },
    {
        "heading": "6. Tax and Fee Responsibility",
        "body": "The customer is responsible for configuring, reviewing, and validating all tax rates, local taxes, service fees, delivery fees, pricing rules, discounts, and totals. Orbi does not determine taxability or provide tax advice. If tax settings are not configured, estimates may show subtotal before taxes and fees.",
    },
    {
        "heading": "7. No Legal, Tax, Medical, Financial, or Professional Advice",
        "body": "Orbi and Aurora do not provide legal, tax, accounting, medical, financial, insurance, employment, safety, or other professional advice. The customer should consult qualified professionals for those matters.",
    },
    {
        "heading": "8. Privacy and Customer Data",
        "body": "The customer is responsible for telling its customers how data is collected and used, obtaining required consents, protecting sensitive information, and avoiding entry of payment card details, protected health information, government identifiers, or other highly sensitive data unless a separate written agreement and appropriate safeguards are in place.",
    },
    {
        "heading": "9. Third-Party Integrations",
        "body": "Orbi may depend on websites, hosting providers, AI providers, payment processors, phone services, email providers, calendars, POS systems, delivery platforms, CRM systems, and other third parties. Third-party changes, downtime, rate limits, permission changes, or data errors may affect performance. Orbi is not responsible for third-party services.",
    },
    {
        "heading": "10. Downtime and Availability",
        "body": "Services may be interrupted by maintenance, updates, network failures, hosting issues, third-party outages, security events, or other causes. The customer must maintain a backup process for orders, calls, messages, and critical business operations.",
    },
    {
        "heading": "11. Limitation of Liability",
        "body": "To the maximum extent allowed by law, Orbi's total liability for claims related to the services is limited to the amount the customer paid to Orbi for the services giving rise to the claim during the three months before the event. Orbi is not liable for indirect, incidental, special, consequential, exemplary, punitive, lost profit, lost revenue, lost data, business interruption, customer loss, or reputational damages.",
    },
    {
        "heading": "12. No Warranty",
        "body": "The services are provided as is and as available. Orbi disclaims all warranties to the maximum extent allowed by law, including implied warranties of merchantability, fitness for a particular purpose, non-infringement, accuracy, uninterrupted operation, and error-free performance.",
    },
    {
        "heading": "13. Indemnification",
        "body": "The customer agrees to defend, indemnify, and hold Orbi harmless from claims, losses, damages, liabilities, costs, and expenses arising from the customer's business operations, products, services, customer disputes, data, configuration choices, legal compliance, misuse of the services, or breach of these terms.",
    },
    {
        "heading": "14. Voice and Recording Disclosure",
        "body": "If voice, call handling, call recording, transcription, monitoring, or phone features are enabled, the customer is responsible for all notices, consents, recording disclosures, call monitoring disclosures, and compliance with federal, state, and local laws for every caller and jurisdiction involved.",
    },
    {
        "heading": "15. Owner Configuration Responsibility",
        "body": "The customer must configure and verify business hours, contact information, product availability, pricing, tax and fee settings, order rules, staff access, escalation rules, and integration permissions. Orbi may assist with setup, but the customer remains responsible for final review and correctness.",
    },
    {
        "heading": "16. Future Features",
        "body": "Descriptions of planned or future features are informational only. Orbi is not obligated to deliver any future feature, integration, timeline, or roadmap item unless stated in a separate signed agreement.",
    },
    {
        "heading": "17. Suspension and Termination",
        "body": "Orbi may suspend or terminate access for nonpayment, security risk, misuse, unlawful activity, harmful content, excessive load, violation of these terms, or business conduct that creates legal, safety, operational, or reputational risk.",
    },
    {
        "heading": "18. Payment Terms",
        "body": "Fees, setup charges, subscriptions, usage charges, renewal terms, cancellation rules, refunds, and payment processing details are governed by the applicable checkout, invoice, order form, or written agreement. Unless otherwise stated, fees are non-refundable after setup work or service activation begins.",
    },
    {
        "heading": "19. Intellectual Property",
        "body": "Orbi retains ownership of its software, systems, prompts, workflows, modules, documentation, designs, trademarks, and technology. The customer retains ownership of its business data and content, subject to the license needed for Orbi to provide the services.",
    },
    {
        "heading": "20. Nevada Governing Law",
        "body": "These terms are governed by the laws of the State of Nevada, without regard to conflict-of-law rules, except where federal law controls.",
    },
    {
        "heading": "21. Arbitration and Class Action Waiver",
        "body": "To the maximum extent allowed by law, disputes must be resolved by binding individual arbitration in Nevada, and not in a class, collective, consolidated, private attorney general, or representative action. The customer and Orbi waive the right to a jury trial for covered disputes.",
    },
    {
        "heading": "22. Electronic Acceptance",
        "body": "Checking the required boxes and submitting acceptance is an electronic signature and creates an electronic record. The customer agrees that electronic acceptance has the same legal effect as a handwritten signature.",
    },
    {
        "heading": "23. Setup Acceptance Flow",
        "body": "Setup, onboarding, purchase completion, installation, or activation may not continue unless the required legal acknowledgments are accepted. If the customer declines, Orbi cannot continue setup.",
    },
]


def legal_terms_payload() -> dict[str, Any]:
    payload = {
        "version": LEGAL_DOCUMENT_VERSION,
        "status": "Acceptance required before setup continues.",
        "plain_english_summary": PLAIN_ENGLISH_SUMMARY,
        "sections": LEGAL_TERMS_SECTIONS,
        "required_checkboxes": list(LEGAL_CHECKBOX_KEYS),
    }
    payload["legal_text_hash"] = legal_text_hash(payload)
    return payload


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_legal_document(payload: dict[str, Any] | None = None) -> str:
    terms = dict(payload or legal_terms_payload())
    terms.pop("legal_text_hash", None)
    return json.dumps(terms, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def legal_text_hash(payload: dict[str, Any] | None = None) -> str:
    return hashlib.sha256(canonical_legal_document(payload).encode("utf-8")).hexdigest()


def customer_business_id(business_name: str, owner_email: str) -> str:
    digest = hashlib.sha256(f"{business_name.lower()}|{owner_email.lower()}".encode("utf-8")).hexdigest()[:12].upper()
    return f"BUS-{digest}"


def clean_optional(payload: dict[str, Any], key: str) -> str:
    return str(payload.get(key, "")).strip()


def create_acceptance(payload: dict[str, Any], ip_address: str, user_agent: str, accepted: bool = True) -> dict[str, Any]:
    name = str(payload.get("owner_full_name") or payload.get("name") or "").strip()
    business_name = str(payload.get("business_name", "")).strip()
    owner_email = str(payload.get("owner_email", "")).strip()
    checkboxes = payload.get("checkboxes", {})
    if not name or not business_name or not owner_email:
        raise ValueError("Owner full name, business name, and owner email are required.")
    if not isinstance(checkboxes, dict):
        raise ValueError("Acceptance checkboxes are required.")
    if accepted:
        missing = [key for key in LEGAL_CHECKBOX_KEYS if checkboxes.get(key) is not True]
        if missing:
            raise ValueError("All legal acknowledgments must be accepted.")
    snapshot = legal_terms_payload()
    business_id = clean_optional(payload, "customer_business_id") or customer_business_id(business_name, owner_email)
    return {
        "id": f"LEGAL-{uuid4().hex[:12].upper()}",
        "decision": "accepted" if accepted else "declined",
        "accepted": bool(accepted),
        "owner_full_name": name,
        "name": name,
        "business_name": business_name,
        "owner_email": owner_email,
        "phone": clean_optional(payload, "phone"),
        "business_website": clean_optional(payload, "business_website"),
        "timestamp_utc": utc_now(),
        "timestamp": utc_now(),
        "timezone": clean_optional(payload, "timezone"),
        "ip_address": ip_address,
        "user_agent": user_agent,
        "browser_user_agent": user_agent,
        "legal_document_version": LEGAL_DOCUMENT_VERSION,
        "legal_text_hash": snapshot["legal_text_hash"],
        "accepted_checkboxes": {key: bool(checkboxes.get(key)) for key in LEGAL_CHECKBOX_KEYS},
        "checkboxes": {key: bool(checkboxes.get(key)) for key in LEGAL_CHECKBOX_KEYS},
        "onboarding_session_id": clean_optional(payload, "onboarding_session_id"),
        "customer_business_id": business_id,
        "selected_product_module": clean_optional(payload, "selected_product_module"),
        "legal_document_snapshot": snapshot,
    }


def receipt_payload(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "receipt_type": "legal_acceptance_proof",
        "acceptance_id": record.get("id"),
        "decision": record.get("decision", "accepted" if record.get("accepted") else "declined"),
        "accepted": record.get("accepted"),
        "owner_full_name": record.get("owner_full_name") or record.get("name"),
        "business_name": record.get("business_name"),
        "owner_email": record.get("owner_email"),
        "timestamp_utc": record.get("timestamp_utc") or record.get("timestamp"),
        "timezone": record.get("timezone"),
        "ip_address": record.get("ip_address"),
        "browser_user_agent": record.get("browser_user_agent") or record.get("user_agent"),
        "legal_document_version": record.get("legal_document_version"),
        "legal_text_hash": record.get("legal_text_hash"),
        "accepted_checkboxes": record.get("accepted_checkboxes") or record.get("checkboxes"),
        "onboarding_session_id": record.get("onboarding_session_id"),
        "customer_business_id": record.get("customer_business_id"),
        "selected_product_module": record.get("selected_product_module"),
        "legal_document_snapshot": record.get("legal_document_snapshot"),
    }
