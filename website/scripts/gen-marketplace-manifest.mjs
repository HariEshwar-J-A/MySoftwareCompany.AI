#!/usr/bin/env node
// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

/**
 * Build-time manifest from orgs/premium/*.yaml (parity with msc marketplace orgs).
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import yaml from "yaml";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "../..");
const premiumDir = path.join(repoRoot, "orgs/premium");
const outPath = path.join(__dirname, "../src/data/marketplace-manifest.json");

/** Display pricing — Stripe checkout uses price_data or STRIPE_PRICE_* env vars. */
const PACK_PRICING = {
  "fintech-studio": {
    priceUsd: 499,
    tagline: "Regulated fintech MVP studio",
    features: [
      "Compliance-first NEXUS-Sprint org",
      "Finance, legal, backend & frontend agents",
      "Human review gate before deliver",
    ],
  },
};

function listPremiumPackIds() {
  if (!fs.existsSync(premiumDir)) return [];
  return fs
    .readdirSync(premiumDir)
    .filter((name) => name.endsWith(".yaml.enc"))
    .map((name) => name.replace(/\.yaml\.enc$/, ""))
    .sort();
}

function loadYamlMetadata(packId) {
  const plainPath = path.join(premiumDir, `${packId}.yaml`);
  if (!fs.existsSync(plainPath)) {
    return { pack_id: packId, name: packId, description: "" };
  }
  const doc = yaml.parse(fs.readFileSync(plainPath, "utf8"));
  return {
    pack_id: doc.pack_id ?? packId,
    name: doc.name ?? packId,
    description: doc.description ?? "",
    mode: doc.mode ?? null,
    budget_default: doc.budget_default ?? null,
  };
}

const packs = listPremiumPackIds().map((packId) => {
  const meta = loadYamlMetadata(packId);
  const pricing = PACK_PRICING[packId] ?? {
    priceUsd: 299,
    tagline: meta.description,
    features: [],
  };
  return {
    ...meta,
    priceUsd: pricing.priceUsd,
    tagline: pricing.tagline ?? meta.description,
    features: pricing.features ?? [],
  };
});

const manifest = {
  generatedAt: new Date().toISOString(),
  packs,
};

fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, `${JSON.stringify(manifest, null, 2)}\n`, "utf8");
console.log(`Wrote ${packs.length} pack(s) → ${outPath}`);
