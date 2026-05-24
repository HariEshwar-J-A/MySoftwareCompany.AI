// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

import type { PremiumPack } from "@/lib/marketplace";
import { CheckoutButton } from "./checkout-button";

export function PackCard({ pack }: { pack: PremiumPack }) {
  return (
    <article className="flex flex-col rounded-2xl border border-white/10 bg-slate-900/60 p-6 shadow-xl shadow-black/20 backdrop-blur">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-indigo-400">
            Premium org pack
          </p>
          <h3 className="mt-1 text-xl font-semibold text-white">{pack.name}</h3>
          <p className="mt-2 text-sm text-slate-400">{pack.tagline}</p>
        </div>
        <span className="shrink-0 rounded-full bg-slate-800 px-3 py-1 text-sm font-semibold text-white">
          ${pack.priceUsd}
        </span>
      </div>
      {pack.features.length > 0 ? (
        <ul className="mb-6 flex-1 space-y-2 text-sm text-slate-300">
          {pack.features.map((feature) => (
            <li key={feature} className="flex gap-2">
              <span className="text-indigo-400">✓</span>
              {feature}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mb-6 flex-1 text-sm text-slate-400">{pack.description}</p>
      )}
      <CheckoutButton pack={pack} />
      <p className="mt-3 text-center text-xs text-slate-500">
        Unlocks via{" "}
        <code className="rounded bg-slate-800 px-1 py-0.5 text-indigo-300">
          msc marketplace login
        </code>
      </p>
    </article>
  );
}
