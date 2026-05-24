// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

import type { Metadata } from "next";
import { ContactForm } from "@/components/contact-form";
import { Container } from "@/components/container";

export const metadata: Metadata = {
  title: "Contact",
  description: "Get in touch about services, marketplace packs, or commercial licensing.",
};

export default function ContactPage() {
  return (
    <Container className="py-16">
      <div className="grid gap-12 lg:grid-cols-2">
        <div>
          <p className="text-sm font-medium uppercase tracking-wider text-indigo-400">
            Contact
          </p>
          <h1 className="mt-2 text-3xl font-bold text-white sm:text-4xl">
            Let&apos;s talk about your build
          </h1>
          <p className="mt-4 text-slate-400">
            Services inquiries, marketplace support, or commercial licensing —
            we respond within one business day.
          </p>
          <dl className="mt-10 space-y-4 text-sm">
            <div>
              <dt className="font-medium text-slate-300">Email</dt>
              <dd className="text-indigo-400">hello@mysoftwarecompany.ai</dd>
            </div>
            <div>
              <dt className="font-medium text-slate-300">CLI docs</dt>
              <dd className="text-slate-400">
                <code>msc --help</code> after{" "}
                <code>pip install mscai</code>
              </dd>
            </div>
          </dl>
        </div>
        <div className="rounded-2xl border border-white/10 bg-slate-900/40 p-8">
          <ContactForm />
        </div>
      </div>
    </Container>
  );
}
