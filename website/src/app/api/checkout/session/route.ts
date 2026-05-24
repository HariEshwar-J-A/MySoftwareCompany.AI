// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

import { NextResponse } from "next/server";
import { getCachedLicense, cacheLicenseForSession } from "@/lib/license-store";
import { issueTokenForCheckout } from "@/lib/license-server";
import { getStripe } from "@/lib/stripe";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const sessionId = searchParams.get("session_id");
  if (!sessionId) {
    return NextResponse.json({ error: "session_id required" }, { status: 400 });
  }

  const cached = getCachedLicense(sessionId);
  if (cached) {
    return NextResponse.json({ token: cached });
  }

  const stripe = getStripe();
  if (!stripe) {
    return NextResponse.json(
      { error: "Stripe not configured" },
      { status: 503 },
    );
  }

  try {
    const session = await stripe.checkout.sessions.retrieve(sessionId);
    if (session.payment_status !== "paid") {
      return NextResponse.json({ error: "Payment not completed" }, { status: 402 });
    }

    const packId = session.metadata?.pack_id;
    if (!packId) {
      return NextResponse.json({ error: "Missing pack metadata" }, { status: 400 });
    }

    const customerId =
      session.customer_email ??
      session.metadata?.customer_id ??
      `stripe-${sessionId.slice(0, 12)}`;

    const token = issueTokenForCheckout({ packId, customerId });
    if (token) {
      cacheLicenseForSession(sessionId, token);
    }

    return NextResponse.json({
      packId,
      customerId,
      token: token ?? undefined,
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Session lookup failed";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
