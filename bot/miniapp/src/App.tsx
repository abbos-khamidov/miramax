import { FormEvent, useEffect, useMemo, useState } from "react";
import { Check, Clock, Gift, History, Minus, Plus, Settings, ShoppingCart, Sparkles, X } from "lucide-react";

import { Badge } from "./components/ui/badge";
import { Button } from "./components/ui/button";
import miramaxLogo from "./assets/miramax-logo.jpg";
import {
  ApiError,
  Product,
  Redemption,
  RedemptionStatus,
  cancelAdminRedemption,
  confirmAdminRedemption,
  createAdminProduct,
  createRedemption,
  getAdminProducts,
  getAdminRedemptions,
  getMe,
  getMyRedemptions,
  getProducts,
  hideAdminProduct,
  updateAdminProduct,
} from "./lib/api";

type Tab = "new" | "catalog" | "cart" | "history" | "admin";
type Cart = Record<number, number>;

const NEW_ARRIVALS_LIMIT = 10;

function initialTab(): Tab {
  const requested = new URLSearchParams(window.location.search).get("tab");
  return requested === "new" ? "new" : "catalog";
}

const statusLabel: Record<RedemptionStatus, string> = {
  pending: "Kutilmoqda",
  fulfilled: "Berildi",
  cancelled: "Bekor qilindi",
};

const emptyProductForm = {
  name: "",
  category: "",
  icon_or_image_url: "",
  points_cost: 0,
  active: true,
};

function formatPoints(points: number) {
  return new Intl.NumberFormat("uz-UZ").format(points);
}

function productVisual(product: Product) {
  if (product.icon_or_image_url?.startsWith("http") || product.icon_or_image_url?.startsWith("/")) {
    return <img src={product.icon_or_image_url} alt="" className="h-full w-full object-cover" />;
  }
  return <span className="text-xl">{product.icon_or_image_url || "M"}</span>;
}

export default function App() {
  const [tab, setTab] = useState<Tab>(initialTab);
  const [me, setMe] = useState<{ balance: number; full_name: string | null; is_admin: boolean } | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [history, setHistory] = useState<Redemption[]>([]);
  const [cart, setCart] = useState<Cart>({});
  const [category, setCategory] = useState("Barchasi");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function loadCustomerData() {
    const productsResult = await getProducts();
    setProducts(productsResult);

    try {
      const [meResult, historyResult] = await Promise.all([getMe(), getMyRedemptions()]);
      setMe(meResult);
      setHistory(historyResult);
    } catch (err) {
      setMe(null);
      setHistory([]);
      if (!(err instanceof ApiError) || (err.status !== 401 && err.status !== 403)) {
        throw err;
      }
    }
  }

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    loadCustomerData()
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Ma'lumot yuklanmadi");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const categories = useMemo(
    () => ["Barchasi", ...Array.from(new Set(products.map((product) => product.category)))],
    [products],
  );
  const newArrivals = useMemo(
    () =>
      [...products]
        .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        .slice(0, NEW_ARRIVALS_LIMIT),
    [products],
  );
  const visibleProducts = category === "Barchasi" ? products : products.filter((product) => product.category === category);
  const cartItems = Object.entries(cart)
    .map(([productId, qty]) => {
      const product = products.find((item) => item.id === Number(productId));
      return product ? { product, qty } : null;
    })
    .filter(Boolean) as Array<{ product: Product; qty: number }>;
  const cartTotal = cartItems.reduce((sum, item) => sum + item.product.points_cost * item.qty, 0);
  const canRedeem = cartItems.length > 0 && me !== null && cartTotal <= me.balance;

  function addToCart(productId: number) {
    setCart((current) => ({ ...current, [productId]: (current[productId] ?? 0) + 1 }));
  }

  function removeFromCart(productId: number) {
    setCart((current) => {
      const nextQty = (current[productId] ?? 0) - 1;
      const next = { ...current };
      if (nextQty > 0) next[productId] = nextQty;
      else delete next[productId];
      return next;
    });
  }

  async function submitRedemption() {
    if (!canRedeem) return;
    setError(null);
    setNotice(null);
    await createRedemption(cartItems.map((item) => ({ product_id: item.product.id, qty: item.qty })));
    setCart({});
    setNotice("So'rov yuborildi. Mahsulot berilganda admin tasdiqlaydi.");
    await loadCustomerData();
    setTab("history");
  }

  if (loading) {
    return <Shell message="Yuklanmoqda..." />;
  }

  return (
    <div className="mx-auto flex min-h-full max-w-[480px] flex-col bg-background text-foreground">
      <header className="sticky top-0 z-10 border-b bg-background/95 px-4 pb-3 pt-4 backdrop-blur">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <img src={miramaxLogo} alt="Miramax" className="h-10 w-10 rounded-lg object-cover" />
            <div>
              <h1 className="text-lg font-semibold leading-tight">Miramax Bonus</h1>
              <p className="text-xs text-muted-foreground">{me?.full_name ?? "Sovg'alar katalogi"}</p>
            </div>
          </div>
          {me ? <div className="rounded-lg bg-primary px-3 py-2 text-right text-primary-foreground">
            <p className="text-[11px] leading-none opacity-80">Balans</p>
            <p className="text-base font-semibold">{formatPoints(me.balance)}</p>
          </div> : <div className="rounded-lg border bg-card px-3 py-2 text-right">
            <p className="text-[11px] leading-none text-muted-foreground">Prizlar</p>
            <p className="text-base font-semibold">{products.length}</p>
          </div>}
        </div>
      </header>

      <main className="flex-1 px-4 pb-24 pt-4">
        {error && <Alert text={error} tone="error" />}
        {notice && <Alert text={notice} tone="ok" />}
        {!me && <Alert text="Ballarni almashtirish uchun bot yuborgan shaxsiy havola orqali kiring." tone="ok" />}
        {tab === "new" && <NewArrivals products={newArrivals} cart={cart} canRedeem={me !== null} onAdd={addToCart} onRemove={removeFromCart} />}
        {tab === "catalog" && (
          <Catalog
            products={visibleProducts}
            categories={categories}
            category={category}
            cart={cart}
            canRedeem={me !== null}
            onCategoryChange={setCategory}
            onAdd={addToCart}
            onRemove={removeFromCart}
          />
        )}
        {tab === "cart" && (
          <CartView
            items={cartItems}
            total={cartTotal}
            balance={me?.balance ?? 0}
            canRedeem={canRedeem}
            onAdd={addToCart}
            onRemove={removeFromCart}
            onSubmit={submitRedemption}
          />
        )}
        {tab === "history" && <HistoryView items={history} />}
        {tab === "admin" && me?.is_admin && <AdminView onCustomerRefresh={loadCustomerData} />}
      </main>

      <nav className="fixed inset-x-0 bottom-0 z-20 mx-auto max-w-[480px] border-t bg-card px-3 py-2">
        <div className={me?.is_admin ? "grid grid-cols-5 gap-2" : "grid grid-cols-4 gap-2"}>
          <NavButton active={tab === "new"} icon={<Sparkles />} label="Yangiliklar" onClick={() => setTab("new")} />
          <NavButton active={tab === "catalog"} icon={<Gift />} label="Sovg'alar" onClick={() => setTab("catalog")} />
          {me && <NavButton active={tab === "cart"} icon={<ShoppingCart />} label={`Savatcha${cartItems.length ? ` (${cartItems.length})` : ""}`} onClick={() => setTab("cart")} />}
          {me && <NavButton active={tab === "history"} icon={<History />} label="Tarix" onClick={() => setTab("history")} />}
          {me?.is_admin && (
            <NavButton active={tab === "admin"} icon={<Settings />} label="Admin" onClick={() => setTab("admin")} />
          )}
        </div>
      </nav>
    </div>
  );
}

function Shell({ message }: { message: string }) {
  return (
    <div className="mx-auto flex min-h-full max-w-[480px] items-center justify-center bg-background p-6 text-sm text-muted-foreground">
      {message}
    </div>
  );
}

function Alert({ text, tone }: { text: string; tone: "error" | "ok" }) {
  return (
    <div className={tone === "error" ? "mb-3 rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive" : "mb-3 rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3 text-sm text-emerald-700"}>
      {text}
    </div>
  );
}

function Catalog(props: {
  products: Product[];
  categories: string[];
  category: string;
  cart: Cart;
  canRedeem: boolean;
  onCategoryChange: (category: string) => void;
  onAdd: (productId: number) => void;
  onRemove: (productId: number) => void;
}) {
  return (
    <section className="space-y-4">
      <div className="flex gap-2 overflow-x-auto pb-1">
        {props.categories.map((item) => (
          <button
            key={item}
            className={item === props.category ? "rounded-lg bg-primary px-3 py-2 text-sm text-primary-foreground" : "rounded-lg border bg-card px-3 py-2 text-sm"}
            onClick={() => props.onCategoryChange(item)}
          >
            {item}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-3">
        {props.products.map((product) => {
          const qty = props.cart[product.id] ?? 0;
          return (
            <article key={product.id} className="overflow-hidden rounded-lg border bg-card">
              <div className="flex aspect-square items-center justify-center overflow-hidden bg-secondary text-secondary-foreground">
                {productVisual(product)}
              </div>
              <div className="space-y-2 p-3">
                <Badge variant="secondary" className="mb-2">{product.category}</Badge>
                <h2 className="min-h-10 text-sm font-semibold leading-tight">{product.name}</h2>
                <p className="text-sm font-semibold text-primary">{formatPoints(product.points_cost)} ball</p>
                {props.canRedeem && <Stepper qty={qty} onAdd={() => props.onAdd(product.id)} onRemove={() => props.onRemove(product.id)} />}
              </div>
            </article>
          );
        })}
        {props.products.length === 0 && <p className="py-8 text-center text-sm text-muted-foreground">Bu kategoriyada mahsulot yo'q.</p>}
      </div>
    </section>
  );
}

function NewArrivals(props: {
  products: Product[];
  cart: Cart;
  canRedeem: boolean;
  onAdd: (productId: number) => void;
  onRemove: (productId: number) => void;
}) {
  return (
    <section className="space-y-4">
      <p className="text-sm text-muted-foreground">So'nggi qo'shilgan sovg'alar.</p>
      <div className="grid grid-cols-2 gap-3">
        {props.products.map((product) => {
          const qty = props.cart[product.id] ?? 0;
          return (
            <article key={product.id} className="overflow-hidden rounded-lg border bg-card">
              <div className="flex aspect-square items-center justify-center overflow-hidden bg-secondary text-secondary-foreground">
                {productVisual(product)}
              </div>
              <div className="space-y-2 p-3">
                <Badge variant="secondary" className="mb-2">Yangi</Badge>
                <h2 className="min-h-10 text-sm font-semibold leading-tight">{product.name}</h2>
                <p className="text-sm font-semibold text-primary">{formatPoints(product.points_cost)} ball</p>
                {props.canRedeem && <Stepper qty={qty} onAdd={() => props.onAdd(product.id)} onRemove={() => props.onRemove(product.id)} />}
              </div>
            </article>
          );
        })}
        {props.products.length === 0 && <p className="py-8 text-center text-sm text-muted-foreground">Hozircha yangiliklar yo'q.</p>}
      </div>
    </section>
  );
}

function CartView(props: {
  items: Array<{ product: Product; qty: number }>;
  total: number;
  balance: number;
  canRedeem: boolean;
  onAdd: (productId: number) => void;
  onRemove: (productId: number) => void;
  onSubmit: () => void;
}) {
  const overLimit = props.total > props.balance;
  return (
    <section className="space-y-4">
      {props.items.length === 0 ? (
        <p className="py-10 text-center text-sm text-muted-foreground">Savatcha bo'sh.</p>
      ) : (
        props.items.map(({ product, qty }) => (
          <div key={product.id} className="flex items-center justify-between gap-3 border-b py-3">
            <div>
              <h2 className="text-base font-semibold">{product.name}</h2>
              <p className="text-sm text-muted-foreground">{qty} x {formatPoints(product.points_cost)} ball</p>
            </div>
            <Stepper qty={qty} onAdd={() => props.onAdd(product.id)} onRemove={() => props.onRemove(product.id)} />
          </div>
        ))
      )}
      <div className="rounded-lg border bg-card p-4">
        <div className="flex justify-between text-sm">
          <span>Jami</span>
          <strong>{formatPoints(props.total)} ball</strong>
        </div>
        <div className="mt-1 flex justify-between text-sm text-muted-foreground">
          <span>Balans</span>
          <span>{formatPoints(props.balance)} ball</span>
        </div>
        {overLimit && <p className="mt-3 text-sm text-destructive">Ball yetarli emas.</p>}
        <Button className="mt-4 w-full" disabled={!props.canRedeem} onClick={props.onSubmit}>
          Ballarni almashtirish
        </Button>
      </div>
    </section>
  );
}

function HistoryView({ items }: { items: Redemption[] }) {
  return (
    <section className="space-y-3">
      {items.length === 0 && <p className="py-10 text-center text-sm text-muted-foreground">Almashtirishlar hali yo'q.</p>}
      {items.map((item) => (
        <article key={item.id} className="rounded-lg border bg-card p-3">
          <div className="flex items-start justify-between gap-3">
            <div>
              <h2 className="text-base font-semibold">{item.product_name}</h2>
              <p className="text-sm text-muted-foreground">{item.qty} dona, {formatPoints(item.points_spent)} ball</p>
            </div>
            <StatusBadge status={item.status} />
          </div>
          <p className="mt-2 text-xs text-muted-foreground">{new Date(item.created_at).toLocaleString("uz-UZ")}</p>
        </article>
      ))}
    </section>
  );
}

function AdminView({ onCustomerRefresh }: { onCustomerRefresh: () => Promise<void> }) {
  const [products, setProducts] = useState<Product[]>([]);
  const [redemptions, setRedemptions] = useState<Redemption[]>([]);
  const [status, setStatus] = useState<RedemptionStatus>("pending");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState(emptyProductForm);
  const [error, setError] = useState<string | null>(null);

  async function loadAdmin() {
    const [adminProducts, adminRedemptions] = await Promise.all([getAdminProducts(), getAdminRedemptions(status)]);
    setProducts(adminProducts);
    setRedemptions(adminRedemptions);
  }

  useEffect(() => {
    loadAdmin().catch((err) => setError(err instanceof Error ? err.message : "Admin ma'lumotlari yuklanmadi"));
  }, [status]);

  async function submitProduct(event: FormEvent) {
    event.preventDefault();
    setError(null);
    const payload = { ...form, points_cost: Number(form.points_cost), icon_or_image_url: form.icon_or_image_url || null };
    if (editingId) await updateAdminProduct(editingId, payload);
    else await createAdminProduct(payload);
    setEditingId(null);
    setForm(emptyProductForm);
    await loadAdmin();
    await onCustomerRefresh();
  }

  function editProduct(product: Product) {
    setEditingId(product.id);
    setForm({
      name: product.name,
      category: product.category,
      icon_or_image_url: product.icon_or_image_url ?? "",
      points_cost: product.points_cost,
      active: product.active,
    });
  }

  async function confirm(id: number) {
    await confirmAdminRedemption(id);
    await loadAdmin();
    await onCustomerRefresh();
  }

  async function cancel(id: number) {
    await cancelAdminRedemption(id);
    await loadAdmin();
  }

  return (
    <section className="space-y-6">
      {error && <Alert text={error} tone="error" />}
      <form className="space-y-3 rounded-lg border bg-card p-4" onSubmit={submitProduct}>
        <h2 className="text-base font-semibold">{editingId ? "Mahsulotni tahrirlash" : "Yangi mahsulot"}</h2>
        <Input label="Nomi" value={form.name} onChange={(value) => setForm({ ...form, name: value })} />
        <Input label="Kategoriya" value={form.category} onChange={(value) => setForm({ ...form, category: value })} />
        <Input label="Rasm yoki belgi" value={form.icon_or_image_url} onChange={(value) => setForm({ ...form, icon_or_image_url: value })} />
        <Input label="Ball narxi" type="number" value={String(form.points_cost)} onChange={(value) => setForm({ ...form, points_cost: Number(value) })} />
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={form.active} onChange={(event) => setForm({ ...form, active: event.target.checked })} />
          Katalogda ko'rinsin
        </label>
        <div className="flex gap-2">
          <Button type="submit" className="flex-1">{editingId ? "Saqlash" : "Qo'shish"}</Button>
          {editingId && <Button type="button" variant="outline" onClick={() => { setEditingId(null); setForm(emptyProductForm); }}>Bekor qilish</Button>}
        </div>
      </form>

      <div className="space-y-3">
        <h2 className="text-base font-semibold">Mahsulotlar</h2>
        {products.map((product) => (
          <div key={product.id} className="rounded-lg border bg-card p-3">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="font-semibold">{product.name}</p>
                <p className="text-sm text-muted-foreground">{product.category} · {formatPoints(product.points_cost)} ball</p>
              </div>
              <Badge variant={product.active ? "secondary" : "outline"}>{product.active ? "Faol" : "Yashirilgan"}</Badge>
            </div>
            <div className="mt-3 flex gap-2">
              <Button size="sm" variant="outline" onClick={() => editProduct(product)}>Tahrirlash</Button>
              {product.active && <Button size="sm" variant="destructive" onClick={() => hideAdminProduct(product.id).then(loadAdmin)}>Yashirish</Button>}
            </div>
          </div>
        ))}
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-base font-semibold">Almashtirish so'rovlari</h2>
          <select className="rounded-md border bg-background px-2 py-1 text-sm" value={status} onChange={(event) => setStatus(event.target.value as RedemptionStatus)}>
            <option value="pending">Kutilmoqda</option>
            <option value="fulfilled">Berildi</option>
            <option value="cancelled">Bekor qilindi</option>
          </select>
        </div>
        {redemptions.length === 0 && <p className="text-sm text-muted-foreground">So'rovlar yo'q.</p>}
        {redemptions.map((item) => (
          <div key={item.id} className="rounded-lg border bg-card p-3">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-semibold">{item.product_name}</p>
                <p className="text-sm text-muted-foreground">Mijoz #{item.customer_id}, {item.qty} dona, {formatPoints(item.points_spent)} ball</p>
              </div>
              <StatusBadge status={item.status} />
            </div>
            {item.status === "pending" && (
              <div className="mt-3 flex gap-2">
                <Button size="sm" onClick={() => confirm(item.id)}><Check /> Tasdiqlash</Button>
                <Button size="sm" variant="outline" onClick={() => cancel(item.id)}><X /> Bekor qilish</Button>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

function Input(props: { label: string; value: string; type?: string; onChange: (value: string) => void }) {
  return (
    <label className="block text-sm">
      <span className="mb-1 block text-muted-foreground">{props.label}</span>
      <input
        className="h-10 w-full rounded-md border bg-background px-3 text-sm"
        required={props.label !== "Rasm yoki belgi"}
        type={props.type ?? "text"}
        value={props.value}
        onChange={(event) => props.onChange(event.target.value)}
      />
    </label>
  );
}

function Stepper({ qty, onAdd, onRemove }: { qty: number; onAdd: () => void; onRemove: () => void }) {
  if (qty === 0) {
    return <Button size="icon" aria-label="Qo'shish" onClick={onAdd}><Plus /></Button>;
  }
  return (
    <div className="flex h-9 items-center gap-1 rounded-md border bg-background px-1">
      <button className="flex h-7 w-7 items-center justify-center rounded-md" aria-label="Kamaytirish" onClick={onRemove}><Minus className="h-4 w-4" /></button>
      <span className="w-6 text-center text-sm font-semibold">{qty}</span>
      <button className="flex h-7 w-7 items-center justify-center rounded-md" aria-label="Qo'shish" onClick={onAdd}><Plus className="h-4 w-4" /></button>
    </div>
  );
}

function StatusBadge({ status }: { status: RedemptionStatus }) {
  if (status === "fulfilled") return <Badge><Check /> {statusLabel[status]}</Badge>;
  if (status === "cancelled") return <Badge variant="outline"><X /> {statusLabel[status]}</Badge>;
  return <Badge variant="secondary"><Clock /> {statusLabel[status]}</Badge>;
}

function NavButton(props: { active: boolean; icon: JSX.Element; label: string; onClick: () => void }) {
  return (
    <button
      className={props.active ? "flex h-12 flex-col items-center justify-center gap-1 rounded-lg bg-primary text-[11px] text-primary-foreground" : "flex h-12 flex-col items-center justify-center gap-1 rounded-lg text-[11px] text-muted-foreground"}
      onClick={props.onClick}
    >
      <span className="[&_svg]:h-4 [&_svg]:w-4">{props.icon}</span>
      <span className="max-w-full truncate px-1">{props.label}</span>
    </button>
  );
}
