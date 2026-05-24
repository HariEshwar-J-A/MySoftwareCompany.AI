import path from "path";
import { fileURLToPath } from "url";
import type { NextConfig } from "next";
import { loadEnvConfig } from "@next/env";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
loadEnvConfig(repoRoot);

const nextConfig: NextConfig = {
  /* config options here */
};

export default nextConfig;
