// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

import Link from "next/link";
import { Container } from "@/components/container";
import { DemoVideo } from "@/components/demo-video";
import { listPremiumPacks } from "@/lib/marketplace";
import { GITHUB_REPO, PYPI_INSTALL } from "@/lib/site";

export default function HomePage() {
  const featured = listPremiumPacks().slice(0, 3);

  return (
    <>
      <section className="relative overflow-hidden border-b border-white/5 pb-24 pt-20">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/40 via-slate-950 to-slate-950" />
        <Container className="relative">
          <p className="mb-4 inline-flex rounded-full border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-xs font-medium text-indigo-300">
            Terminal-native AI software agencies
          </p>
          <h1 className="max-w-3xl text-4xl font-bold tracking-tight text-white sm:text-5xl lg:text-6xl">
            Ship MVPs with coordinated agent teams—not a single chatbot
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-relaxed text-slate-400">
            MySoftwareCompany.AI vendors MetaGPT and 140+ specialist personas into
            org templates you run with{" "}
            <code className="rounded bg-slate-800 px-1.5 py-0.5 text-sm text-indigo-300">
              msc run
            </code>
            . Quality gates, evidence collection, and human review before anything
            client-facing ships.
          </p>
          <div className="mt-10 flex flex-wrap gap-4">
            <Link
              href={`${GITHUB_REPO}#install`}
              className="rounded-xl bg-indigo-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30 transition hover:bg-indigo-400"
            >
              Get started
            </Link>
            <Link
              href="/marketplace"
              className="rounded-xl border border-white/15 px-6 py-3 text-sm font-semibold text-white transition hover:bg-white/5"
            >
              Browse org marketplace
            </Link>
            <Link
              href="/services"
              className="rounded-xl border border-white/15 px-6 py-3 text-sm font-semibold text-white transition hover:bg-white/5"
            >
              Hire our team
            </Link>
          </div>
          <p className="mt-6 font-mono text-sm text-slate-500">
            <span className="text-slate-600">$</span> {PYPI_INSTALL}
          </p>
        </Container>
      </section>

      <section className="border-b border-white/5 py-20">
        <Container>
          <h2 className="text-2xl font-semibold text-white">See it in action</h2>
          <p className="mt-2 max-w-2xl text-slate-400">
            Launch demo — terminal workflow, benchmark gate, and marketplace checkout.
          </p>
          <div className="mt-10 max-w-4xl">
            <DemoVideo />
          </div>
        </Container>
      </section>

      <section className="py-20">
        <Container>
          <h2 className="text-2xl font-semibold text-white">How it works</h2>
          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {[
              {
                step: "01",
                title: "Pick an org",
                body: "OSS templates for MVPs, microservices, marketing, and incidents—or unlock premium vertical packs.",
              },
              {
                step: "02",
                title: "Run from the CLI",
                body: "Describe your idea, set a budget, and let phased playbooks orchestrate backend, frontend, and QA agents.",
              },
              {
                step: "03",
                title: "Gate before ship",
                body: "Evidence collectors and reality checkers block bad output. Human review is mandatory for client work.",
              },
            ].map((item) => (
              <div
                key={item.step}
                className="rounded-2xl border border-white/10 bg-slate-900/50 p-6"
              >
                <span className="text-sm font-bold text-indigo-400">
                  {item.step}
                </span>
                <h3 className="mt-2 text-lg font-semibold text-white">
                  {item.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-400">
                  {item.body}
                </p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      <section className="border-y border-white/5 bg-slate-900/30 py-20">
        <Container>
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <h2 className="text-2xl font-semibold text-white">
                Featured org packs
              </h2>
              <p className="mt-2 text-slate-400">
                Same catalog as{" "}
                <code className="text-indigo-300">msc marketplace orgs</code>
              </p>
            </div>
            <Link
              href="/marketplace"
              className="text-sm font-medium text-indigo-400 hover:text-indigo-300"
            >
              View all →
            </Link>
          </div>
          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {featured.map((pack) => (
              <div
                key={pack.pack_id}
                className="rounded-2xl border border-white/10 bg-slate-950/60 p-6"
              >
                <h3 className="font-semibold text-white">{pack.name}</h3>
                <p className="mt-2 text-sm text-slate-400">{pack.tagline}</p>
                <p className="mt-4 text-lg font-semibold text-indigo-300">
                  ${pack.priceUsd}
                </p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      <section className="py-20">
        <Container className="rounded-2xl border border-indigo-500/20 bg-gradient-to-br from-indigo-950/50 to-slate-950 p-10 text-center">
          <h2 className="text-2xl font-semibold text-white">
            Ready to run your first agency?
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-slate-400">
            Install the CLI, dry-run an org, or talk to us about a guided MVP
            build with human review in the SLA.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-4">
            <Link
              href={`${GITHUB_REPO}#quick-start`}
              className="rounded-xl bg-white px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-200"
            >
              Get started
            </Link>
            <Link
              href="/pricing"
              className="rounded-xl border border-white/20 px-6 py-3 text-sm font-semibold text-white transition hover:bg-white/5"
            >
              See pricing
            </Link>
            <Link
              href="/contact"
              className="rounded-xl border border-white/20 px-6 py-3 text-sm font-semibold text-white transition hover:bg-white/5"
            >
              Talk to us
            </Link>
          </div>
        </Container>
      </section>
    </>
  );
}
