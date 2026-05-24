// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

/**
 * Stripe webhook — verifies signature and issues MSC1 license tokens.
 *
 * Integration with Python entitlements (packages/msc/entitlements/stripe_webhook.py):
 *   1. Webhook receives checkout.session.completed
 *   2. Production admin endpoint runs gen_license_key.py with pack + customer_id
 *   3. Token emailed to customer; optional POST back to cache for success page
 *
 * This route implements step 2 in TypeScript for Vercel/serverless deployment.
 * Set MSC_LICENSE_PRIVATE_KEY or MSC_LICENSE_PRIVATE_KEY_PATH (same Ed25519 key as
 * scripts/.marketplace_dev_key.pem locally — never commit production keys).
 */

import { NextResponse } from "next/server";
import Stripe from "stripe";
import { cacheLicenseForSession } from "@/lib/license-store";
import { issueTokenForCheckout } from "@/lib/license-server";
import { getStripe } from "@/lib/stripe";

export async function POST(request: Request) {
  const stripe = getStripe();
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

  if (!stripe || !webhookSecret) {
    return NextResponse.json(
      {
        error:
          "Webhook not configured (STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET).",
      },
      { status: 503 },
    );
  }

  const body = await request.text();
  const signature = request.headers.get("stripe-signature");
  if (!signature) {
    return NextResponse.json({ error: "Missing stripe-signature" }, { status: 400 });
  }

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(body, signature, webhookSecret);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Invalid signature";
    return NextResponse.json({ error: message }, { status: 400 });
  }

  if (event.type === "checkout.session.completed") {
    const session = event.data.object as Stripe.Checkout.Session;
    const packId = session.metadata?.pack_id;
    if (!packId) {
      console.warn("[stripe/webhook] checkout.session.completed without pack_id");
      return NextResponse.json({ received: true, skipped: "no pack_id" });
    }

    const customerId =
      session.customer_email ??
      session.metadata?.customer_id ??
      `stripe-${session.id}`;

    const token = issueTokenForCheckout({ packId, customerId });
    if (token && session.id) {
      cacheLicenseForSession(session.id, token);
      console.info(
        `[stripe/webhook] Issued MSC1 license for pack=${packId} customer=${customerId}`,
      );
      // Production: also email token via SendGrid/Resend and log to CRM
    } else {
      console.warn(
        "[stripe/webhook] MSC_LICENSE_PRIVATE_KEY not set — token not issued. " +
          "Call Python: python scripts/gen_license_key.py --customer-id ... --pack ...",
      );
    }
  }

  return NextResponse.json({ received: true });
}
