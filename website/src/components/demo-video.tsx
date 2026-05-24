// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

import Link from "next/link";
import { DEMO_VIDEO_URL, GITHUB_REPO } from "@/lib/site";

/** Map common watch URLs to embed-friendly iframe src. */
function embedSrc(url: string): string | null {
  try {
    const u = new URL(url);
    if (u.hostname.includes("youtube.com") && u.searchParams.get("v")) {
      return `https://www.youtube.com/embed/${u.searchParams.get("v")}`;
    }
    if (u.hostname === "youtu.be" && u.pathname.length > 1) {
      return `https://www.youtube.com/embed${u.pathname}`;
    }
    if (u.hostname.includes("vimeo.com")) {
      const id = u.pathname.split("/").filter(Boolean).pop();
      if (id) return `https://player.vimeo.com/video/${id}`;
    }
    if (u.pathname.includes("/embed/")) {
      return url;
    }
  } catch {
    return null;
  }
  return null;
}

export function DemoVideo() {
  const src = DEMO_VIDEO_URL ? embedSrc(DEMO_VIDEO_URL) : null;

  if (src) {
    return (
      <div className="aspect-video overflow-hidden rounded-2xl border border-white/10 bg-black shadow-xl">
        <iframe
          title="MySoftwareCompany.AI demo"
          src={src}
          className="h-full w-full"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      </div>
    );
  }

  return (
    <div className="flex aspect-video flex-col items-center justify-center rounded-2xl border border-dashed border-white/15 bg-slate-900/50 p-8 text-center">
      <p className="text-sm font-medium text-slate-300">Launch demo video</p>
      <p className="mt-2 max-w-md text-sm text-slate-500">
        Set{" "}
        <code className="rounded bg-slate-800 px-1.5 py-0.5 text-indigo-300">
          NEXT_PUBLIC_DEMO_VIDEO_URL
        </code>{" "}
        to a YouTube or Vimeo URL, or follow the recording outline in the repo.
      </p>
      <Link
        href={`${GITHUB_REPO}/blob/main/docs/DEMO.md`}
        className="mt-4 text-sm font-medium text-indigo-400 hover:text-indigo-300"
        target="_blank"
        rel="noopener noreferrer"
      >
        Demo script (docs/DEMO.md) →
      </Link>
    </div>
  );
}
