import { useEffect, useMemo, useState } from "react";

import { Badge } from "./components/ui/badge";
import miramaxLogo from "./assets/miramax-logo.jpg";
import { Product, getProducts } from "./lib/api";

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
  const [products, setProducts] = useState<Product[]>([]);
  const [category, setCategory] = useState("Barchasi");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadCustomerData() {
    const productsResult = await getProducts();
    setProducts(productsResult);
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
  const visibleProducts = category === "Barchasi" ? products : products.filter((product) => product.category === category);

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
              <p className="text-xs text-muted-foreground">Sovg'alar katalogi</p>
            </div>
          </div>
          <div className="rounded-lg border bg-card px-3 py-2 text-right">
            <p className="text-[11px] leading-none text-muted-foreground">Prizlar</p>
            <p className="text-base font-semibold">{products.length}</p>
          </div>
        </div>
      </header>

      <main className="flex-1 px-4 pb-6 pt-4">
        {error && <Alert text={error} tone="error" />}
        <Catalog
          products={visibleProducts}
          categories={categories}
          category={category}
          onCategoryChange={setCategory}
        />
      </main>
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
  onCategoryChange: (category: string) => void;
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
        {props.products.map((product) => (
          <article key={product.id} className="overflow-hidden rounded-lg border bg-card">
            <div className="flex aspect-square items-center justify-center overflow-hidden bg-secondary text-secondary-foreground">
              {productVisual(product)}
            </div>
            <div className="space-y-2 p-3">
              <Badge variant="secondary" className="mb-2">{product.category}</Badge>
              <h2 className="min-h-10 text-sm font-semibold leading-tight">{product.name}</h2>
              <p className="text-sm font-semibold text-primary">{formatPoints(product.points_cost)} ball</p>
            </div>
          </article>
        ))}
        {props.products.length === 0 && <p className="py-8 text-center text-sm text-muted-foreground">Bu kategoriyada mahsulot yo'q.</p>}
      </div>
    </section>
  );
}
