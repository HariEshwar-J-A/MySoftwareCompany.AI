// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

/** Public site constants (override via NEXT_PUBLIC_* env at build time). */

export const GITHUB_REPO =
  process.env.NEXT_PUBLIC_GITHUB_REPO ??
  "https://github.com/mysoftwarecompany/MySoftwareCompany.AI";

export const PYPI_INSTALL = "pip install mscai==0.1.0";

export const PYPI_URL = "https://pypi.org/project/mscai/";

/** YouTube/Vimeo watch URL; empty until a launch video is published. */
export const DEMO_VIDEO_URL = process.env.NEXT_PUBLIC_DEMO_VIDEO_URL ?? "";
