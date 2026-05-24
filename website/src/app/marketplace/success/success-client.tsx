// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Container } from "@/components/container";

type SessionResult = {
  packId?: string;
  customerId?: string;
  token?: string;
  error?: string;
};

export function MarketplaceSuccessClient() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session_id");
  const [result, setResult] = useState<SessionResult | null>(null);
  const [copied, setCopied] = useState(false);

  const missingSession = !sessionId;

  useEffect(() => {
    if (!sessionId) return;
    fetch(`/api/checkout/session?session_id=${encodeURIComponent(sessionId)}`)
      .then((r) => r.json())
      .then((data: SessionResult) => setResult(data))
      .catch(() => setResult({ error: "Failed to load purchase details." }));
  }, [sessionId]);

  const display = missingSession
    ? { error: "Missing session_id query parameter." }
    : result;

  async function copyToken() {
    if (!display?.token) return;
    await navigator.clipboard.writeText(display.token);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <Container className="py-16">
      <p className="text-sm font-medium uppercase tracking-wider text-emerald-400">
        Purchase complete
      </p>
      <h1 className="mt-2 text-3xl font-bold text-white">Your license key</h1>
      <p className="mt-4 max-w-xl text-slate-400">
        Save this MSC1 token and activate it locally with the CLI command below.
      </p>

      {!display ? (
        <p className="mt-10 text-slate-500">Loading purchase details…</p>
      ) : display.error ? (
        <p className="mt-10 rounded-xl border border-rose-500/30 bg-rose-950/20 p-6 text-rose-300">
          {display.error}
        </p>
      ) : (
        <div className="mt-10 space-y-6">
          <dl className="grid gap-4 text-sm md:grid-cols-2">
            <div className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
              <dt className="text-slate-500">Pack</dt>
              <dd className="mt-1 font-medium text-white">{display.packId}</dd>
            </div>
            <div className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
              <dt className="text-slate-500">Customer</dt>
              <dd className="mt-1 font-medium text-white">{display.customerId}</dd>
            </div>
          </dl>

          {display.token ? (
            <>
              <div className="rounded-xl border border-indigo-500/30 bg-slate-900 p-4">
                <p className="text-xs font-medium uppercase text-slate-500">
                  MSC1 license token
                </p>
                <code className="mt-2 block break-all font-mono text-sm text-indigo-200">
                  {display.token}
                </code>
                <button
                  type="button"
                  onClick={copyToken}
                  className="mt-4 rounded-lg bg-indigo-500 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-400"
                >
                  {copied ? "Copied!" : "Copy token"}
                </button>
              </div>
              <div className="rounded-xl border border-white/10 bg-slate-950 p-6">
                <p className="text-sm font-medium text-white">Activate locally</p>
                <pre className="mt-3 overflow-x-auto rounded-lg bg-black/40 p-4 font-mono text-sm text-emerald-300">
                  {`msc marketplace login ${display.token}`}
                </pre>
                <p className="mt-3 text-sm text-slate-500">
                  Then run{" "}
                  <code className="text-indigo-300">msc marketplace orgs</code> to
                  confirm the pack shows as entitled.
                </p>
              </div>
            </>
          ) : (
            <p className="text-amber-300">
              Payment received. License issuance requires{" "}
              <code>MSC_LICENSE_PRIVATE_KEY</code> on the server — check your email
              or contact support.
            </p>
          )}
        </div>
      )}

      <Link
        href="/marketplace"
        className="mt-10 inline-flex text-sm font-medium text-indigo-400 hover:text-indigo-300"
      >
        ← Back to marketplace
      </Link>
    </Container>
  );
}
