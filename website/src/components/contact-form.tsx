// Copyright (c) 2026 MySoftwareCompany.AI
// SPDX-License-Identifier: BUSL-1.1

"use client";

import { useState } from "react";

export function ContactForm() {
  const [status, setStatus] = useState<"idle" | "loading" | "ok" | "error">(
    "idle",
  );
  const [message, setMessage] = useState("");

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setStatus("loading");
    setMessage("");
    const form = e.currentTarget;
    const data = Object.fromEntries(new FormData(form).entries());
    try {
      const res = await fetch("/api/lead", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      const body = (await res.json()) as { error?: string; ok?: boolean };
      if (!res.ok) throw new Error(body.error ?? "Failed to send");
      setStatus("ok");
      setMessage("Thanks — we'll be in touch within one business day.");
      form.reset();
    } catch (err) {
      setStatus("error");
      setMessage(err instanceof Error ? err.message : "Something went wrong");
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-5">
      <div className="grid gap-5 md:grid-cols-2">
        <label className="block">
          <span className="text-sm font-medium text-slate-300">Name</span>
          <input
            name="name"
            required
            className="mt-1 w-full rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-white outline-none ring-indigo-500/0 transition focus:ring-2"
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-300">Email</span>
          <input
            name="email"
            type="email"
            required
            className="mt-1 w-full rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-white outline-none transition focus:ring-2 focus:ring-indigo-500/50"
          />
        </label>
      </div>
      <label className="block">
        <span className="text-sm font-medium text-slate-300">Company</span>
        <input
          name="company"
          className="mt-1 w-full rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-white outline-none transition focus:ring-2 focus:ring-indigo-500/50"
        />
      </label>
      <label className="block">
        <span className="text-sm font-medium text-slate-300">
          What are you building?
        </span>
        <textarea
          name="message"
          required
          rows={5}
          className="mt-1 w-full rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-white outline-none transition focus:ring-2 focus:ring-indigo-500/50"
        />
      </label>
      <button
        type="submit"
        disabled={status === "loading"}
        className="rounded-xl bg-indigo-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 transition hover:bg-indigo-400 disabled:opacity-60"
      >
        {status === "loading" ? "Sending…" : "Send message"}
      </button>
      {message ? (
        <p
          className={`text-sm ${status === "ok" ? "text-emerald-400" : "text-rose-400"}`}
        >
          {message}
        </p>
      ) : null}
    </form>
  );
}
