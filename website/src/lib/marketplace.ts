// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

import manifest from "@/data/marketplace-manifest.json";

export type PremiumPack = {
  pack_id: string;
  name: string;
  description: string;
  mode: string | null;
  budget_default: number | null;
  priceUsd: number;
  tagline: string;
  features: string[];
};

export function listPremiumPacks(): PremiumPack[] {
  return manifest.packs as PremiumPack[];
}

export function getPremiumPack(packId: string): PremiumPack | undefined {
  return listPremiumPacks().find((p) => p.pack_id === packId);
}
