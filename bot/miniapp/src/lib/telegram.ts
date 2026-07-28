interface TelegramWebApp {
  initData: string;
  colorScheme?: "light" | "dark";
  themeParams?: Record<string, string | undefined>;
  ready: () => void;
  expand: () => void;
}

declare global {
  interface Window {
    Telegram?: { WebApp: TelegramWebApp };
  }
}

export function getInitData(): string {
  const webApp = window.Telegram?.WebApp;
  if (webApp?.initData) return webApp.initData;

  // Dev-only fallback so the dashboard is viewable in a plain browser tab, outside
  // Telegram, while building locally. import.meta.env.DEV is false in a production
  // build, so this branch is compiled out and never reaches a real deployment.
  if (import.meta.env.DEV) {
    return localStorage.getItem("debug_init_data") ?? "";
  }

  return "";
}

export function initTelegramWebApp() {
  const webApp = window.Telegram?.WebApp;
  webApp?.ready();
  webApp?.expand();

  if (!webApp) return;

  document.documentElement.classList.toggle("dark", webApp.colorScheme === "dark");
  const theme = webApp.themeParams ?? {};
  const root = document.documentElement;

  if (theme.bg_color) root.style.setProperty("--background", theme.bg_color);
  if (theme.text_color) root.style.setProperty("--foreground", theme.text_color);
  if (theme.button_color) root.style.setProperty("--primary", theme.button_color);
  if (theme.button_text_color) root.style.setProperty("--primary-foreground", theme.button_text_color);
  if (theme.secondary_bg_color) {
    root.style.setProperty("--card", theme.secondary_bg_color);
    root.style.setProperty("--muted", theme.secondary_bg_color);
  }
  if (theme.hint_color) root.style.setProperty("--muted-foreground", theme.hint_color);
}
