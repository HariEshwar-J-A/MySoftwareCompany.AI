// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

/**
 * Lead capture stub — forwards to HubSpot / Plain / email in production.
 * Logs payload server-side when LEAD_WEBHOOK_URL is unset.
 */

import { NextResponse } from "next/server";

type LeadPayload = {
  name?: string;
  email?: string;
  company?: string;
  message?: string;
};

export async function POST(request: Request) {
  let payload: LeadPayload;
  try {
    payload = (await request.json()) as LeadPayload;
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!payload.email || !payload.name || !payload.message) {
    return NextResponse.json(
      { error: "name, email, and message are required" },
      { status: 400 },
    );
  }

  const forwardUrl = process.env.LEAD_WEBHOOK_URL;
  if (forwardUrl) {
    try {
      const res = await fetch(forwardUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...payload,
          source: "mysoftwarecompany.ai/contact",
          submittedAt: new Date().toISOString(),
        }),
      });
      if (!res.ok) {
        return NextResponse.json(
          { error: "Upstream CRM rejected the lead" },
          { status: 502 },
        );
      }
    } catch {
      return NextResponse.json({ error: "Failed to forward lead" }, { status: 502 });
    }
  } else {
    console.info("[api/lead] New lead (stub — set LEAD_WEBHOOK_URL to forward):", {
      name: payload.name,
      email: payload.email,
      company: payload.company,
    });
  }

  return NextResponse.json({ ok: true });
}
