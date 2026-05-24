// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

import type { Metadata } from "next";
import { Container } from "@/components/container";
import { PackCard } from "@/components/pack-card";
import { listPremiumPacks } from "@/lib/marketplace";

export const metadata: Metadata = {
  title: "Marketplace",
  description: "Premium org packs for the msc CLI — unlock vertical-specific agent teams.",
};

export default function MarketplacePage() {
  const packs = listPremiumPacks();

  return (
    <Container className="py-16">
      <p className="text-sm font-medium uppercase tracking-wider text-indigo-400">
        Marketplace
      </p>
      <h1 className="mt-2 text-3xl font-bold text-white sm:text-4xl">
        Premium org packs
      </h1>
      <p className="mt-4 max-w-2xl text-slate-400">
        Purchase a pack, receive an MSC1 license token, then run{" "}
        <code className="rounded bg-slate-800 px-1.5 py-0.5 text-indigo-300">
          msc marketplace login &lt;key&gt;
        </code>{" "}
        to unlock it locally. Catalog matches{" "}
        <code className="text-indigo-300">msc marketplace orgs</code>.
      </p>

      {packs.length === 0 ? (
        <p className="mt-12 rounded-xl border border-amber-500/30 bg-amber-950/20 p-6 text-amber-200">
          No premium packs found. Run{" "}
          <code>npm run gen:manifest</code> after adding packs under{" "}
          <code>orgs/premium/</code>.
        </p>
      ) : (
        <div className="mt-12 grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {packs.map((pack) => (
            <PackCard key={pack.pack_id} pack={pack} />
          ))}
        </div>
      )}
    </Container>
  );
}
