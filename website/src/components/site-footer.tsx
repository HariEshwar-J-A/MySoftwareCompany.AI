// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="mt-auto border-t border-white/10 bg-slate-950">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 px-6 py-12 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm font-semibold text-white">MySoftwareCompany.AI</p>
          <p className="mt-1 max-w-sm text-sm text-slate-400">
            AI software agencies you run from the terminal. BUSL-1.1 core; MIT
            vendored deps.
          </p>
        </div>
        <div className="flex flex-wrap gap-6 text-sm text-slate-400">
          <Link href="/services" className="hover:text-white">
            Services
          </Link>
          <Link href="/marketplace" className="hover:text-white">
            Marketplace
          </Link>
          <Link href="/pricing" className="hover:text-white">
            Pricing
          </Link>
          <Link href="/contact" className="hover:text-white">
            Contact
          </Link>
        </div>
      </div>
      <div className="border-t border-white/5 py-4 text-center text-xs text-slate-500">
        © {new Date().getFullYear()} MySoftwareCompany.AI — Core licensed under
        BUSL-1.1
      </div>
    </footer>
  );
}
