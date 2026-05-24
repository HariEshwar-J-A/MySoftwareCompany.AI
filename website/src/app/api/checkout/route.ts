// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

import { NextResponse } from "next/server";
import { getPremiumPack } from "@/lib/marketplace";
import { getStripe, siteUrl } from "@/lib/stripe";

export async function POST(request: Request) {
  const stripe = getStripe();
  if (!stripe) {
    return NextResponse.json(
      {
        error:
          "Stripe is not configured. Set STRIPE_SECRET_KEY and NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY.",
      },
      { status: 503 },
    );
  }

  let packId: string;
  try {
    const body = (await request.json()) as { packId?: string };
    if (!body.packId) throw new Error("packId required");
    packId = body.packId;
  } catch {
    return NextResponse.json({ error: "Invalid request body" }, { status: 400 });
  }

  const pack = getPremiumPack(packId);
  if (!pack) {
    return NextResponse.json({ error: "Unknown pack" }, { status: 404 });
  }

  const base = siteUrl();
  const envPriceId = process.env[`STRIPE_PRICE_${packId.toUpperCase().replace(/-/g, "_")}`];

  try {
    const session = await stripe.checkout.sessions.create({
      mode: "payment",
      success_url: `${base}/marketplace/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${base}/marketplace`,
      metadata: { pack_id: packId },
      line_items: envPriceId
        ? [{ price: envPriceId, quantity: 1 }]
        : [
            {
              quantity: 1,
              price_data: {
                currency: "usd",
                unit_amount: pack.priceUsd * 100,
                product_data: {
                  name: `${pack.name} org pack`,
                  description: pack.tagline,
                },
              },
            },
          ],
    });

    if (!session.url) {
      return NextResponse.json({ error: "No checkout URL" }, { status: 500 });
    }
    return NextResponse.json({ url: session.url });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Checkout failed";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
