// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

import Link from "next/link";
import { GITHUB_REPO, PYPI_URL } from "@/lib/site";

const external = [
  { href: GITHUB_REPO, label: "GitHub" },
  { href: `${GITHUB_REPO}#install`, label: "Docs" },
  { href: PYPI_URL, label: "PyPI" },
  { href: `${GITHUB_REPO}/blob/main/CHANGELOG.md`, label: "Changelog" },
];

export function SiteFooter() {
  return (
    <footer className="mt-auto border-t border-white/10 bg-slate-950">
      <div className="mx-auto flex max-w-6xl flex-col gap-8 px-6 py-12 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="text-sm font-semibold text-white">MySoftwareCompany.AI</p>
          <p className="mt-1 max-w-sm text-sm text-slate-400">
            AI software agencies you run from the terminal. BUSL-1.1 core; MIT
            vendored deps. v0.1.0
          </p>
        </div>
        <div className="flex flex-wrap gap-x-8 gap-y-4">
          <div className="flex flex-col gap-2 text-sm text-slate-400">
            <span className="font-medium text-slate-300">Product</span>
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
          <div className="flex flex-col gap-2 text-sm text-slate-400">
            <span className="font-medium text-slate-300">Resources</span>
            {external.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="hover:text-white"
                target="_blank"
                rel="noopener noreferrer"
              >
                {link.label}
              </a>
            ))}
          </div>
        </div>
      </div>
      <div className="border-t border-white/5 py-4 text-center text-xs text-slate-500">
        © {new Date().getFullYear()} MySoftwareCompany.AI — Core licensed under
        BUSL-1.1
      </div>
    </footer>
  );
}
