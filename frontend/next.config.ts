import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Bundle autónomo (server.js + deps mínimas) para una imagen Docker liviana.
  output: "standalone",
};

export default nextConfig;
