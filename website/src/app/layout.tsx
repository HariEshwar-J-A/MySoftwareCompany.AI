// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { GITHUB_REPO } from "@/lib/site";
import "./globals.css";

const siteUrl =
  process.env.NEXT_PUBLIC_SITE_URL ?? "https://mysoftwarecompany.ai";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "MySoftwareCompany.AI — AI software agencies from the terminal",
    template: "%s · MySoftwareCompany.AI",
  },
  description:
    "Configure an org, describe an idea, and let a coordinated AI team build it—with quality gates and human review before client handoff.",
  keywords: [
    "AI agents",
    "software agency",
    "MetaGPT",
    "multi-agent",
    "CLI",
    "marketplace",
  ],
  openGraph: {
    title: "MySoftwareCompany.AI",
    description: "AI software agencies you run from the terminal.",
    siteName: "MySoftwareCompany.AI",
    type: "website",
    url: siteUrl,
  },
  twitter: {
    card: "summary_large_image",
    title: "MySoftwareCompany.AI",
    description: "AI software agencies you run from the terminal.",
  },
  alternates: {
    canonical: siteUrl,
  },
  other: {
    "github-repo": GITHUB_REPO,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full`}
    >
      <body className="flex min-h-full flex-col bg-slate-950 font-sans text-slate-100 antialiased">
        <SiteHeader />
        <main className="flex-1">{children}</main>
        <SiteFooter />
      </body>
    </html>
  );
}
