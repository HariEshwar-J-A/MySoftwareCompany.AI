// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

/**
 * Ephemeral session → license token cache populated by the Stripe webhook.
 * Replace with Redis / DB in production; success page falls back to re-issuance.
 */

const tokensBySession = new Map<string, string>();

export function cacheLicenseForSession(sessionId: string, token: string): void {
  tokensBySession.set(sessionId, token);
}

export function getCachedLicense(sessionId: string): string | undefined {
  return tokensBySession.get(sessionId);
}
