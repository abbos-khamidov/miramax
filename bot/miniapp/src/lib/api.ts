import { getInitData, getLinkToken } from "./telegram";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export type RedemptionStatus = "pending" | "fulfilled" | "cancelled";

export interface MiniAppMe {
  customer_id: number;
  telegram_id: number;
  full_name: string | null;
  balance: number;
  is_admin: boolean;
}

export interface Product {
  id: number;
  name: string;
  category: string;
  icon_or_image_url: string | null;
  points_cost: number;
  active: boolean;
  created_at: string;
}

export interface Redemption {
  id: number;
  customer_id: number;
  product_id: number;
  product_name: string;
  product_category: string;
  product_icon_or_image_url: string | null;
  qty: number;
  points_spent: number;
  status: RedemptionStatus;
  confirmed_by: number | null;
  created_at: string;
  confirmed_at: string | null;
}

export interface RedemptionCreateResponse {
  items: Redemption[];
  total_points: number;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const initData = getInitData();
  if (initData) headers.set("X-Telegram-Init-Data", initData);
  const linkToken = getLinkToken();
  if (linkToken) headers.set("X-Link-Token", linkToken);
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  if (!response.ok) {
    throw new ApiError(response.status, await response.text());
  }
  return response.json() as Promise<T>;
}

export function getMe() {
  return apiFetch<MiniAppMe>("/api/miniapp/me");
}

export function getProducts(category?: string) {
  const query = new URLSearchParams();
  if (category) query.set("category", category);
  const qs = query.toString();
  return apiFetch<Product[]>(`/api/miniapp/products${qs ? `?${qs}` : ""}`);
}

export function createRedemption(items: Array<{ product_id: number; qty: number }>) {
  return apiFetch<RedemptionCreateResponse>("/api/miniapp/redemptions", {
    method: "POST",
    body: JSON.stringify({ items }),
  });
}

export function getMyRedemptions() {
  return apiFetch<Redemption[]>("/api/miniapp/redemptions/me");
}

export function getAdminProducts() {
  return apiFetch<Product[]>("/api/admin/products");
}

export function createAdminProduct(payload: Omit<Product, "id" | "created_at">) {
  return apiFetch<Product>("/api/admin/products", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateAdminProduct(productId: number, payload: Partial<Omit<Product, "id" | "created_at">>) {
  return apiFetch<Product>(`/api/admin/products/${productId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function hideAdminProduct(productId: number) {
  return apiFetch<Product>(`/api/admin/products/${productId}`, { method: "DELETE" });
}

export function getAdminRedemptions(status?: RedemptionStatus) {
  const query = new URLSearchParams();
  if (status) query.set("status", status);
  const qs = query.toString();
  return apiFetch<Redemption[]>(`/api/admin/redemptions${qs ? `?${qs}` : ""}`);
}

export function confirmAdminRedemption(redemptionId: number) {
  return apiFetch<Redemption>(`/api/admin/redemptions/${redemptionId}/confirm`, { method: "POST" });
}

export function cancelAdminRedemption(redemptionId: number) {
  return apiFetch<Redemption>(`/api/admin/redemptions/${redemptionId}/cancel`, { method: "POST" });
}
