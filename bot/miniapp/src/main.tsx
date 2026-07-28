import { createRoot } from "react-dom/client";
import App from "./App";
import { initTelegramWebApp } from "./lib/telegram";
import "./styles/index.css";

initTelegramWebApp();

createRoot(document.getElementById("root")!).render(<App />);
