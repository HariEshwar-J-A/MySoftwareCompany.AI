// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

/**
 * MSC1 license tokens — mirrors packages/msc/entitlements/keys.py for webhook issuance.
 * Production may delegate to gen_license_key.py via an internal admin endpoint.
 */

import { createPrivateKey, sign } from "node:crypto";

export const LICENSE_PREFIX = "MSC1";

export type LicensePayload = {
  customer_id: string;
  tier: string;
  entitled_packs: string[];
  expires_at: string | null;
};

function base64UrlEncode(data: Buffer | string): string {
  const buf = typeof data === "string" ? Buffer.from(data, "utf8") : data;
  return buf.toString("base64url");
}

/** Issue an MSC1 token compatible with `msc marketplace login`. */
export function issueLicenseToken(
  payload: LicensePayload,
  privateKeyPem: string,
): string {
  const bodyJson = JSON.stringify({
    customer_id: payload.customer_id,
    tier: payload.tier,
    entitled_packs: payload.entitled_packs,
    expires_at: payload.expires_at,
  });
  const body = base64UrlEncode(bodyJson);
  const privateKey = createPrivateKey(privateKeyPem);
  const signature = sign(null, Buffer.from(body, "utf8"), privateKey);
  return `${LICENSE_PREFIX}.${body}.${base64UrlEncode(signature)}`;
}

export function buildMarketplacePayload(
  customerId: string,
  packId: string,
): LicensePayload {
  return {
    customer_id: customerId,
    tier: "marketplace",
    entitled_packs: [packId],
    expires_at: null,
  };
}
