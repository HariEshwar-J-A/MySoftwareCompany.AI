# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""Stripe webhook stub — maps checkout events to license issuance (Phase 4)."""

from __future__ import annotations

from typing import Any

from msc.entitlements.keys import LicensePayload, issue_license_token, save_stored_license


def stripe_checkout_to_license(
    event: dict[str, Any],
    *,
    private_key_pem: bytes,
    pack_id: str,
    customer_id: str,
) -> str:
    """Convert a Stripe checkout.session.completed-style payload to a license token.

    Production: website/app/api/stripe/webhook calls an admin endpoint that uses this.
    """
    if event.get("type") not in ("checkout.session.completed", "test.checkout.completed"):
        raise ValueError(f"Unsupported Stripe event type: {event.get('type')}")
    payload = LicensePayload(
        customer_id=customer_id,
        tier="marketplace",
        entitled_packs=[pack_id],
        expires_at=None,
    )
    return issue_license_token(payload, private_key_pem=private_key_pem)


def issue_and_store_from_stripe_stub(
    event: dict[str, Any],
    *,
    private_key_pem: bytes,
    pack_id: str,
    customer_id: str,
) -> str:
    token = stripe_checkout_to_license(
        event,
        private_key_pem=private_key_pem,
        pack_id=pack_id,
        customer_id=customer_id,
    )
    save_stored_license(token)
    return token
