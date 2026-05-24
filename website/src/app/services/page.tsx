// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

import Link from "next/link";
import type { Metadata } from "next";
import { Container } from "@/components/container";

export const metadata: Metadata = {
  title: "Services",
  description:
    "Spike, MVP build, and custom engagements with mandatory human review in every SLA.",
};

const tiers = [
  {
    name: "Spike",
    price: "From $2,500",
    summary: "1–2 week feasibility slice with evidence and a go/no-go recommendation.",
    includes: [
      "Scoped discovery with product + UX agents",
      "Working prototype or architecture spike",
      "Written scorecard and next-step plan",
      "Human review before delivery",
    ],
  },
  {
    name: "MVP build",
    price: "From $15,000",
    summary: "End-to-end MVP using your chosen org template and quality gates.",
    includes: [
      "Full NEXUS sprint with dev/QA loop",
      "Tests, artifacts, and deployment notes",
      "Weekly human review checkpoints",
      "30-day fix window for gate failures",
    ],
    featured: true,
  },
  {
    name: "Custom",
    price: "Quote",
    summary: "Multi-org programs, compliance-heavy verticals, or dedicated agent tuning.",
    includes: [
      "Solution design workshop",
      "Custom org packs and playbooks",
      "Embedded human tech lead",
      "SLA with non-bypassable review gate",
    ],
  },
];

export default function ServicesPage() {
  return (
    <Container className="py-16">
      <p className="text-sm font-medium uppercase tracking-wider text-indigo-400">
        Services
      </p>
      <h1 className="mt-2 max-w-2xl text-3xl font-bold text-white sm:text-4xl">
        We run the agents. You get production-ready output.
      </h1>
      <p className="mt-4 max-w-2xl text-slate-400">
        Every engagement includes a mandatory human review gate before client
        handoff—contractual in our SLA.{" "}
        <code className="text-indigo-300">--no-human-review</code> is for personal
        CLI use only.
      </p>

      <div className="mt-14 grid gap-8 lg:grid-cols-3">
        {tiers.map((tier) => (
          <article
            key={tier.name}
            className={`flex flex-col rounded-2xl border p-8 ${
              tier.featured
                ? "border-indigo-500/50 bg-indigo-950/30 shadow-xl shadow-indigo-500/10"
                : "border-white/10 bg-slate-900/40"
            }`}
          >
            {tier.featured ? (
              <span className="mb-4 w-fit rounded-full bg-indigo-500/20 px-3 py-1 text-xs font-semibold text-indigo-300">
                Most popular
              </span>
            ) : null}
            <h2 className="text-xl font-semibold text-white">{tier.name}</h2>
            <p className="mt-1 text-2xl font-bold text-indigo-300">{tier.price}</p>
            <p className="mt-3 text-sm text-slate-400">{tier.summary}</p>
            <ul className="mt-6 flex-1 space-y-2 text-sm text-slate-300">
              {tier.includes.map((item) => (
                <li key={item} className="flex gap-2">
                  <span className="text-indigo-400">✓</span>
                  {item}
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>

      <div className="mt-16 rounded-2xl border border-white/10 bg-slate-900/50 p-8">
        <h2 className="text-lg font-semibold text-white">Scope examples</h2>
        <ul className="mt-4 grid gap-3 text-sm text-slate-400 md:grid-cols-2">
          <li>• Fintech onboarding flow with compliance checker gate</li>
          <li>• Internal admin CRUD with FastAPI + React SPA</li>
          <li>• Incident-response runbook automation POC</li>
          <li>• Marketing landing + analytics instrumentation</li>
        </ul>
        <Link
          href="/contact"
          className="mt-8 inline-flex rounded-xl bg-indigo-500 px-6 py-3 text-sm font-semibold text-white hover:bg-indigo-400"
        >
          Start a conversation
        </Link>
      </div>
    </Container>
  );
}
