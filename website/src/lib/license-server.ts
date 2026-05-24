// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

import fs from "node:fs";
import path from "node:path";
import { buildMarketplacePayload, issueLicenseToken } from "@/lib/license";

/**
 * Publisher private key for MSC1 issuance (webhook / success page).
 * Set MSC_LICENSE_PRIVATE_KEY_PATH or MSC_LICENSE_PRIVATE_KEY (PEM contents).
 * Production: use a secrets manager; never commit real keys.
 */
export function loadLicensePrivateKeyPem(): string | null {
  const inline = process.env.MSC_LICENSE_PRIVATE_KEY;
  if (inline?.includes("BEGIN")) {
    return inline.replace(/\\n/g, "\n");
  }
  const keyPath =
    process.env.MSC_LICENSE_PRIVATE_KEY_PATH ??
    path.resolve(/* turbopackIgnore: true */ process.cwd(), "../scripts/.marketplace_dev_key.pem");
  if (fs.existsSync(keyPath)) {
    return fs.readFileSync(keyPath, "utf8");
  }
  return null;
}

/** Issue token from a paid Stripe session (shared by webhook + success API). */
export function issueTokenForCheckout(params: {
  packId: string;
  customerId: string;
}): string | null {
  const pem = loadLicensePrivateKeyPem();
  if (!pem) return null;
  const payload = buildMarketplacePayload(params.customerId, params.packId);
  return issueLicenseToken(payload, pem);
}
