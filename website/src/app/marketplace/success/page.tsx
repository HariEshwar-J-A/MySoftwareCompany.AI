// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

import { Suspense } from "react";
import { MarketplaceSuccessClient } from "./success-client";

export default function MarketplaceSuccessPage() {
  return (
    <Suspense
      fallback={
        <p className="p-16 text-center text-slate-500">Loading purchase…</p>
      }
    >
      <MarketplaceSuccessClient />
    </Suspense>
  );
}
