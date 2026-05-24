// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

import type { Metadata } from "next";
import Link from "next/link";
import { Container } from "@/components/container";
import { listPremiumPacks } from "@/lib/marketplace";

export const metadata: Metadata = {
  title: "Pricing",
  description: "CLI usage, marketplace org packs, and services tiers.",
};

export default function PricingPage() {
  const packs = listPremiumPacks();

  return (
    <Container className="py-16">
      <p className="text-sm font-medium uppercase tracking-wider text-indigo-400">
        Pricing
      </p>
      <h1 className="mt-2 text-3xl font-bold text-white sm:text-4xl">
        Simple, transparent pricing
      </h1>

      <section className="mt-14">
        <h2 className="text-xl font-semibold text-white">CLI & OSS orgs</h2>
        <p className="mt-2 text-slate-400">
          Core runtime and four OSS org templates are free for non-production use
          under BUSL-1.1. Production use requires a commercial license — see{" "}
          <Link href="/contact" className="text-indigo-400 hover:underline">
            COMMERCIAL
          </Link>
          .
        </p>
        <div className="mt-6 rounded-2xl border border-white/10 bg-slate-900/40 p-6">
          <p className="text-3xl font-bold text-white">$0</p>
          <p className="mt-1 text-sm text-slate-400">
            startup-mvp · nexus-micro · marketing-campaign · incident-response
          </p>
        </div>
      </section>

      <section className="mt-14">
        <h2 className="text-xl font-semibold text-white">Marketplace org packs</h2>
        <p className="mt-2 text-slate-400">
          One-time purchase per pack. MSC1 license stored in{" "}
          <code className="text-indigo-300">~/.msc/license.json</code>.
        </p>
        <div className="mt-6 overflow-hidden rounded-2xl border border-white/10">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-900/80 text-slate-400">
              <tr>
                <th className="px-6 py-4 font-medium">Pack</th>
                <th className="px-6 py-4 font-medium">Description</th>
                <th className="px-6 py-4 font-medium text-right">Price</th>
              </tr>
            </thead>
            <tbody>
              {packs.map((pack) => (
                <tr key={pack.pack_id} className="border-t border-white/5">
                  <td className="px-6 py-4 font-medium text-white">
                    {pack.name}
                  </td>
                  <td className="px-6 py-4 text-slate-400">{pack.tagline}</td>
                  <td className="px-6 py-4 text-right font-semibold text-indigo-300">
                    ${pack.priceUsd}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <Link
          href="/marketplace"
          className="mt-6 inline-flex text-sm font-medium text-indigo-400 hover:text-indigo-300"
        >
          Buy a pack →
        </Link>
      </section>

      <section className="mt-14">
        <h2 className="text-xl font-semibold text-white">Services</h2>
        <p className="mt-2 text-slate-400">
          Hands-on builds with human review in the SLA.{" "}
          <Link href="/services" className="text-indigo-400 hover:underline">
            See service tiers
          </Link>
          .
        </p>
      </section>
    </Container>
  );
}
