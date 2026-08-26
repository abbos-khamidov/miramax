import { defineConfig } from "vite";
import path from "path";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ command }) => ({
  // Served from miramaxmpp.uz/bonuses/ in production (same nginx/domain as the rest
  // of the site — no separate hosting to keep in sync). Dev server stays at root.
  base: command === "build" ? "/bonuses/" : "/",
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: true,
    // The Mini App runs inside the Telegram client's browser, reachable only over the
    // public tunnel URL — proxying /api here means only one HTTPS tunnel is needed
    // (pointed at this dev server) instead of a second one for the backend container.
    proxy: {
      "/api": {
        target: "http://backend:8000",
        changeOrigin: true,
      },
    },
  },
}));
