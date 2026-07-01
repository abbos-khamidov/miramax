import { useState, useEffect, useRef } from "react";
import {
  Home, Gift, Tag, Clock, User, LayoutDashboard, ShoppingBag,
  Users, Star, Megaphone, ChevronRight, Search, Plus, Check,
  Award, Zap, Coffee, Package, Battery, CreditCard, Bell,
  Phone, Calendar, DollarSign, BarChart2, ArrowLeft, Edit2,
  Flame, Crown, Trophy, Percent, Target, Activity,
  Lock, Scan, Filter, TrendingUp, Heart, Wallet, Layers,
  ToggleLeft, RefreshCw, X, ChevronUp, ChevronDown, Settings,
  Mail, MapPin, ShieldCheck, HelpCircle, LogOut,
} from "lucide-react";
import {
  AreaChart, Area, LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, BarChart, Bar,
} from "recharts";
import miramaxLogo from "../assets/miramax-logo.jpg";

/* ─────────────────────────────────────────────────────────────
   GLOBAL ANIMATIONS
───────────────────────────────────────────────────────────── */
const GLOBAL_CSS = `
  @keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes shimmer {
    0%   { background-position: -200% 0; }
    100% { background-position:  200% 0; }
  }
  @keyframes scalePop {
    0%   { transform: scale(0.8); opacity: 0; }
    70%  { transform: scale(1.05); }
    100% { transform: scale(1); opacity: 1; }
  }
  @keyframes pulse-ring {
    0%   { box-shadow: 0 0 0 0 rgba(37,99,235,0.35); }
    70%  { box-shadow: 0 0 0 12px rgba(37,99,235,0); }
    100% { box-shadow: 0 0 0 0 rgba(37,99,235,0); }
  }
  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50%       { transform: translateY(-6px); }
  }
  @keyframes slideInUp {
    from { opacity: 0; transform: translateY(40px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes countUp {
    from { opacity: 0; transform: translateY(8px) scale(0.9); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
  }
  .anim-fadeSlideUp { animation: fadeSlideUp 0.5s ease both; }
  .anim-scalePop    { animation: scalePop 0.4s cubic-bezier(.34,1.56,.64,1) both; }
  .anim-float       { animation: float 3s ease-in-out infinite; }
  .anim-slideInUp   { animation: slideInUp 0.5s cubic-bezier(.16,1,.3,1) both; }
  .skeleton {
    background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
    background-size: 200% 100%;
    animation: shimmer 1.4s ease infinite;
    border-radius: 12px;
  }
  ::-webkit-scrollbar { display: none; }
  * { scrollbar-width: none; }
  .snap-x { scroll-snap-type: x mandatory; }
  .snap-start { scroll-snap-align: start; }
  .no-scroll { overflow: hidden !important; }
`;

/* ─────────────────────────────────────────────────────────────
   TYPES & DATA
───────────────────────────────────────────────────────────── */
type Role = "customer" | "admin" | null;
type CustomerTab = "home" | "rewards" | "discounts" | "history" | "profile";
type AdminTab = "dashboard" | "purchases" | "customers" | "rewards" | "promotions";

const IMG = (id: string, w: number, h: number) =>
  `https://images.unsplash.com/photo-${id}?w=${w}&h=${h}&fit=crop&auto=format`;

const salesData = [
  { day: "Mon", sales: 4200, customers: 32 },
  { day: "Tue", sales: 6800, customers: 51 },
  { day: "Wed", sales: 5300, customers: 44 },
  { day: "Thu", sales: 8900, customers: 68 },
  { day: "Fri", sales: 11000, customers: 89 },
  { day: "Sat", sales: 9500, customers: 77 },
  { day: "Sun", sales: 7400, customers: 58 },
];

const rewardsData = [
  {
    id: 1, name: "Signature krujka", category: "Turmush tarzi",
    points: 500, available: true, badge: "OMMABOP",
    img: IMG("1514228742587-6b1558fcca3d", 400, 300),
    badgeColor: "#ef4444", desc: "Premium keramika, 350 ml",
  },
  {
    id: 2, name: "Urban ryukzak", category: "Moda",
    points: 2500, available: true, badge: "YANGI",
    img: IMG("1547949003-9792a18a2601", 400, 300),
    badgeColor: "#2563eb", desc: "Suv o'tkazmaydi, 25 L",
  },
  {
    id: 3, name: "Power Bank Pro", category: "Texnika",
    points: 5000, available: true, badge: "CHEKLANGAN",
    img: IMG("1609592424950-a21d2d99daa2", 400, 300),
    badgeColor: "#f59e0b", desc: "20 000 mAh, tez quvvatlash",
  },
  {
    id: 4, name: "$50 sovg'a kartasi", category: "Sovg'a kartalari",
    points: 10000, available: false, badge: "EKSKLYUZIV",
    img: IMG("1556742049-0cfed4f6a45d", 400, 300),
    badgeColor: "#7c3aed", desc: "Barcha Miramax do'konlarida amal qiladi",
  },
];

const banners = [
  {
    id: 1,
    title: "Yozgi chegirma",
    sub: "30% gacha chegirma + bonus ballar",
    gradient: "linear-gradient(135deg, #1e3a8a 0%, #2563eb 60%, #3b82f6 100%)",
    img: IMG("1483985988355-763728e1935b", 240, 140),
  },
  {
    id: 2,
    title: "Ikki baravar ball",
    sub: "Faqat shu dam olish kunlari - 5-6 iyul",
    gradient: "linear-gradient(135deg, #78350f 0%, #d97706 60%, #f59e0b 100%)",
    img: IMG("1567966260330-295406f00384", 240, 140),
  },
  {
    id: 3,
    title: "Tug'ilgan kun bonusi",
    sub: "Siz uchun 500 bonus ball",
    gradient: "linear-gradient(135deg, #4c1d95 0%, #7c3aed 60%, #a78bfa 100%)",
    img: IMG("1567958451986-2de427a4a0be", 240, 140),
  },
];

const historyData = [
  { id: 1, date: "28-iyun, 2025", amount: 84.5,  pts: 85,  store: "Miramax Downtown", type: "purchase" },
  { id: 2, date: "21-iyun, 2025", amount: 132,   pts: 264, store: "Miramax Mall",     type: "double" },
  { id: 3, date: "14-iyun, 2025", amount: 47.2,  pts: 47,  store: "Miramax Central",  type: "purchase" },
  { id: 4, date: "7-iyun, 2025", amount: 210,   pts: 210, store: "Miramax Downtown", type: "purchase" },
  { id: 5, date: "30-may, 2025", amount: 63.8,  pts: 64,  store: "Miramax Mall",     type: "purchase" },
];

const adminCustomers = [
  { id: 1, name: "Sarah Johnson",  initials: "SJ", phone: "+1 555-234-5678", points: 3420,  total: "$1,240", level: "Gold",     since: "Jan 2024", purchases: 18 },
  { id: 2, name: "Marcus Chen",    initials: "MC", phone: "+1 555-876-5432", points: 1280,  total: "$580",   level: "Silver",   since: "Mar 2024", purchases: 5  },
  { id: 3, name: "Aisha Patel",    initials: "AP", phone: "+1 555-345-6789", points: 8750,  total: "$3,100", level: "Platinum", since: "Nov 2023", purchases: 34 },
  { id: 4, name: "James Rivera",   initials: "JR", phone: "+1 555-654-3210", points: 420,   total: "$180",   level: "Bronze",   since: "Jun 2025", purchases: 2  },
];

const LEVEL_COLORS: Record<string, { bg: string; text: string; glow: string }> = {
  Bronze:   { bg: "#fef3c7", text: "#92400e", glow: "#f59e0b" },
  Silver:   { bg: "#f1f5f9", text: "#475569", glow: "#94a3b8" },
  Gold:     { bg: "#fefce8", text: "#854d0e", glow: "#eab308" },
  Platinum: { bg: "#f5f3ff", text: "#5b21b6", glow: "#8b5cf6" },
};

const LEVEL_LABELS: Record<string, string> = {
  Bronze: "Bronza",
  Silver: "Kumush",
  Gold: "Oltin",
  Platinum: "Platina",
};

const AVATAR_GRADIENTS = [
  "linear-gradient(135deg,#1d4ed8,#2563eb)",
  "linear-gradient(135deg,#7c3aed,#a78bfa)",
  "linear-gradient(135deg,#065f46,#10b981)",
  "linear-gradient(135deg,#92400e,#f59e0b)",
];

/* ─────────────────────────────────────────────────────────────
   UTILITY HOOKS
───────────────────────────────────────────────────────────── */
function useCountdown(target: Date) {
  const [t, setT] = useState({ d: 0, h: 0, m: 0, s: 0 });
  useEffect(() => {
    const tick = () => {
      const diff = target.getTime() - Date.now();
      if (diff <= 0) { setT({ d: 0, h: 0, m: 0, s: 0 }); return; }
      setT({
        d: Math.floor(diff / 86400000),
        h: Math.floor((diff % 86400000) / 3600000),
        m: Math.floor((diff % 3600000) / 60000),
        s: Math.floor((diff % 60000) / 1000),
      });
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [target]);
  return t;
}

/* ─────────────────────────────────────────────────────────────
   SHARED COMPONENTS
───────────────────────────────────────────────────────────── */
function CircleProgress({
  value, max, size = 100, stroke = 9, color = "#2563eb", bg = "#e2e8f0",
}: { value: number; max: number; size?: number; stroke?: number; color?: string; bg?: string }) {
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const pct = Math.min(value / max, 1);
  return (
    <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={bg} strokeWidth={stroke} />
      <circle
        cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth={stroke}
        strokeLinecap="round"
        strokeDasharray={circ}
        strokeDashoffset={circ * (1 - pct)}
        style={{ transition: "stroke-dashoffset 1.2s cubic-bezier(.16,1,.3,1)" }}
      />
    </svg>
  );
}

function LevelBadge({ level, size = "sm" }: { level: string; size?: "sm" | "md" }) {
  const c = LEVEL_COLORS[level] ?? LEVEL_COLORS.Silver;
  const iconMap: Record<string, React.ReactNode> = {
    Bronze: <Award size={size === "md" ? 14 : 10} />,
    Silver: <Star size={size === "md" ? 14 : 10} />,
    Gold: <Crown size={size === "md" ? 14 : 10} />,
    Platinum: <Trophy size={size === "md" ? 14 : 10} />,
  };
  return (
    <span
      style={{
        display: "inline-flex", alignItems: "center", gap: 4,
        background: c.bg, color: c.text,
        padding: size === "md" ? "4px 10px" : "2px 7px",
        borderRadius: 99, fontSize: size === "md" ? 12 : 10,
        fontWeight: 700, letterSpacing: "0.02em",
        boxShadow: `0 0 0 1px ${c.glow}30`,
      }}
    >
      {iconMap[level]}
      {LEVEL_LABELS[level] ?? level}
    </span>
  );
}

function QRCodeSVG({ size = 128 }: { size?: number }) {
  const p = [
    [1,1,1,1,1,1,1,0,1,0,0,1,0,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,1,0,0,1,1,0,1,0,1,0,0,0,0,0,1],
    [1,0,1,1,1,0,1,0,1,0,1,1,0,0,1,0,1,1,1,0,1],
    [1,0,1,1,1,0,1,0,0,1,0,1,1,0,1,0,1,1,1,0,1],
    [1,0,1,1,1,0,1,0,1,1,0,0,1,0,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,1,0,0,0,1,1,0,0,1,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,0,1,0,1,0,1,0,1,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0,1,1,0,1,1,0,0,0,0,0,0,0,0],
    [1,1,0,1,1,0,1,1,0,1,0,1,1,1,1,0,1,0,1,1,0],
    [0,1,1,0,0,1,0,0,1,0,1,0,0,1,0,1,1,0,0,1,1],
    [1,0,1,0,1,1,1,1,0,1,1,0,1,0,1,1,0,1,0,1,0],
    [0,1,0,1,0,0,0,0,1,0,0,1,1,0,0,0,1,0,1,0,1],
    [1,1,1,0,1,0,1,0,0,1,0,1,0,1,1,0,0,1,1,0,1],
    [0,0,0,0,0,0,0,0,1,1,1,0,0,0,1,0,1,0,1,1,0],
    [1,1,1,1,1,1,1,0,1,0,1,1,0,1,1,0,0,1,0,1,1],
    [1,0,0,0,0,0,1,0,0,1,0,0,1,0,0,1,1,0,1,0,0],
    [1,0,1,1,1,0,1,0,1,0,1,1,0,1,1,1,0,0,1,1,0],
    [1,0,1,1,1,0,1,0,0,1,1,0,1,0,0,0,1,1,0,0,1],
    [1,0,1,1,1,0,1,0,1,0,0,1,0,1,1,0,0,1,1,0,0],
    [1,0,0,0,0,0,1,0,0,1,1,0,1,0,1,1,0,0,0,1,1],
    [1,1,1,1,1,1,1,0,1,1,0,1,0,0,1,0,1,0,0,0,1],
  ];
  const n = 21; const cell = size / n;
  return (
    <svg width={size} height={size} style={{ borderRadius: 8 }}>
      <rect width={size} height={size} fill="white" />
      {p.map((row, r) => row.map((c, col) => c ? (
        <rect key={`${r}-${col}`} x={col*cell} y={r*cell} width={cell} height={cell} fill="#0f172a" rx={cell*0.15} />
      ) : null))}
    </svg>
  );
}

function Skeleton({ h = 16, w = "100%", r = 12, className = "" }: { h?: number; w?: number | string; r?: number; className?: string }) {
  return <div className={`skeleton ${className}`} style={{ height: h, width: w, borderRadius: r }} />;
}

function CountdownUnit({ value, label }: { value: number; label: string }) {
  return (
    <div style={{ textAlign: "center", minWidth: 40 }}>
      <div style={{
        background: "rgba(0,0,0,0.5)", backdropFilter: "blur(8px)",
        borderRadius: 10, padding: "6px 10px",
        fontSize: 20, fontWeight: 800, color: "white", lineHeight: 1,
        fontVariantNumeric: "tabular-nums",
        fontFamily: "'Plus Jakarta Sans', sans-serif",
      }}>
        {String(value).padStart(2, "0")}
      </div>
      <div style={{ fontSize: 9, color: "rgba(255,255,255,0.6)", marginTop: 4, fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase" }}>
        {label}
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   BOTTOM NAVIGATION — Dark Floating Pill
───────────────────────────────────────────────────────────── */
function BottomNav<T extends string>({
  tabs, active, onSelect,
}: { tabs: { id: T; label: string; icon: React.ReactNode }[]; active: T; onSelect: (id: T) => void }) {
  return (
    <div style={{
      position: "fixed", bottom: 16, left: "50%", transform: "translateX(-50%)",
      width: "calc(100% - 32px)", maxWidth: 344,
      background: "rgba(10,16,32,0.92)", backdropFilter: "blur(24px)",
      WebkitBackdropFilter: "blur(24px)",
      borderRadius: 28, padding: "10px 8px",
      display: "flex", justifyContent: "space-around", alignItems: "center",
      border: "1px solid rgba(255,255,255,0.08)",
      boxShadow: "0 20px 60px rgba(0,0,0,0.5), 0 1px 0 rgba(255,255,255,0.06) inset",
      zIndex: 50,
    }}>
      {tabs.map((tab) => {
        const isActive = tab.id === active;
        return (
          <button
            key={tab.id}
            onClick={() => onSelect(tab.id)}
            style={{
              flex: 1, display: "flex", flexDirection: "column",
              alignItems: "center", gap: 4, padding: "6px 4px",
              borderRadius: 20, border: "none", background: "none",
              cursor: "pointer",
              color: isActive ? "#60a5fa" : "rgba(255,255,255,0.35)",
              transition: "all 0.2s ease",
              position: "relative",
            }}
          >
            {isActive && (
              <div style={{
                position: "absolute", top: 0, left: "10%", right: "10%", bottom: 0,
                background: "rgba(37,99,235,0.18)", borderRadius: 20,
              }} />
            )}
            <span style={{ position: "relative", transform: isActive ? "scale(1.1)" : "scale(1)", transition: "transform 0.2s" }}>
              {tab.icon}
            </span>
            <span style={{
              position: "relative", fontSize: 9, fontWeight: 700,
              letterSpacing: "0.05em", textTransform: "uppercase",
            }}>
              {tab.label}
            </span>
          </button>
        );
      })}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   CUSTOMER: HOME
───────────────────────────────────────────────────────────── */
function CustomerHome({ onViewRewards }: { onViewRewards: () => void }) {
  const [qrVisible, setQrVisible] = useState(false);
  const [loaded, setLoaded] = useState(false);
  useEffect(() => { setTimeout(() => setLoaded(true), 200); }, []);

  const userPts = 1280;
  const nextPts = 3000;
  const pct = Math.round((userPts / nextPts) * 100);

  return (
    <div style={{ background: "#F8FAFC", minHeight: "100%", paddingBottom: 100 }}>
      {/* HERO */}
      <div style={{
        background: "linear-gradient(160deg, #020617 0%, #0f172a 30%, #1e1b4b 65%, #1e3a8a 100%)",
        padding: "20px 20px 34px", position: "relative", overflow: "hidden",
      }}>
        {/* Mesh orbs */}
        <div style={{ position:"absolute",top:-40,right:-40,width:200,height:200,borderRadius:"50%",background:"radial-gradient(circle,rgba(37,99,235,0.3),transparent 70%)", pointerEvents:"none" }} />
        <div style={{ position:"absolute",bottom:-20,left:-30,width:180,height:180,borderRadius:"50%",background:"radial-gradient(circle,rgba(124,58,237,0.25),transparent 70%)", pointerEvents:"none" }} />
        <div style={{ position:"absolute",top:"40%",left:"40%",width:120,height:120,borderRadius:"50%",background:"radial-gradient(circle,rgba(16,185,129,0.15),transparent 70%)", pointerEvents:"none" }} />

        <div style={{ position:"relative", zIndex:1 }}>
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:24 }}>
            <div>
              <p style={{ color:"rgba(148,163,184,0.8)", fontSize:13, marginBottom:2 }}>Xayrli tong,</p>
              <h2 style={{ color:"white", fontSize:22, fontWeight:800, fontFamily:"'Plus Jakarta Sans',sans-serif", margin:0 }}>Marcus Chen 👋</h2>
            </div>
            <button
              onClick={() => setQrVisible(true)}
              style={{
                width:44,height:44,borderRadius:16,
                background:"rgba(255,255,255,0.1)",border:"1px solid rgba(255,255,255,0.15)",
                display:"flex",alignItems:"center",justifyContent:"center",
                backdropFilter:"blur(12px)",cursor:"pointer",position:"relative",
                animation:"pulse-ring 2s ease-out infinite",
              }}
            >
              <Scan size={20} color="white" />
              <span style={{
                position:"absolute",top:8,right:8,width:8,height:8,
                borderRadius:"50%",background:"#22c55e",
                boxShadow:"0 0 6px #22c55e",
              }} />
            </button>
          </div>
        </div>
      </div>

      {/* GLASS MEMBERSHIP CARD */}
      <div style={{ padding:"16px 16px 0", position:"relative", zIndex:2 }}>
        <div
          className="anim-slideInUp"
          style={{
            background: "linear-gradient(135deg, rgba(255,255,255,0.18) 0%, rgba(255,255,255,0.08) 100%)",
            backdropFilter:"blur(24px)", WebkitBackdropFilter:"blur(24px)",
            borderRadius:24, border:"1px solid rgba(255,255,255,0.22)",
            overflow:"hidden", position:"relative",
            boxShadow:"0 32px 64px rgba(0,0,0,0.35), 0 1px 0 rgba(255,255,255,0.2) inset",
          }}
        >
          {/* Card gradient background */}
          <div style={{
            position:"absolute",inset:0,
            background:"linear-gradient(135deg,#1e3a8a 0%,#1d4ed8 40%,#3b82f6 70%,#2563eb 100%)",
            opacity:0.85,
          }} />
          {/* Decorative circles */}
          <div style={{position:"absolute",top:-30,right:-30,width:160,height:160,borderRadius:"50%",background:"rgba(255,255,255,0.07)"}} />
          <div style={{position:"absolute",bottom:-40,left:-20,width:140,height:140,borderRadius:"50%",background:"rgba(255,255,255,0.05)"}} />

          <div style={{ position:"relative", padding:"20px 20px 16px" }}>
            <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", marginBottom:20 }}>
              <div>
                <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:4 }}>
                  <div style={{ width:82,height:34,borderRadius:10,background:"rgba(255,255,255,0.18)",display:"flex",alignItems:"center",justifyContent:"center",overflow:"hidden",border:"1px solid rgba(255,255,255,0.22)" }}>
                    <img src={miramaxLogo} alt="Miramax" style={{ width:"100%",height:"100%",objectFit:"cover" }} />
                  </div>
                </div>
                <LevelBadge level="Silver" size="md" />
              </div>
              <div style={{ textAlign:"right" }}>
                <p style={{ color:"rgba(255,255,255,0.6)", fontSize:11, marginBottom:2 }}>Karta raqami</p>
                <p style={{ color:"white", fontSize:13, fontWeight:700 }}>••• 4821</p>
              </div>
            </div>

            <div style={{ marginBottom:16 }}>
              <p style={{ color:"rgba(255,255,255,0.6)", fontSize:11, marginBottom:4 }}>Ballar balansi</p>
              <div style={{ display:"flex", alignItems:"flex-end", gap:6 }}>
                <span style={{ color:"white", fontSize:40, fontWeight:900, lineHeight:1, fontFamily:"'Plus Jakarta Sans',sans-serif" }}>
                  1,280
                </span>
                <span style={{ color:"rgba(255,255,255,0.6)", fontSize:14, marginBottom:4, fontWeight:600 }}>ball</span>
              </div>
            </div>

            <div style={{
              display:"flex", gap:16, paddingTop:12,
              borderTop:"1px solid rgba(255,255,255,0.12)",
            }}>
              {[
                { label:"Jami xarid", value:"$580.00" },
                { label:"A'zo bo'lgan", value:"Mar 2024" },
                { label:"Sovg'alar", value:"3 faol" },
              ].map((s) => (
                <div key={s.label}>
                  <p style={{ color:"rgba(255,255,255,0.5)", fontSize:10, marginBottom:2 }}>{s.label}</p>
                  <p style={{ color:"white", fontSize:12, fontWeight:700 }}>{s.value}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* LEVEL PROGRESS */}
      <div style={{ padding:"20px 16px 0" }} className="anim-fadeSlideUp">
        <div style={{
          background:"white", borderRadius:20,
          padding:16, boxShadow:"0 2px 16px rgba(0,0,0,0.06)",
          border:"1px solid rgba(0,0,0,0.05)",
        }}>
          <div style={{ display:"flex", alignItems:"center", gap:16 }}>
            <div style={{ position:"relative", flexShrink:0 }}>
              <CircleProgress value={userPts} max={nextPts} size={72} stroke={7} color="#2563eb" bg="#e0e7ff" />
              <div style={{
                position:"absolute", inset:0, display:"flex", flexDirection:"column",
                alignItems:"center", justifyContent:"center",
              }}>
                <span style={{ fontSize:14, fontWeight:900, color:"#1d4ed8", fontFamily:"'Plus Jakarta Sans',sans-serif" }}>{pct}%</span>
              </div>
            </div>
            <div style={{ flex:1 }}>
              <div style={{ display:"flex", justifyContent:"space-between", marginBottom:4 }}>
                <span style={{ fontSize:13, fontWeight:700, color:"#0f172a" }}>Oltin darajagacha</span>
                <span style={{ fontSize:11, color:"#64748b" }}>1 720 ball qoldi</span>
              </div>
              <div style={{ height:6, background:"#e0e7ff", borderRadius:99, overflow:"hidden" }}>
                <div style={{
                  height:"100%", width:`${pct}%`,
                  background:"linear-gradient(90deg,#2563eb,#60a5fa)",
                  borderRadius:99, transition:"width 1.2s cubic-bezier(.16,1,.3,1)",
                }} />
              </div>
              <div style={{ display:"flex", gap:8, marginTop:8 }}>
                {["Bronze","Silver","Gold","Platinum"].map((lv) => (
                  <div key={lv} style={{ display:"flex", flexDirection:"column", alignItems:"center", gap:3 }}>
                    <div style={{
                      width:6, height:6, borderRadius:"50%",
                      background: lv === "Silver" ? "#2563eb" : lv === "Bronze" ? "#22c55e" : "#d1d5db",
                    }} />
                    <span style={{ fontSize:8, color: lv === "Silver" ? "#2563eb" : "#94a3b8", fontWeight:700 }}>{lv.slice(0,2)}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* PROMOTIONS CAROUSEL */}
      <div style={{ padding:"20px 0 0" }}>
        <div style={{ padding:"0 16px", display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:12 }}>
          <h3 style={{ fontSize:16, fontWeight:800, color:"#0f172a", fontFamily:"'Plus Jakarta Sans',sans-serif", margin:0 }}>
            Maxsus takliflar
          </h3>
          <button style={{ fontSize:12, color:"#2563eb", fontWeight:700, background:"none", border:"none", cursor:"pointer" }}>
            Barchasi
          </button>
        </div>
        <div className="snap-x" style={{ display:"flex", gap:12, paddingLeft:16, paddingRight:16, overflowX:"auto" }}>
          {banners.map((b) => (
            <div
              key={b.id}
              className="snap-start"
              style={{
                minWidth:280, height:140, borderRadius:20, overflow:"hidden",
                position:"relative", flexShrink:0, cursor:"pointer",
                boxShadow:"0 8px 32px rgba(0,0,0,0.2)",
              }}
            >
              <div style={{ position:"absolute", inset:0, background:b.gradient }} />
              <img src={b.img} alt={b.title} style={{ position:"absolute",right:0,top:0,height:"100%",width:120,objectFit:"cover",opacity:0.35 }} />
              <div style={{ position:"absolute",inset:0,padding:"16px 18px",display:"flex",flexDirection:"column",justifyContent:"flex-end" }}>
                <p style={{ color:"rgba(255,255,255,0.7)", fontSize:10, fontWeight:700, letterSpacing:"0.1em", textTransform:"uppercase", marginBottom:4 }}>
                  Cheklangan taklif
                </p>
                <p style={{ color:"white", fontSize:18, fontWeight:900, fontFamily:"'Plus Jakarta Sans',sans-serif", marginBottom:2 }}>
                  {b.title}
                </p>
                <p style={{ color:"rgba(255,255,255,0.75)", fontSize:12, fontWeight:500 }}>{b.sub}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* QUICK STATS */}
      <div style={{ padding:"20px 16px 0" }}>
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:10 }}>
          {[
            { label:"Bu oy",icon:DollarSign,value:"$132",bg:"#eff6ff",icon_c:"#2563eb" },
            { label:"Ishlatilgan ball",icon:Gift,value:"500",bg:"#f5f3ff",icon_c:"#7c3aed" },
            { label:"Do'kon reytingi",icon:TrendingUp,value:"#147",bg:"#f0fdf4",icon_c:"#16a34a" },
          ].map((s) => (
            <div key={s.label} style={{
              background:"white",borderRadius:16,padding:"12px 10px",
              boxShadow:"0 2px 10px rgba(0,0,0,0.05)",border:"1px solid rgba(0,0,0,0.04)",
            }}>
              <div style={{ width:32,height:32,borderRadius:10,background:s.bg,display:"flex",alignItems:"center",justifyContent:"center",marginBottom:8 }}>
                <s.icon size={16} color={s.icon_c} />
              </div>
              <p style={{ fontSize:18,fontWeight:900,color:"#0f172a",fontFamily:"'Plus Jakarta Sans',sans-serif",margin:0 }}>{s.value}</p>
              <p style={{ fontSize:10,color:"#94a3b8",marginTop:2,fontWeight:600 }}>{s.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* PERSONALIZED RECOMMENDATIONS */}
      <div style={{ padding:"20px 16px 0" }}>
        <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:12 }}>
          <h3 style={{ fontSize:16,fontWeight:800,color:"#0f172a",fontFamily:"'Plus Jakarta Sans',sans-serif",margin:0 }}>Siz uchun</h3>
          <button onClick={onViewRewards} style={{ fontSize:12,color:"#2563eb",fontWeight:700,background:"none",border:"none",cursor:"pointer",display:"flex",alignItems:"center",gap:4 }}>
            Barcha sovg'alar <ChevronRight size={14} />
          </button>
        </div>
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:12 }}>
          {rewardsData.slice(0,2).map((r) => (
            <div key={r.id} style={{ background:"white",borderRadius:16,overflow:"hidden",boxShadow:"0 2px 12px rgba(0,0,0,0.07)",border:"1px solid rgba(0,0,0,0.04)" }}>
              <div style={{ height:90,background:"#f8fafc",position:"relative",overflow:"hidden" }}>
                <img src={r.img} alt={r.name} style={{ width:"100%",height:"100%",objectFit:"cover" }} />
                <div style={{ position:"absolute",top:8,left:8 }}>
                  <span style={{ background:r.badgeColor,color:"white",fontSize:8,fontWeight:800,padding:"2px 6px",borderRadius:99,letterSpacing:"0.05em" }}>
                    {r.badge}
                  </span>
                </div>
              </div>
              <div style={{ padding:"10px 10px 12px" }}>
                <p style={{ fontSize:12,fontWeight:700,color:"#0f172a",marginBottom:2 }}>{r.name}</p>
                <p style={{ fontSize:11,color:"#2563eb",fontWeight:800 }}>{r.points.toLocaleString()} ball</p>
                <button onClick={onViewRewards} style={{
                  marginTop:8,width:"100%",padding:"6px 0",borderRadius:10,
                  background:1280 >= r.points ? "#2563eb" : "#f1f5f9",
                  color:1280 >= r.points ? "white" : "#94a3b8",
                  fontSize:11,fontWeight:700,border:"none",cursor:"pointer",
                }}>
                  {1280 >= r.points ? "Olish" : "Yopiq"}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* RECENT ACTIVITY */}
      <div style={{ padding:"20px 16px 0" }}>
        <h3 style={{ fontSize:16,fontWeight:800,color:"#0f172a",fontFamily:"'Plus Jakarta Sans',sans-serif",margin:"0 0 12px" }}>So'nggi faollik</h3>
        <div style={{ background:"white",borderRadius:20,overflow:"hidden",boxShadow:"0 2px 16px rgba(0,0,0,0.06)",border:"1px solid rgba(0,0,0,0.04)" }}>
          {historyData.slice(0,3).map((h,i) => (
            <div key={h.id} style={{
              display:"flex",alignItems:"center",gap:12,padding:"14px 16px",
              borderBottom: i < 2 ? "1px solid #f1f5f9" : "none",
            }}>
              <div style={{ width:40,height:40,borderRadius:14,background:"#eff6ff",display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0 }}>
                <ShoppingBag size={18} color="#2563eb" />
              </div>
              <div style={{ flex:1,minWidth:0 }}>
                <p style={{ fontSize:13,fontWeight:700,color:"#0f172a",marginBottom:2,whiteSpace:"nowrap",overflow:"hidden",textOverflow:"ellipsis" }}>
                  {h.store}
                </p>
                <p style={{ fontSize:11,color:"#94a3b8" }}>{h.date}</p>
              </div>
              <div style={{ textAlign:"right",flexShrink:0 }}>
                <p style={{ fontSize:14,fontWeight:800,color:"#0f172a" }}>${h.amount}</p>
                <p style={{ fontSize:11,color:"#22c55e",fontWeight:700 }}>+{h.pts} ball</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* QR OVERLAY */}
      {qrVisible && (
        <div
          onClick={() => setQrVisible(false)}
          style={{
            position:"fixed",inset:0,background:"rgba(0,0,0,0.7)",backdropFilter:"blur(12px)",
            display:"flex",alignItems:"center",justifyContent:"center",zIndex:100,
          }}
        >
          <div className="anim-scalePop" onClick={(e) => e.stopPropagation()} style={{
            background:"white",borderRadius:28,padding:"28px 24px",textAlign:"center",
            boxShadow:"0 32px 80px rgba(0,0,0,0.4)", margin:"0 24px",
          }}>
            <div style={{ marginBottom:12 }}>
                <p style={{ fontSize:11,color:"#94a3b8",fontWeight:700,letterSpacing:"0.08em",textTransform:"uppercase",marginBottom:4 }}>
                A'zolik QR
              </p>
              <p style={{ fontSize:18,fontWeight:800,color:"#0f172a",fontFamily:"'Plus Jakarta Sans',sans-serif" }}>
                Marcus Chen
              </p>
            </div>
            <div style={{
              display:"inline-block",padding:16,borderRadius:20,
              background:"white",boxShadow:"0 0 0 1px rgba(0,0,0,0.08), 0 4px 24px rgba(0,0,0,0.1)",
            }}>
              <QRCodeSVG size={176} />
            </div>
            <div style={{ marginTop:16,display:"flex",justifyContent:"center",gap:8,flexWrap:"wrap" }}>
              <LevelBadge level="Silver" size="md" />
              <span style={{ display:"inline-flex",alignItems:"center",gap:4,background:"#f0fdf4",color:"#16a34a",padding:"4px 10px",borderRadius:99,fontSize:12,fontWeight:700 }}>
                <Star size={12} /> 1 280 ball
              </span>
            </div>
            <p style={{ fontSize:11,color:"#94a3b8",marginTop:12 }}>Karta raqami ••• 4821 · A'zo bo'lgan: Mar 2024</p>
            <button
              onClick={() => setQrVisible(false)}
              style={{ marginTop:16,padding:"10px 32px",background:"#0f172a",color:"white",borderRadius:14,border:"none",fontSize:14,fontWeight:700,cursor:"pointer",width:"100%" }}
            >
              Yopish
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   CUSTOMER: REWARDS
───────────────────────────────────────────────────────────── */
function CustomerRewards() {
  const [cat, setCat] = useState("Hammasi");
  const [redeemed, setRedeemed] = useState<number[]>([]);
  const cats = ["Hammasi","Turmush tarzi","Moda","Texnika","Sovg'a kartalari"];
  const userPts = 1280;

  const filtered = cat === "Hammasi" ? rewardsData : rewardsData.filter(r => r.category === cat);

  return (
    <div style={{ background:"#F8FAFC", minHeight:"100%", paddingBottom:100 }}>
      {/* Header */}
      <div style={{
        background:"linear-gradient(160deg,#1e3a8a,#2563eb)",
        padding:"20px 20px 32px",
      }}>
        <h2 style={{ color:"white",fontSize:22,fontWeight:900,fontFamily:"'Plus Jakarta Sans',sans-serif",margin:"0 0 4px" }}>
          Sovg'alar do'koni
        </h2>
        <p style={{ color:"rgba(255,255,255,0.7)",fontSize:13 }}>
          Balansingiz: <strong style={{ color:"white" }}>1 280 ball</strong>
        </p>
      </div>

      {/* Category pills */}
      <div style={{ paddingBottom:8,background:"white",borderRadius:"0 0 20px 20px",boxShadow:"0 4px 16px rgba(0,0,0,0.06)" }}>
        <div style={{ display:"flex",gap:8,padding:"12px 16px",overflowX:"auto" }}>
          {cats.map((c) => (
            <button
              key={c}
              onClick={() => setCat(c)}
              style={{
                padding:"7px 16px",borderRadius:99,border:"none",cursor:"pointer",
                whiteSpace:"nowrap",fontSize:13,fontWeight:700,
                background: cat === c ? "#2563eb" : "#f1f5f9",
                color: cat === c ? "white" : "#64748b",
                transition:"all 0.2s",
                boxShadow: cat === c ? "0 4px 12px rgba(37,99,235,0.35)" : "none",
              }}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      {/* Featured reward */}
      <div style={{ padding:"16px 16px 0" }}>
        <div style={{
          borderRadius:20,overflow:"hidden",position:"relative",height:160,
          boxShadow:"0 8px 32px rgba(37,99,235,0.25)",
        }}>
          <img src={IMG("1547949003-9792a18a2601",600,240)} alt="Tavsiya etilgan" style={{ width:"100%",height:"100%",objectFit:"cover" }} />
          <div style={{ position:"absolute",inset:0,background:"linear-gradient(90deg,rgba(0,0,0,0.75) 0%,rgba(0,0,0,0.15) 100%)" }} />
          <div style={{ position:"absolute",bottom:0,left:0,padding:"16px 18px" }}>
            <span style={{ background:"#f59e0b",color:"white",fontSize:9,fontWeight:800,padding:"2px 8px",borderRadius:99,letterSpacing:"0.1em",textTransform:"uppercase" }}>
              ★ TAVSIYA
            </span>
            <p style={{ color:"white",fontSize:18,fontWeight:900,fontFamily:"'Plus Jakarta Sans',sans-serif",margin:"6px 0 2px" }}>Urban ryukzak</p>
            <p style={{ color:"rgba(255,255,255,0.75)",fontSize:12 }}>Cheklangan miqdor · 2 500 ball</p>
          </div>
          <button style={{
            position:"absolute",right:14,bottom:14,padding:"8px 16px",
            background:"white",color:"#1d4ed8",borderRadius:12,border:"none",
            fontSize:12,fontWeight:800,cursor:"pointer",
            boxShadow:"0 4px 16px rgba(0,0,0,0.2)",
          }}>
            Olish
          </button>
        </div>
      </div>

      {/* Grid */}
      <div style={{ padding:"16px 16px 0", display:"grid", gridTemplateColumns:"1fr 1fr", gap:12 }}>
        {filtered.map((r) => {
          const done = redeemed.includes(r.id);
          const can = userPts >= r.points;
          const progress = Math.min((userPts / r.points) * 100, 100);
          return (
            <div key={r.id} style={{
              background:"white",borderRadius:20,overflow:"hidden",
              boxShadow:"0 2px 16px rgba(0,0,0,0.07)",border:"1px solid rgba(0,0,0,0.04)",
              transition:"transform 0.2s",
            }}>
              <div style={{ height:110,background:"#f8fafc",position:"relative",overflow:"hidden" }}>
                <img src={r.img} alt={r.name} style={{ width:"100%",height:"100%",objectFit:"cover",opacity:can?1:0.5 }} />
                {!can && (
                  <div style={{ position:"absolute",inset:0,display:"flex",alignItems:"center",justifyContent:"center",background:"rgba(0,0,0,0.35)",backdropFilter:"blur(2px)" }}>
                    <Lock size={20} color="white" />
                  </div>
                )}
                <div style={{ position:"absolute",top:8,left:8 }}>
                  <span style={{ background:r.badgeColor,color:"white",fontSize:8,fontWeight:800,padding:"2px 6px",borderRadius:99 }}>
                    {r.badge}
                  </span>
                </div>
                {done && (
                  <div style={{ position:"absolute",inset:0,background:"rgba(34,197,94,0.4)",display:"flex",alignItems:"center",justifyContent:"center" }}>
                    <div style={{ width:36,height:36,borderRadius:"50%",background:"#22c55e",display:"flex",alignItems:"center",justifyContent:"center" }}>
                      <Check size={18} color="white" />
                    </div>
                  </div>
                )}
              </div>
              <div style={{ padding:"12px 12px 14px" }}>
                <p style={{ fontSize:12,fontWeight:800,color:"#0f172a",marginBottom:1 }}>{r.name}</p>
                <p style={{ fontSize:10,color:"#94a3b8",marginBottom:8 }}>{r.desc}</p>
                {/* Progress bar */}
                <div style={{ marginBottom:8 }}>
                  <div style={{ height:3,background:"#f1f5f9",borderRadius:99,overflow:"hidden" }}>
                    <div style={{ height:"100%",width:`${progress}%`,background: can ? "#22c55e" : "#2563eb",borderRadius:99 }} />
                  </div>
                </div>
                <div style={{ display:"flex",alignItems:"center",justifyContent:"space-between",marginBottom:8 }}>
                  <span style={{ fontSize:13,fontWeight:900,color:"#1d4ed8",fontFamily:"'Plus Jakarta Sans',sans-serif" }}>
                    {r.points.toLocaleString()}
                    <span style={{ fontSize:9,fontWeight:700,color:"#94a3b8",marginLeft:2 }}>ball</span>
                  </span>
                  {!can && (
                    <span style={{ fontSize:9,color:"#94a3b8",fontWeight:600 }}>
                      yana +{(r.points - userPts).toLocaleString()}
                    </span>
                  )}
                </div>
                <button
                  onClick={() => can && !done && setRedeemed(p => [...p, r.id])}
                  disabled={!can || done}
                  style={{
                    width:"100%",padding:"8px 0",borderRadius:12,border:"none",cursor: can && !done ? "pointer":"default",
                    background: done ? "#f0fdf4" : can ? "#2563eb" : "#f1f5f9",
                    color: done ? "#16a34a" : can ? "white" : "#cbd5e1",
                    fontSize:12,fontWeight:800,transition:"all 0.2s",
                    boxShadow: can && !done ? "0 4px 12px rgba(37,99,235,0.3)" : "none",
                  }}
                >
                  {done ? "✓ Olindi" : can ? "Hozir olish" : "Yopiq"}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   CUSTOMER: OFFERS/DISCOUNTS
───────────────────────────────────────────────────────────── */
function DoublePointsTimer() {
  const target = new Date("2025-07-06T23:59:59");
  const t = useCountdown(target);
  return (
    <div style={{ display:"flex",gap:8,justifyContent:"center" }}>
      <CountdownUnit value={t.d} label="Kun" />
      <div style={{ color:"rgba(255,255,255,0.6)",fontSize:20,fontWeight:800,alignSelf:"flex-start",paddingTop:8 }}>:</div>
      <CountdownUnit value={t.h} label="Soat" />
      <div style={{ color:"rgba(255,255,255,0.6)",fontSize:20,fontWeight:800,alignSelf:"flex-start",paddingTop:8 }}>:</div>
      <CountdownUnit value={t.m} label="Daq" />
      <div style={{ color:"rgba(255,255,255,0.6)",fontSize:20,fontWeight:800,alignSelf:"flex-start",paddingTop:8 }}>:</div>
      <CountdownUnit value={t.s} label="Son" />
    </div>
  );
}

function CustomerOffers() {
  const offers = [
    { title:"Hammasiga 10% chegirma", desc:"Bu hafta istalgan Miramax do'konida foydalaning", expires:"8-iyul, 2025", icon:Percent, gradient:"linear-gradient(135deg,#1e3a8a,#2563eb)", cat:"Chegirma" },
    { title:"Happy Hour taklifi", desc:"Har kuni 14:00-17:00 oralig'ida qo'shimcha 5%", expires:"15-iyul, 2025", icon:Clock, gradient:"linear-gradient(135deg,#065f46,#10b981)", cat:"Tezkor" },
    { title:"Tug'ilgan kun sovg'asi", desc:"Tug'ilgan kun bonusi: 500 bepul ball", expires:"31-iyul, 2025", icon:Gift, gradient:"linear-gradient(135deg,#4c1d95,#7c3aed)", cat:"Shaxsiy" },
  ];

  return (
    <div style={{ background:"#F8FAFC", minHeight:"100%", paddingBottom:100 }}>
      {/* Header */}
      <div style={{
        background:"linear-gradient(160deg,#92400e,#d97706,#f59e0b)",
        padding:"20px 20px 32px", position:"relative",overflow:"hidden",
      }}>
        <div style={{ position:"absolute",top:-20,right:-20,width:120,height:120,borderRadius:"50%",background:"rgba(255,255,255,0.1)" }} />
        <h2 style={{ color:"white",fontSize:22,fontWeight:900,fontFamily:"'Plus Jakarta Sans',sans-serif",margin:"0 0 4px",position:"relative" }}>
          Maxsus takliflar
        </h2>
        <p style={{ color:"rgba(255,255,255,0.8)",fontSize:13,position:"relative" }}>Faqat siz uchun eksklyuziv takliflar</p>
      </div>

      {/* Double Points Countdown Banner */}
      <div style={{ padding:"16px 16px 0" }}>
        <div style={{
          background:"linear-gradient(135deg,#0c1445,#1d4ed8)",
          borderRadius:20,padding:"18px 16px",
          boxShadow:"0 8px 32px rgba(37,99,235,0.35)",
          position:"relative",overflow:"hidden",
        }}>
          <div style={{ position:"absolute",top:-20,right:-20,width:100,height:100,borderRadius:"50%",background:"rgba(255,255,255,0.05)" }} />
          <div style={{ display:"flex",alignItems:"center",gap:10,marginBottom:12 }}>
            <div style={{ width:36,height:36,borderRadius:12,background:"rgba(255,255,255,0.15)",display:"flex",alignItems:"center",justifyContent:"center" }}>
              <Zap size={18} color="#fbbf24" />
            </div>
            <div>
              <p style={{ color:"white",fontSize:15,fontWeight:800,fontFamily:"'Plus Jakarta Sans',sans-serif",margin:0 }}>Ikki baravar ball dam olish kunlari</p>
              <p style={{ color:"rgba(255,255,255,0.6)",fontSize:11,margin:0 }}>Har bir xariddan 2x ball oling</p>
            </div>
          </div>
          <DoublePointsTimer />
        </div>
      </div>

      {/* Seasonal Campaign */}
      <div style={{ padding:"16px 16px 0" }}>
        <div style={{
          borderRadius:20,overflow:"hidden",position:"relative",height:130,
          boxShadow:"0 8px 24px rgba(0,0,0,0.15)",
        }}>
          <img src={IMG("1483985988355-763728e1935b",600,200)} alt="Yoz" style={{ width:"100%",height:"100%",objectFit:"cover" }} />
          <div style={{ position:"absolute",inset:0,background:"linear-gradient(90deg,rgba(0,0,0,0.7),rgba(0,0,0,0.1))" }} />
          <div style={{ position:"absolute",inset:0,padding:"16px 18px",display:"flex",flexDirection:"column",justifyContent:"center" }}>
            <span style={{ background:"#f59e0b",color:"white",fontSize:9,fontWeight:800,padding:"2px 8px",borderRadius:99,width:"fit-content",letterSpacing:"0.1em" }}>MAVSUMIY</span>
            <p style={{ color:"white",fontSize:18,fontWeight:900,fontFamily:"'Plus Jakarta Sans',sans-serif",margin:"6px 0 2px" }}>Yozgi sovg'alar</p>
            <p style={{ color:"rgba(255,255,255,0.8)",fontSize:11 }}>Avgustgacha xarid qiling va ko'proq ball oling</p>
          </div>
        </div>
      </div>

      {/* Offer cards */}
      <div style={{ padding:"16px 16px 0", display:"flex", flexDirection:"column", gap:10 }}>
        {offers.map((o) => (
          <div key={o.title} style={{
            background:"white",borderRadius:20,overflow:"hidden",
            boxShadow:"0 2px 16px rgba(0,0,0,0.06)",border:"1px solid rgba(0,0,0,0.04)",
            display:"flex",
          }}>
            <div style={{ width:64,background:o.gradient,display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0 }}>
              <o.icon size={24} color="white" />
            </div>
            <div style={{ flex:1,padding:"14px 14px 14px 16px" }}>
              <div style={{ display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:4 }}>
                <p style={{ fontSize:14,fontWeight:800,color:"#0f172a",margin:0 }}>{o.title}</p>
                <span style={{ fontSize:9,background:"#f0fdf4",color:"#16a34a",padding:"2px 7px",borderRadius:99,fontWeight:700,flexShrink:0,marginLeft:8 }}>
                  {o.cat}
                </span>
              </div>
              <p style={{ fontSize:12,color:"#64748b",marginBottom:4 }}>{o.desc}</p>
              <p style={{ fontSize:10,color:"#94a3b8",fontWeight:600 }}>Tugash sanasi: {o.expires}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Notification nudge */}
      <div style={{ padding:"16px 16px 0" }}>
        <div style={{
          background:"linear-gradient(135deg,#eff6ff,#dbeafe)",
          borderRadius:20,padding:"14px 16px",border:"1px solid #bfdbfe",
          display:"flex",alignItems:"center",gap:12,
        }}>
          <div style={{ width:40,height:40,borderRadius:14,background:"#2563eb",display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0 }}>
            <Bell size={18} color="white" />
          </div>
          <div style={{ flex:1 }}>
            <p style={{ fontSize:13,fontWeight:800,color:"#1e40af",margin:0 }}>Takliflarni o'tkazib yubormang</p>
            <p style={{ fontSize:11,color:"#3b82f6",marginTop:2 }}>Takliflarni birinchi bo'lib olish uchun bildirishnomani yoqing</p>
          </div>
          <button style={{ padding:"6px 14px",background:"#2563eb",color:"white",borderRadius:12,border:"none",fontSize:12,fontWeight:700,cursor:"pointer",flexShrink:0 }}>
            Yoqish
          </button>
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   CUSTOMER: HISTORY
───────────────────────────────────────────────────────────── */
function CustomerHistory() {
  return (
    <div style={{ background:"#F8FAFC", minHeight:"100%", paddingBottom:100 }}>
      <div style={{ background:"linear-gradient(160deg,#0f172a,#1e293b)", padding:"20px 20px 32px" }}>
        <h2 style={{ color:"white",fontSize:22,fontWeight:900,fontFamily:"'Plus Jakarta Sans',sans-serif",margin:"0 0 4px" }}>Tarix</h2>
        <p style={{ color:"rgba(255,255,255,0.6)",fontSize:13 }}>
          Jami yig'ilgan: <strong style={{ color:"#22c55e" }}>1 280 ball</strong>
        </p>
      </div>

      {/* Monthly summary */}
      <div style={{ padding:"16px 16px 0" }}>
        <div style={{
          background:"white",borderRadius:20,padding:16,
          boxShadow:"0 4px 20px rgba(0,0,0,0.1)",border:"1px solid rgba(0,0,0,0.04)",
        }}>
          <p style={{ fontSize:11,fontWeight:700,color:"#94a3b8",textTransform:"uppercase",letterSpacing:"0.08em",marginBottom:12 }}>2025-yil iyun xulosasi</p>
          <div style={{ display:"grid",gridTemplateColumns:"1fr 1fr 1fr",gap:12 }}>
            {[
              { label:"Sarflandi",value:"$473.50",color:"#0f172a" },
              { label:"Yig'ildi",value:"738 ball",color:"#2563eb" },
              { label:"Tashrif",value:"4",color:"#16a34a" },
            ].map((s) => (
              <div key={s.label} style={{ textAlign:"center" }}>
                <p style={{ fontSize:18,fontWeight:900,color:s.color,fontFamily:"'Plus Jakarta Sans',sans-serif",margin:0 }}>{s.value}</p>
                <p style={{ fontSize:10,color:"#94a3b8",fontWeight:600,marginTop:2 }}>{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Transaction list */}
      <div style={{ padding:"16px 16px 0" }}>
        <p style={{ fontSize:12,fontWeight:700,color:"#94a3b8",textTransform:"uppercase",letterSpacing:"0.08em",marginBottom:10 }}>Tranzaksiyalar</p>
        <div style={{ background:"white",borderRadius:20,overflow:"hidden",boxShadow:"0 2px 16px rgba(0,0,0,0.06)",border:"1px solid rgba(0,0,0,0.04)" }}>
          {historyData.map((h,i) => (
            <div key={h.id} style={{
              display:"flex",alignItems:"center",gap:12,padding:"14px 16px",
              borderBottom: i < historyData.length-1 ? "1px solid #f1f5f9" : "none",
            }}>
              <div style={{
                width:44,height:44,borderRadius:16,flexShrink:0,overflow:"hidden",
                background: h.type === "double" ? "linear-gradient(135deg,#f59e0b,#d97706)" : "linear-gradient(135deg,#2563eb,#1d4ed8)",
                display:"flex",alignItems:"center",justifyContent:"center",
              }}>
                {h.type === "double" ? <Zap size={20} color="white" /> : <ShoppingBag size={20} color="white" />}
              </div>
              <div style={{ flex:1,minWidth:0 }}>
                <p style={{ fontSize:13,fontWeight:700,color:"#0f172a",whiteSpace:"nowrap",overflow:"hidden",textOverflow:"ellipsis" }}>
                  {h.store}
                </p>
                <div style={{ display:"flex",alignItems:"center",gap:6,marginTop:2 }}>
                  <Calendar size={10} color="#94a3b8" />
                  <p style={{ fontSize:11,color:"#94a3b8" }}>{h.date}</p>
                  {h.type === "double" && (
                    <span style={{ background:"#fef3c7",color:"#92400e",fontSize:8,fontWeight:800,padding:"1px 5px",borderRadius:99 }}>2× ball</span>
                  )}
                </div>
              </div>
              <div style={{ textAlign:"right",flexShrink:0 }}>
                <p style={{ fontSize:14,fontWeight:900,color:"#0f172a" }}>${h.amount}</p>
                <p style={{ fontSize:12,color:"#22c55e",fontWeight:800 }}>+{h.pts} ball</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   CUSTOMER: PROFILE
───────────────────────────────────────────────────────────── */
function CustomerProfile() {
  const nextTierPoints = 3000;
  const currentPoints = 1280;
  const progress = Math.round((currentPoints / nextTierPoints) * 100);
  const badges = [
    { id:"Bronze", earned:true, icon:Award, color:"#f59e0b", label:"Qo'shildi" },
    { id:"Silver", earned:true, icon:Star, color:"#94a3b8", label:"1K ball" },
    { id:"Gold", earned:false, icon:Crown, color:"#eab308", label:"3K ball" },
    { id:"Platinum", earned:false, icon:Trophy, color:"#8b5cf6", label:"10K ball" },
  ];
  return (
    <div style={{ background:"#F8FAFC", minHeight:"100%", paddingBottom:100 }}>
      {/* Hero */}
      <div style={{
        background:"linear-gradient(160deg,#1e1b4b,#2563eb)",
        padding:"20px 20px 34px",position:"relative",overflow:"hidden",
      }}>
        <div style={{ position:"absolute",bottom:-40,right:-40,width:180,height:180,borderRadius:"50%",background:"rgba(255,255,255,0.07)" }} />
        <div style={{ display:"flex",justifyContent:"flex-end",marginBottom:20 }}>
          <button style={{ width:36,height:36,borderRadius:12,background:"rgba(255,255,255,0.15)",border:"none",cursor:"pointer",display:"flex",alignItems:"center",justifyContent:"center" }}>
            <Settings size={18} color="white" />
          </button>
        </div>
        <div style={{ display:"flex",alignItems:"center",gap:16 }}>
          <div style={{
            width:64,height:64,borderRadius:22,
            background:"rgba(255,255,255,0.2)",backdropFilter:"blur(10px)",
            border:"2px solid rgba(255,255,255,0.3)",
            display:"flex",alignItems:"center",justifyContent:"center",
            fontSize:24,fontWeight:900,color:"white",
            fontFamily:"'Plus Jakarta Sans',sans-serif",
            flexShrink:0,
          }}>
            MC
          </div>
          <div>
            <h3 style={{ color:"white",fontSize:20,fontWeight:900,fontFamily:"'Plus Jakarta Sans',sans-serif",margin:"0 0 4px" }}>
              Marcus Chen
            </h3>
            <p style={{ color:"rgba(255,255,255,0.7)",fontSize:13,margin:0 }}>+1 (555) 876-5432</p>
            <div style={{ marginTop:8 }}>
              <LevelBadge level="Silver" size="md" />
            </div>
          </div>
        </div>
      </div>

      {/* Stats card overlapping hero */}
      <div style={{ padding:"16px 16px 0" }}>
        <div style={{
          background:"white",borderRadius:24,padding:16,
          boxShadow:"0 8px 32px rgba(0,0,0,0.12)",border:"1px solid rgba(0,0,0,0.04)",
        }}>
          <div style={{ display:"grid",gridTemplateColumns:"1fr 1fr 1fr 1fr",gap:8 }}>
            {[
              { label:"Ballar",value:"1,280",color:"#2563eb" },
              { label:"Sovg'alar",value:"3",color:"#7c3aed" },
              { label:"Xaridlar",value:"5",color:"#16a34a" },
              { label:"Reyting",value:"#147",color:"#f59e0b" },
            ].map((s) => (
              <div key={s.label} style={{ textAlign:"center" }}>
                <p style={{ fontSize:18,fontWeight:900,color:s.color,fontFamily:"'Plus Jakarta Sans',sans-serif",margin:0 }}>{s.value}</p>
                <p style={{ fontSize:9,color:"#94a3b8",fontWeight:700,textTransform:"uppercase",letterSpacing:"0.05em",marginTop:2 }}>{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Tier progress */}
      <div style={{ padding:"16px 16px 0" }}>
        <div style={{
          background:"linear-gradient(135deg,#0f172a,#1d4ed8)",
          borderRadius:22,padding:16,overflow:"hidden",position:"relative",
          boxShadow:"0 10px 30px rgba(37,99,235,0.22)",
        }}>
          <div style={{ position:"absolute",top:-46,right:-28,width:150,height:150,borderRadius:"50%",background:"rgba(255,255,255,0.08)" }} />
          <div style={{ display:"flex",justifyContent:"space-between",alignItems:"flex-start",gap:16,position:"relative" }}>
            <div>
              <p style={{ color:"rgba(255,255,255,0.58)",fontSize:11,fontWeight:800,textTransform:"uppercase",letterSpacing:"0.08em",margin:"0 0 4px" }}>
                Keyingi daraja
              </p>
              <p style={{ color:"white",fontSize:18,fontWeight:900,fontFamily:"'Plus Jakarta Sans',sans-serif",margin:0 }}>
                Oltin a'zo
              </p>
              <p style={{ color:"rgba(255,255,255,0.68)",fontSize:12,marginTop:4 }}>
                Premium takliflarni ochish uchun {nextTierPoints - currentPoints} ball qoldi
              </p>
            </div>
            <div style={{ position:"relative",width:74,height:74,flexShrink:0 }}>
              <CircleProgress value={currentPoints} max={nextTierPoints} size={74} stroke={7} color="#facc15" bg="rgba(255,255,255,0.2)" />
              <div style={{ position:"absolute",inset:0,display:"flex",alignItems:"center",justifyContent:"center",flexDirection:"column" }}>
                <span style={{ color:"white",fontSize:18,fontWeight:900,lineHeight:1 }}>{progress}%</span>
                <span style={{ color:"rgba(255,255,255,0.55)",fontSize:8,fontWeight:800,textTransform:"uppercase" }}>Bajarildi</span>
              </div>
            </div>
          </div>
          <div style={{ marginTop:14,height:8,borderRadius:999,background:"rgba(255,255,255,0.16)",overflow:"hidden",position:"relative" }}>
            <div style={{ width:`${progress}%`,height:"100%",background:"linear-gradient(90deg,#facc15,#f59e0b)",borderRadius:999 }} />
          </div>
          <div style={{ display:"flex",justifyContent:"space-between",marginTop:8,position:"relative" }}>
            <span style={{ color:"rgba(255,255,255,0.55)",fontSize:10,fontWeight:700 }}>Kumush</span>
            <span style={{ color:"rgba(255,255,255,0.75)",fontSize:10,fontWeight:800 }}>3 000 ball</span>
          </div>
        </div>
      </div>

      {/* Membership QR */}
      <div style={{ padding:"16px 16px 0" }}>
        <div style={{
          background:"white",borderRadius:22,padding:16,
          boxShadow:"0 2px 16px rgba(0,0,0,0.06)",border:"1px solid rgba(0,0,0,0.04)",
          display:"flex",gap:16,alignItems:"center",
        }}>
          <div style={{
            width:116,height:116,borderRadius:18,background:"#f8fafc",
            display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0,
            border:"1px solid #e2e8f0",
          }}>
            <QRCodeSVG size={92} />
          </div>
          <div style={{ flex:1,minWidth:0 }}>
            <p style={{ fontSize:11,fontWeight:800,color:"#94a3b8",textTransform:"uppercase",letterSpacing:"0.08em",margin:"0 0 5px" }}>
              A'zo ID
            </p>
            <p style={{ fontSize:18,fontWeight:900,color:"#0f172a",fontFamily:"'Plus Jakarta Sans',sans-serif",margin:"0 0 4px" }}>
              MRX-4286
            </p>
            <p style={{ fontSize:12,color:"#64748b",lineHeight:1.4,margin:"0 0 10px" }}>
              Ball yig'ish va faol sovg'alarni qo'llash uchun kassada skaner qiling.
            </p>
            <button style={{
              display:"inline-flex",alignItems:"center",gap:6,padding:"8px 12px",
              background:"#eff6ff",color:"#2563eb",border:"1px solid #bfdbfe",
              borderRadius:12,fontSize:12,fontWeight:800,cursor:"pointer",
            }}>
              <Scan size={14} />
              Kodni ko'rsatish
            </button>
          </div>
        </div>
      </div>

      {/* Achievement Badges */}
      <div style={{ padding:"16px 16px 0" }}>
        <p style={{ fontSize:14,fontWeight:800,color:"#0f172a",marginBottom:12,fontFamily:"'Plus Jakarta Sans',sans-serif" }}>
          Yutuqlar
        </p>
        <div style={{ display:"grid",gridTemplateColumns:"1fr 1fr 1fr 1fr",gap:10 }}>
          {badges.map((b) => (
            <div key={b.id} style={{
              background:b.earned ? "white" : "#f8fafc",
              borderRadius:16,padding:"12px 8px",textAlign:"center",
              boxShadow: b.earned ? "0 4px 16px rgba(0,0,0,0.08)" : "none",
              border: b.earned ? `1px solid ${b.color}30` : "1px solid rgba(0,0,0,0.04)",
              opacity: b.earned ? 1 : 0.5,
            }}>
              <div style={{
                width:40,height:40,borderRadius:14,
                background: b.earned ? `${b.color}15` : "#f1f5f9",
                display:"flex",alignItems:"center",justifyContent:"center",
                margin:"0 auto 8px",
              }}>
                <b.icon size={20} color={b.earned ? b.color : "#cbd5e1"} />
              </div>
              <p style={{ fontSize:11,fontWeight:800,color:b.earned ? "#0f172a" : "#94a3b8",margin:0 }}>{LEVEL_LABELS[b.id] ?? b.id}</p>
              <p style={{ fontSize:9,color:"#94a3b8",marginTop:2 }}>{b.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Personal details */}
      <div style={{ padding:"16px 16px 0" }}>
        <p style={{ fontSize:14,fontWeight:800,color:"#0f172a",marginBottom:12,fontFamily:"'Plus Jakarta Sans',sans-serif" }}>
          Shaxsiy ma'lumotlar
        </p>
        <div style={{
          background:"white",borderRadius:20,overflow:"hidden",
          boxShadow:"0 2px 16px rgba(0,0,0,0.06)",border:"1px solid rgba(0,0,0,0.04)",
        }}>
          {[
            { icon:Phone,label:"Telefon",value:"+1 (555) 876-5432",color:"#2563eb",bg:"#eff6ff" },
            { icon:Mail,label:"Email",value:"marcus.chen@example.com",color:"#7c3aed",bg:"#f5f3ff" },
            { icon:MapPin,label:"Sevimli do'kon",value:"Miramax Mall",color:"#16a34a",bg:"#f0fdf4" },
            { icon:Calendar,label:"A'zo bo'lgan",value:"Mar 2024",color:"#f59e0b",bg:"#fffbeb" },
          ].map((item, i, arr) => (
            <div key={item.label} style={{
              display:"flex",alignItems:"center",gap:12,padding:"13px 16px",
              borderBottom: i < arr.length - 1 ? "1px solid #f1f5f9" : "none",
            }}>
              <div style={{ width:34,height:34,borderRadius:12,background:item.bg,display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0 }}>
                <item.icon size={16} color={item.color} />
              </div>
              <div style={{ flex:1,minWidth:0 }}>
                <p style={{ fontSize:10,fontWeight:800,color:"#94a3b8",textTransform:"uppercase",letterSpacing:"0.06em",margin:"0 0 2px" }}>{item.label}</p>
                <p style={{ fontSize:13,fontWeight:700,color:"#0f172a",margin:0,whiteSpace:"nowrap",overflow:"hidden",textOverflow:"ellipsis" }}>{item.value}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Settings list */}
      <div style={{ padding:"16px 16px 0" }}>
        <div style={{ background:"white",borderRadius:20,overflow:"hidden",boxShadow:"0 2px 16px rgba(0,0,0,0.06)",border:"1px solid rgba(0,0,0,0.04)" }}>
          {[
            { icon:User,label:"Shaxsiy ma'lumot",color:"#2563eb",bg:"#eff6ff" },
            { icon:Bell,label:"Bildirishnomalar",color:"#7c3aed",bg:"#f5f3ff" },
            { icon:Wallet,label:"To'lov usullari",color:"#16a34a",bg:"#f0fdf4" },
            { icon:Scan,label:"Mening QR kodim",color:"#0891b2",bg:"#ecfeff" },
            { icon:ShieldCheck,label:"Maxfiylik va xavfsizlik",color:"#0f766e",bg:"#f0fdfa" },
            { icon:HelpCircle,label:"Yordam markazi",color:"#64748b",bg:"#f8fafc" },
            { icon:Settings,label:"Ilova sozlamalari",color:"#64748b",bg:"#f8fafc" },
          ].map((item, i, arr) => (
            <button
              key={item.label}
              style={{
                width:"100%",display:"flex",alignItems:"center",gap:14,padding:"14px 16px",
                borderBottom: i < arr.length - 1 ? "1px solid #f1f5f9" : "none",
                background:"none",border: "none",
                borderBottomWidth: i < arr.length - 1 ? 1 : 0,
                borderBottomStyle:"solid",
                borderBottomColor:"#f1f5f9",
                cursor:"pointer",textAlign:"left",
              }}
            >
              <div style={{ width:36,height:36,borderRadius:12,background:item.bg,display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0 }}>
                <item.icon size={17} color={item.color} />
              </div>
              <span style={{ flex:1,fontSize:14,fontWeight:600,color:"#0f172a" }}>{item.label}</span>
              <ChevronRight size={16} color="#d1d5db" />
            </button>
          ))}
        </div>
      </div>

      <div style={{ padding:"12px 16px 0" }}>
        <button style={{ width:"100%",padding:"14px",borderRadius:16,border:"1px solid #fecaca",background:"#fff5f5",color:"#ef4444",fontSize:14,fontWeight:700,cursor:"pointer",display:"flex",alignItems:"center",justifyContent:"center",gap:8 }}>
          <LogOut size={16} />
          Chiqish
        </button>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   ADMIN: DASHBOARD
───────────────────────────────────────────────────────────── */
function AdminDashboard() {
  const kpis = [
    { label:"Bugungi tushum",value:"$11,240",change:"+18%",up:true,icon:DollarSign,color:"#2563eb",bg:"#eff6ff" },
    { label:"Yangi mijozlar",value:"48",change:"+12%",up:true,icon:Users,color:"#16a34a",bg:"#f0fdf4" },
    { label:"Berilgan ballar",value:"18.4K",change:"+24%",up:true,icon:Star,color:"#f59e0b",bg:"#fffbeb" },
    { label:"Sovg'a olishlar",value:"23",change:"-3%",up:false,icon:Gift,color:"#7c3aed",bg:"#f5f3ff" },
  ];

  return (
    <div style={{ background:"#F8FAFC",minHeight:"100%",paddingBottom:100 }}>
      {/* Header */}
      <div style={{
        background:"linear-gradient(160deg,#020617,#0f172a,#1e293b)",
        padding:"20px 20px 28px",position:"relative",overflow:"hidden",
      }}>
        <div style={{ position:"absolute",top:-30,right:-30,width:140,height:140,borderRadius:"50%",background:"radial-gradient(circle,rgba(37,99,235,0.2),transparent 70%)" }} />
        <div style={{ display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:4 }}>
          <div>
            <h2 style={{ color:"white",fontSize:22,fontWeight:900,fontFamily:"'Plus Jakarta Sans',sans-serif",margin:"0 0 2px" }}>Boshqaruv paneli</h2>
            <p style={{ color:"rgba(148,163,184,0.8)",fontSize:12,margin:0 }}>Dushanba, 30-iyun, 2025</p>
          </div>
          <button style={{ width:36,height:36,borderRadius:12,background:"rgba(255,255,255,0.1)",border:"1px solid rgba(255,255,255,0.1)",cursor:"pointer",display:"flex",alignItems:"center",justifyContent:"center" }}>
            <RefreshCw size={16} color="rgba(255,255,255,0.7)" />
          </button>
        </div>
      </div>

      {/* KPIs */}
      <div style={{ padding:"16px 16px 0",display:"grid",gridTemplateColumns:"1fr 1fr",gap:10 }}>
        {kpis.map((k) => (
          <div key={k.label} style={{
            background:"white",borderRadius:18,padding:"14px 14px",
            boxShadow:"0 2px 12px rgba(0,0,0,0.06)",border:"1px solid rgba(0,0,0,0.04)",
          }}>
            <div style={{ display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:10 }}>
              <div style={{ width:34,height:34,borderRadius:11,background:k.bg,display:"flex",alignItems:"center",justifyContent:"center" }}>
                <k.icon size={16} color={k.color} />
              </div>
              <span style={{
                fontSize:10,fontWeight:800,padding:"2px 7px",borderRadius:99,
                background: k.up ? "#f0fdf4" : "#fff5f5",
                color: k.up ? "#16a34a" : "#ef4444",
              }}>
                {k.change}
              </span>
            </div>
            <p style={{ fontSize:22,fontWeight:900,color:"#0f172a",fontFamily:"'Plus Jakarta Sans',sans-serif",margin:0 }}>{k.value}</p>
            <p style={{ fontSize:10,color:"#94a3b8",fontWeight:600,marginTop:2 }}>{k.label}</p>
          </div>
        ))}
      </div>

      {/* Revenue Chart */}
      <div style={{ padding:"16px 16px 0" }}>
        <div style={{ background:"white",borderRadius:20,padding:"16px 16px 8px",boxShadow:"0 2px 16px rgba(0,0,0,0.06)",border:"1px solid rgba(0,0,0,0.04)" }}>
          <div style={{ display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:12 }}>
            <p style={{ fontSize:14,fontWeight:800,color:"#0f172a",margin:0 }}>Haftalik tushum</p>
            <div style={{ display:"flex",alignItems:"center",gap:4 }}>
              <div style={{ width:8,height:8,borderRadius:"50%",background:"#2563eb" }} />
              <span style={{ fontSize:11,color:"#64748b" }}>Bu hafta</span>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={130}>
            <AreaChart data={salesData} margin={{ top:4,right:4,bottom:0,left:-20 }}>
              <defs>
                <linearGradient id="salesGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2563eb" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="day" tick={{ fontSize:10,fill:"#94a3b8" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize:10,fill:"#94a3b8" }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ borderRadius:12,border:"none",boxShadow:"0 8px 32px rgba(0,0,0,0.15)",fontSize:12,background:"white" }}
                formatter={(v: number) => [`$${v.toLocaleString()}`, "Tushum"]}
              />
              <Area type="monotone" dataKey="sales" stroke="#2563eb" strokeWidth={2.5} fill="url(#salesGrad)" dot={false} activeDot={{ r:5,fill:"#2563eb",strokeWidth:0 }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Customers */}
      <div style={{ padding:"16px 16px 0" }}>
        <div style={{ display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:10 }}>
          <p style={{ fontSize:14,fontWeight:800,color:"#0f172a",margin:0 }}>Eng faol mijozlar</p>
          <button style={{ fontSize:11,color:"#2563eb",fontWeight:700,background:"none",border:"none",cursor:"pointer" }}>Barchasi</button>
        </div>
        <div style={{ background:"white",borderRadius:20,overflow:"hidden",boxShadow:"0 2px 16px rgba(0,0,0,0.06)",border:"1px solid rgba(0,0,0,0.04)" }}>
          {/* Table header */}
          <div style={{ display:"grid",gridTemplateColumns:"1fr 60px 60px",padding:"10px 16px",background:"#f8fafc",borderBottom:"1px solid #f1f5f9" }}>
            {["Mijoz","Ball","Xarid"].map((h) => (
              <span key={h} style={{ fontSize:10,fontWeight:700,color:"#94a3b8",textTransform:"uppercase",letterSpacing:"0.06em" }}>{h}</span>
            ))}
          </div>
          {adminCustomers.map((c,i) => (
            <div key={c.id} style={{
              display:"grid",gridTemplateColumns:"1fr 60px 60px",
              padding:"12px 16px",alignItems:"center",
              borderBottom: i < adminCustomers.length-1 ? "1px solid #f1f5f9" : "none",
            }}>
              <div style={{ display:"flex",alignItems:"center",gap:10 }}>
                <div style={{ width:32,height:32,borderRadius:10,background:AVATAR_GRADIENTS[i % 4],display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0 }}>
                  <span style={{ color:"white",fontSize:11,fontWeight:800 }}>{c.initials}</span>
                </div>
                <div>
                  <p style={{ fontSize:12,fontWeight:700,color:"#0f172a",margin:0,whiteSpace:"nowrap",overflow:"hidden",textOverflow:"ellipsis",maxWidth:100 }}>{c.name}</p>
                  <LevelBadge level={c.level} />
                </div>
              </div>
              <span style={{ fontSize:12,fontWeight:800,color:"#2563eb" }}>{c.points.toLocaleString()}</span>
              <span style={{ fontSize:12,fontWeight:700,color:"#0f172a" }}>{c.total}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Activity bar chart */}
      <div style={{ padding:"16px 16px 0" }}>
        <div style={{ background:"white",borderRadius:20,padding:"16px 16px 8px",boxShadow:"0 2px 16px rgba(0,0,0,0.06)",border:"1px solid rgba(0,0,0,0.04)" }}>
          <p style={{ fontSize:14,fontWeight:800,color:"#0f172a",margin:"0 0 12px" }}>Kunlik mijozlar</p>
          <ResponsiveContainer width="100%" height={90}>
            <BarChart data={salesData} margin={{ top:0,right:4,bottom:0,left:-20 }}>
              <XAxis dataKey="day" tick={{ fontSize:10,fill:"#94a3b8" }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ borderRadius:12,border:"none",fontSize:12,boxShadow:"0 8px 24px rgba(0,0,0,0.12)" }} formatter={(v:number) => [v,"Mijozlar"]} />
              <Bar dataKey="customers" fill="#2563eb" radius={[6,6,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   ADMIN: POS REGISTER PURCHASE
───────────────────────────────────────────────────────────── */
function AdminPOS() {
  const [amount, setAmount] = useState("0");
  const [phone, setPhone] = useState("");
  const [foundCustomer, setFoundCustomer] = useState<typeof adminCustomers[0] | null>(null);
  const [products, setProducts] = useState("");
  const [success, setSuccess] = useState(false);

  const pts = Math.floor(parseFloat(amount.replace(/,/g,"")) || 0);

  const handleKey = (k: string) => {
    if (k === "⌫") {
      setAmount(p => p.length > 1 ? p.slice(0,-1) : "0");
    } else if (k === "." && amount.includes(".")) {
      // no-op
    } else if (amount === "0" && k !== ".") {
      setAmount(k);
    } else {
      const next = amount + k;
      if (next.replace(".","").length <= 8) setAmount(next);
    }
  };

  const handlePhoneSearch = () => {
    const found = adminCustomers.find(c => c.phone.replace(/\D/g,"").includes(phone.replace(/\D/g,"")));
    setFoundCustomer(found ?? null);
  };

  const handleSave = () => {
    if (parseFloat(amount) > 0) {
      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
        setAmount("0");
        setPhone("");
        setFoundCustomer(null);
        setProducts("");
      }, 2500);
    }
  };

  const keys = ["7","8","9","4","5","6","1","2","3",".","0","⌫"];

  return (
    <div style={{ background:"#F8FAFC",minHeight:"100%",paddingBottom:100 }}>
      {/* Header */}
      <div style={{ background:"linear-gradient(160deg,#020617,#0f172a)", padding:"20px 20px 20px" }}>
        <h2 style={{ color:"white",fontSize:22,fontWeight:900,fontFamily:"'Plus Jakarta Sans',sans-serif",margin:"0 0 2px" }}>Xaridni ro'yxatdan o'tkazish</h2>
        <p style={{ color:"rgba(148,163,184,0.7)",fontSize:12,margin:0 }}>POS terminal</p>
      </div>

      <div style={{ padding:"16px 16px 0" }}>
        {/* Customer Search */}
        <div style={{ background:"white",borderRadius:20,padding:16,boxShadow:"0 2px 16px rgba(0,0,0,0.07)",border:"1px solid rgba(0,0,0,0.04)",marginBottom:12 }}>
          <p style={{ fontSize:11,fontWeight:700,color:"#94a3b8",textTransform:"uppercase",letterSpacing:"0.08em",marginBottom:8 }}>Mijoz</p>
          <div style={{ display:"flex",gap:8 }}>
            <div style={{ position:"relative",flex:1 }}>
              <Phone size={15} style={{ position:"absolute",left:12,top:"50%",transform:"translateY(-50%)",color:"#94a3b8" }} />
              <input
                type="tel"
                placeholder="+1 555-000-0000"
                value={phone}
                onChange={e => setPhone(e.target.value)}
                style={{ width:"100%",paddingLeft:36,paddingRight:12,paddingTop:11,paddingBottom:11,borderRadius:14,border:"1.5px solid #e2e8f0",fontSize:14,background:"#f8fafc",outline:"none",boxSizing:"border-box" }}
              />
            </div>
            <button
              onClick={handlePhoneSearch}
              style={{ padding:"0 16px",borderRadius:14,background:"#2563eb",color:"white",border:"none",fontSize:13,fontWeight:700,cursor:"pointer",whiteSpace:"nowrap" }}
            >
              Topish
            </button>
          </div>

          {foundCustomer && (
            <div className="anim-slideInUp" style={{
              marginTop:10,display:"flex",alignItems:"center",gap:10,
              background:"#f0fdf4",borderRadius:14,padding:"10px 12px",border:"1px solid #bbf7d0",
            }}>
              <div style={{ width:36,height:36,borderRadius:12,background:"linear-gradient(135deg,#16a34a,#22c55e)",display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0 }}>
                <span style={{ color:"white",fontSize:13,fontWeight:800 }}>{foundCustomer.initials}</span>
              </div>
              <div style={{ flex:1 }}>
                <p style={{ fontSize:13,fontWeight:800,color:"#065f46",margin:0 }}>{foundCustomer.name}</p>
                <div style={{ display:"flex",alignItems:"center",gap:6,marginTop:2 }}>
                  <LevelBadge level={foundCustomer.level} />
                  <span style={{ fontSize:10,color:"#16a34a",fontWeight:700 }}>{foundCustomer.points.toLocaleString()} ball</span>
                </div>
              </div>
              <Check size={18} color="#16a34a" />
            </div>
          )}
        </div>

        {/* Amount Display */}
        <div style={{
          background:"linear-gradient(160deg,#0f172a,#1e293b)",
          borderRadius:20,padding:"20px 20px 16px",marginBottom:12,
          boxShadow:"0 8px 32px rgba(0,0,0,0.3)",
        }}>
          <p style={{ color:"rgba(148,163,184,0.7)",fontSize:11,textTransform:"uppercase",letterSpacing:"0.1em",marginBottom:8 }}>Xarid summasi</p>
          <div style={{ display:"flex",alignItems:"flex-start" }}>
            <span style={{ color:"rgba(255,255,255,0.5)",fontSize:24,fontWeight:700,marginTop:8,marginRight:4 }}>$</span>
            <span style={{ color:"white",fontSize:52,fontWeight:900,fontFamily:"'Plus Jakarta Sans',sans-serif",lineHeight:1,fontVariantNumeric:"tabular-nums" }}>
              {parseFloat(amount).toLocaleString("en-US",{ minimumFractionDigits: amount.includes(".") ? (amount.split(".")[1]?.length ?? 0) : 0, maximumFractionDigits: 2 })}
            </span>
          </div>
          {/* Products input */}
          <input
            type="text"
            placeholder="Mahsulot tavsifi (ixtiyoriy)"
            value={products}
            onChange={e => setProducts(e.target.value)}
            style={{
              marginTop:12,width:"100%",background:"rgba(255,255,255,0.08)",border:"1px solid rgba(255,255,255,0.1)",
              borderRadius:12,padding:"9px 12px",color:"white",fontSize:13,outline:"none",boxSizing:"border-box",
            }}
          />
          <div style={{ display:"flex",alignItems:"center",justifyContent:"space-between",marginTop:12,paddingTop:12,borderTop:"1px solid rgba(255,255,255,0.08)" }}>
            <div style={{ display:"flex",alignItems:"center",gap:8 }}>
              <Star size={16} color="#f59e0b" />
              <span style={{ color:"rgba(255,255,255,0.7)",fontSize:13 }}>Yig'iladigan ballar</span>
            </div>
            <span style={{ color:"#fbbf24",fontSize:22,fontWeight:900,fontFamily:"'Plus Jakarta Sans',sans-serif" }}>
              +{pts} ball
            </span>
          </div>
        </div>

        {/* Numpad */}
        <div style={{ background:"white",borderRadius:20,padding:14,boxShadow:"0 2px 16px rgba(0,0,0,0.07)",border:"1px solid rgba(0,0,0,0.04)",marginBottom:12 }}>
          <div style={{ display:"grid",gridTemplateColumns:"1fr 1fr 1fr",gap:8 }}>
            {keys.map((k) => (
              <button
                key={k}
                onClick={() => handleKey(k)}
                style={{
                  height:58,borderRadius:16,border:"1px solid #e2e8f0",
                  background: k === "⌫" ? "#fef2f2" : "#f8fafc",
                  fontSize: k === "⌫" ? 18 : 22,
                  fontWeight:800,color: k === "⌫" ? "#ef4444" : "#0f172a",
                  cursor:"pointer",transition:"all 0.1s",fontFamily:"'Plus Jakarta Sans',sans-serif",
                  boxShadow:"0 2px 8px rgba(0,0,0,0.04)",
                }}
              >
                {k}
              </button>
            ))}
          </div>
        </div>

        {/* Save */}
        <button
          onClick={handleSave}
          style={{
            width:"100%",padding:"16px",borderRadius:18,border:"none",cursor:"pointer",
            background: pts > 0 ? "linear-gradient(135deg,#1d4ed8,#2563eb)" : "#e2e8f0",
            color: pts > 0 ? "white" : "#94a3b8",
            fontSize:16,fontWeight:800,
            boxShadow: pts > 0 ? "0 8px 32px rgba(37,99,235,0.4)" : "none",
            display:"flex",alignItems:"center",justifyContent:"center",gap:10,
            fontFamily:"'Plus Jakarta Sans',sans-serif",
            transition:"all 0.2s",
          }}
        >
          <Check size={20} />
          Xaridni saqlash
        </button>
      </div>

      {/* Success overlay */}
      {success && (
        <div style={{
          position:"fixed",inset:0,background:"rgba(0,0,0,0.5)",backdropFilter:"blur(8px)",
          display:"flex",alignItems:"center",justifyContent:"center",zIndex:100,
        }}>
          <div className="anim-scalePop" style={{
            background:"white",borderRadius:28,padding:"32px 28px",textAlign:"center",
            margin:"0 24px",boxShadow:"0 32px 80px rgba(0,0,0,0.3)",
          }}>
            <div style={{ width:72,height:72,borderRadius:24,background:"linear-gradient(135deg,#16a34a,#22c55e)",display:"flex",alignItems:"center",justifyContent:"center",margin:"0 auto 16px",boxShadow:"0 8px 24px rgba(34,197,94,0.4)" }}>
              <Check size={36} color="white" />
            </div>
            <h3 style={{ fontSize:20,fontWeight:900,color:"#0f172a",fontFamily:"'Plus Jakarta Sans',sans-serif",margin:"0 0 8px" }}>
              Xarid ro'yxatdan o'tdi!
            </h3>
            <p style={{ fontSize:14,color:"#64748b",margin:"0 0 16px" }}>
              Muvaffaqiyatli qayta ishlandi
            </p>
            <div style={{ background:"#f0fdf4",borderRadius:16,padding:"12px 20px",display:"inline-flex",alignItems:"center",gap:8 }}>
              <Star size={18} color="#16a34a" />
              <span style={{ fontSize:18,fontWeight:900,color:"#16a34a",fontFamily:"'Plus Jakarta Sans',sans-serif" }}>+{pts} ball qo'shildi</span>
            </div>
            {foundCustomer && (
              <p style={{ fontSize:12,color:"#94a3b8",marginTop:8 }}>
                {foundCustomer.name} hisobiga
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   ADMIN: CUSTOMERS
───────────────────────────────────────────────────────────── */
function AdminCustomers() {
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<typeof adminCustomers[0] | null>(null);

  const filtered = adminCustomers.filter(c =>
    c.name.toLowerCase().includes(search.toLowerCase()) || c.phone.includes(search)
  );

  return (
    <div style={{ background:"#F8FAFC",minHeight:"100%",paddingBottom:100 }}>
      <div style={{ background:"linear-gradient(160deg,#065f46,#16a34a)", padding:"20px 20px 28px" }}>
        <h2 style={{ color:"white",fontSize:22,fontWeight:900,fontFamily:"'Plus Jakarta Sans',sans-serif",margin:"0 0 12px" }}>Mijozlar</h2>
        <div style={{ position:"relative" }}>
          <Search size={16} style={{ position:"absolute",left:14,top:"50%",transform:"translateY(-50%)",color:"rgba(255,255,255,0.5)" }} />
          <input
            type="search"
            placeholder="Ism yoki telefon bo'yicha qidirish..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{
              width:"100%",paddingLeft:42,paddingRight:14,paddingTop:12,paddingBottom:12,
              borderRadius:16,border:"1px solid rgba(255,255,255,0.2)",
              background:"rgba(255,255,255,0.15)",color:"white",fontSize:14,outline:"none",boxSizing:"border-box",
            }}
          />
        </div>
      </div>

      {/* Table */}
      <div style={{ padding:"16px 16px 0" }}>
        {/* Header row */}
        <div style={{ display:"grid",gridTemplateColumns:"1fr 72px 60px",padding:"10px 16px",marginBottom:4 }}>
          {["Mijoz","Ball","Jami"].map((h) => (
            <span key={h} style={{ fontSize:10,fontWeight:700,color:"#94a3b8",textTransform:"uppercase",letterSpacing:"0.06em" }}>{h}</span>
          ))}
        </div>

        <div style={{ background:"white",borderRadius:20,overflow:"hidden",boxShadow:"0 2px 16px rgba(0,0,0,0.06)",border:"1px solid rgba(0,0,0,0.04)" }}>
          {filtered.length === 0 ? (
            <div style={{ padding:"40px 20px",textAlign:"center" }}>
              <Users size={32} color="#d1d5db" style={{ marginBottom:8 }} />
              <p style={{ color:"#94a3b8",fontSize:14,fontWeight:600 }}>Mijozlar topilmadi</p>
            </div>
          ) : filtered.map((c, i) => (
            <button
              key={c.id}
              onClick={() => setSelected(c)}
              style={{
                display:"grid",gridTemplateColumns:"1fr 72px 60px",
                padding:"14px 16px",alignItems:"center",width:"100%",
                borderBottom: i < filtered.length-1 ? "1px solid #f1f5f9" : "none",
                background: selected?.id === c.id ? "#f0f9ff" : "transparent",
                border: "none",borderBottomWidth: i < filtered.length-1 ? 1 : 0,
                borderBottomStyle:"solid",borderBottomColor:"#f1f5f9",
                cursor:"pointer",textAlign:"left",
                transition:"background 0.15s",
              }}
            >
              <div style={{ display:"flex",alignItems:"center",gap:10 }}>
                <div style={{ width:36,height:36,borderRadius:12,background:AVATAR_GRADIENTS[i % 4],display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0 }}>
                  <span style={{ color:"white",fontSize:12,fontWeight:800 }}>{c.initials}</span>
                </div>
                <div style={{ minWidth:0 }}>
                  <p style={{ fontSize:13,fontWeight:700,color:"#0f172a",margin:0,whiteSpace:"nowrap",overflow:"hidden",textOverflow:"ellipsis",maxWidth:110 }}>{c.name}</p>
                  <LevelBadge level={c.level} />
                </div>
              </div>
              <span style={{ fontSize:13,fontWeight:800,color:"#2563eb" }}>{c.points.toLocaleString()}</span>
              <span style={{ fontSize:12,fontWeight:700,color:"#0f172a" }}>{c.total}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Profile preview */}
      {selected && (
        <div style={{
          position:"fixed",inset:0,background:"rgba(0,0,0,0.5)",backdropFilter:"blur(6px)",zIndex:90,
          display:"flex",alignItems:"flex-end",
        }} onClick={() => setSelected(null)}>
          <div
            className="anim-slideInUp"
            onClick={e => e.stopPropagation()}
            style={{
              background:"white",borderRadius:"24px 24px 0 0",width:"100%",maxWidth:390,
              margin:"0 auto",padding:"0 0 32px",
              boxShadow:"0 -16px 64px rgba(0,0,0,0.25)",
            }}
          >
            <div style={{ width:40,height:4,background:"#e2e8f0",borderRadius:99,margin:"12px auto 20px" }} />
            <div style={{
              background:"linear-gradient(135deg,#1e3a8a,#2563eb)",
              margin:"0 16px 16px",borderRadius:20,padding:"20px",
            }}>
              <div style={{ display:"flex",alignItems:"center",gap:14,marginBottom:16 }}>
                <div style={{ width:52,height:52,borderRadius:18,background:"rgba(255,255,255,0.2)",display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0 }}>
                  <span style={{ color:"white",fontSize:18,fontWeight:900 }}>{selected.initials}</span>
                </div>
                <div>
                  <p style={{ color:"white",fontSize:17,fontWeight:900,fontFamily:"'Plus Jakarta Sans',sans-serif",margin:0 }}>{selected.name}</p>
                  <p style={{ color:"rgba(255,255,255,0.65)",fontSize:12,margin:"2px 0 6px" }}>{selected.phone}</p>
                  <LevelBadge level={selected.level} size="md" />
                </div>
              </div>
              <div style={{ display:"grid",gridTemplateColumns:"1fr 1fr 1fr",gap:8 }}>
                {[
                  { l:"Ball",v:selected.points.toLocaleString() },
                  { l:"Xaridlar",v:String(selected.purchases) },
                  { l:"Jami",v:selected.total },
                ].map(s => (
                  <div key={s.l} style={{ background:"rgba(255,255,255,0.1)",borderRadius:12,padding:"8px 10px",textAlign:"center" }}>
                    <p style={{ color:"white",fontSize:15,fontWeight:900,fontFamily:"'Plus Jakarta Sans',sans-serif",margin:0 }}>{s.v}</p>
                    <p style={{ color:"rgba(255,255,255,0.6)",fontSize:10,marginTop:2 }}>{s.l}</p>
                  </div>
                ))}
              </div>
            </div>
            <div style={{ padding:"0 16px",display:"flex",flexDirection:"column",gap:8 }}>
              <button style={{ padding:"14px",borderRadius:16,background:"#2563eb",color:"white",fontSize:14,fontWeight:800,border:"none",cursor:"pointer" }}>
                To'liq tarixni ko'rish
              </button>
              <button style={{ padding:"12px",borderRadius:16,background:"#f1f5f9",color:"#64748b",fontSize:14,fontWeight:700,border:"none",cursor:"pointer" }}>
                Profilni tahrirlash
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   ADMIN: REWARDS MANAGEMENT
───────────────────────────────────────────────────────────── */
function AdminRewards() {
  const [items, setItems] = useState(rewardsData.map(r => ({ ...r, status: "Active" })));
  const toggle = (id: number) => setItems(p => p.map(r => r.id === id ? { ...r, status: r.status === "Active" ? "Disabled" : "Active" } : r));

  return (
    <div style={{ background:"#F8FAFC",minHeight:"100%",paddingBottom:100 }}>
      <div style={{ background:"linear-gradient(160deg,#4c1d95,#7c3aed)", padding:"20px 20px 28px" }}>
        <div style={{ display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:4 }}>
          <h2 style={{ color:"white",fontSize:22,fontWeight:900,fontFamily:"'Plus Jakarta Sans',sans-serif",margin:0 }}>Sovg'alar</h2>
          <button style={{
            display:"flex",alignItems:"center",gap:6,padding:"8px 14px",
            background:"rgba(255,255,255,0.2)",border:"1px solid rgba(255,255,255,0.2)",
            borderRadius:14,color:"white",fontSize:12,fontWeight:700,cursor:"pointer",
          }}>
            <Plus size={14} /> Sovg'a qo'shish
          </button>
        </div>
        <p style={{ color:"rgba(255,255,255,0.6)",fontSize:12,margin:0 }}>{items.filter(i=>i.status==="Active").length} faol · jami {items.length}</p>
      </div>

      <div style={{ padding:"16px 16px 0",display:"grid",gridTemplateColumns:"1fr 1fr",gap:12 }}>
        {items.map((r) => (
          <div key={r.id} style={{
            background:"white",borderRadius:20,overflow:"hidden",
            boxShadow:"0 2px 16px rgba(0,0,0,0.07)",border:"1px solid rgba(0,0,0,0.04)",
            opacity: r.status === "Disabled" ? 0.6 : 1,transition:"opacity 0.2s",
          }}>
            <div style={{ height:90,position:"relative",overflow:"hidden",background:"#f8fafc" }}>
              <img src={r.img} alt={r.name} style={{ width:"100%",height:"100%",objectFit:"cover" }} />
              <div style={{ position:"absolute",top:8,right:8 }}>
                <span style={{
                  fontSize:9,fontWeight:800,padding:"2px 7px",borderRadius:99,
                  background: r.status === "Active" ? "#22c55e" : "#94a3b8",
                  color:"white",
                }}>
                  {r.status === "Active" ? "Faol" : "O'chirilgan"}
                </span>
              </div>
            </div>
            <div style={{ padding:"12px 12px 14px" }}>
              <p style={{ fontSize:13,fontWeight:800,color:"#0f172a",margin:"0 0 2px" }}>{r.name}</p>
              <p style={{ fontSize:12,fontWeight:900,color:"#7c3aed",marginBottom:10 }}>{r.points.toLocaleString()} ball</p>
              <div style={{ display:"grid",gridTemplateColumns:"1fr 1fr",gap:6 }}>
                <button style={{ padding:"7px",borderRadius:10,border:"1px solid #e2e8f0",background:"#f8fafc",fontSize:11,fontWeight:700,color:"#64748b",cursor:"pointer",display:"flex",alignItems:"center",justifyContent:"center",gap:4 }}>
                  <Edit2 size={11} /> Tahrirlash
                </button>
                <button
                  onClick={() => toggle(r.id)}
                  style={{
                    padding:"7px",borderRadius:10,border:"none",fontSize:11,fontWeight:700,cursor:"pointer",
                    background: r.status === "Active" ? "#fef2f2" : "#f0fdf4",
                    color: r.status === "Active" ? "#ef4444" : "#16a34a",
                    display:"flex",alignItems:"center",justifyContent:"center",gap:4,
                  }}
                >
                  <ToggleLeft size={11} />
                  {r.status === "Active" ? "O'chirish" : "Yoqish"}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   ADMIN: PROMOTIONS
───────────────────────────────────────────────────────────── */
function AdminPromotions() {
  const campaigns = [
    { title:"Yozgi 10% chegirma",status:"Faol",color:"#22c55e",bg:"#f0fdf4",ends:"15-iyul",reach:"2 481",icon:Percent,iconColor:"#16a34a",iconBg:"#dcfce7" },
    { title:"Ikki baravar ball",status:"Tez orada",color:"#f59e0b",bg:"#fffbeb",ends:"5-6 iyul",reach:"Kumush+",icon:Zap,iconColor:"#d97706",iconBg:"#fef3c7" },
    { title:"Tug'ilgan kun bonusi",status:"Faol",color:"#8b5cf6",bg:"#f5f3ff",ends:"Doimiy",reach:"Barcha a'zolar",icon:Gift,iconColor:"#7c3aed",iconBg:"#ede9fe" },
  ];

  const actions = [
    { label:"Chegirma yaratish",desc:"Barcha xaridlarga % yoki $ chegirma",icon:Percent,gradient:"linear-gradient(135deg,#1e3a8a,#2563eb)" },
    { label:"Ikki baravar ball",desc:"Ma'lum muddatga 2x yoki ko'proq",icon:Zap,gradient:"linear-gradient(135deg,#92400e,#d97706)" },
    { label:"Mavsumiy aksiya",desc:"Bayram va tadbir takliflari",icon:Star,gradient:"linear-gradient(135deg,#4c1d95,#7c3aed)" },
    { label:"Tezkor savdo",desc:"Qisqa muddatli shoshilinch taklif",icon:Flame,gradient:"linear-gradient(135deg,#7f1d1d,#ef4444)" },
  ];

  return (
    <div style={{ background:"#F8FAFC",minHeight:"100%",paddingBottom:100 }}>
      <div style={{ background:"linear-gradient(160deg,#7f1d1d,#dc2626)", padding:"20px 20px 28px" }}>
        <h2 style={{ color:"white",fontSize:22,fontWeight:900,fontFamily:"'Plus Jakarta Sans',sans-serif",margin:"0 0 2px" }}>Aksiyalar</h2>
        <p style={{ color:"rgba(255,255,255,0.65)",fontSize:12,margin:0 }}>Kampaniyalarni yarating va boshqaring</p>
      </div>

      {/* Quick Create */}
      <div style={{ padding:"16px 16px 0" }}>
        <p style={{ fontSize:12,fontWeight:700,color:"#94a3b8",textTransform:"uppercase",letterSpacing:"0.08em",marginBottom:10 }}>Tez yaratish</p>
        <div style={{ display:"grid",gridTemplateColumns:"1fr 1fr",gap:10 }}>
          {actions.map((a) => (
            <button key={a.label} style={{
              background:"white",borderRadius:18,padding:"14px 14px",
              boxShadow:"0 2px 12px rgba(0,0,0,0.06)",border:"1px solid rgba(0,0,0,0.04)",
              cursor:"pointer",textAlign:"left",display:"flex",flexDirection:"column",gap:8,
              transition:"transform 0.15s",
            }}>
              <div style={{ width:40,height:40,borderRadius:14,background:a.gradient,display:"flex",alignItems:"center",justifyContent:"center" }}>
                <a.icon size={19} color="white" />
              </div>
              <div>
                <p style={{ fontSize:13,fontWeight:800,color:"#0f172a",margin:"0 0 2px" }}>{a.label}</p>
                <p style={{ fontSize:11,color:"#94a3b8",margin:0 }}>{a.desc}</p>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Active campaigns */}
      <div style={{ padding:"16px 16px 0" }}>
        <p style={{ fontSize:12,fontWeight:700,color:"#94a3b8",textTransform:"uppercase",letterSpacing:"0.08em",marginBottom:10 }}>Faol kampaniyalar</p>
        <div style={{ display:"flex",flexDirection:"column",gap:10 }}>
          {campaigns.map((c) => (
            <div key={c.title} style={{
              background:"white",borderRadius:18,padding:"14px 16px",
              boxShadow:"0 2px 12px rgba(0,0,0,0.06)",border:"1px solid rgba(0,0,0,0.04)",
              display:"flex",alignItems:"center",gap:12,
            }}>
              <div style={{ width:42,height:42,borderRadius:14,background:c.iconBg,display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0 }}>
                <c.icon size={19} color={c.iconColor} />
              </div>
              <div style={{ flex:1,minWidth:0 }}>
                <p style={{ fontSize:13,fontWeight:800,color:"#0f172a",margin:"0 0 3px",whiteSpace:"nowrap",overflow:"hidden",textOverflow:"ellipsis" }}>
                  {c.title}
                </p>
                <p style={{ fontSize:11,color:"#94a3b8",margin:0 }}>Tugaydi: {c.ends} · {c.reach} mijoz</p>
              </div>
              <div style={{ display:"flex",flexDirection:"column",alignItems:"flex-end",gap:4,flexShrink:0 }}>
                <span style={{ fontSize:10,fontWeight:800,padding:"2px 8px",borderRadius:99,background:c.bg,color:c.color }}>
                  {c.status}
                </span>
                <button style={{ background:"none",border:"none",cursor:"pointer",padding:0 }}>
                  <Edit2 size={14} color="#94a3b8" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   ROLE SELECTOR
───────────────────────────────────────────────────────────── */
function RoleSelector({ onSelect }: { onSelect: (r: "customer" | "admin") => void }) {
  return (
    <div style={{
      minHeight:"100vh",
      background:"linear-gradient(160deg,#020617 0%,#0f172a 40%,#1e1b4b 70%,#1e3a8a 100%)",
      display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"space-between",
      padding:"60px 24px 48px",position:"relative",overflow:"hidden",
    }}>
      {/* Decorative orbs */}
      <div style={{ position:"absolute",top:-60,right:-60,width:240,height:240,borderRadius:"50%",background:"radial-gradient(circle,rgba(37,99,235,0.2),transparent 70%)" }} />
      <div style={{ position:"absolute",bottom:-40,left:-60,width:200,height:200,borderRadius:"50%",background:"radial-gradient(circle,rgba(124,58,237,0.2),transparent 70%)" }} />
      <div style={{ position:"absolute",top:"40%",right:-30,width:120,height:120,borderRadius:"50%",background:"radial-gradient(circle,rgba(34,197,94,0.1),transparent 70%)" }} />

      {/* Logo area */}
      <div className="anim-fadeSlideUp" style={{ textAlign:"center",position:"relative" }}>
        <div className="anim-float" style={{
          width:210,height:108,borderRadius:28,
          background:"linear-gradient(135deg,rgba(255,255,255,0.2),rgba(255,255,255,0.08))",
          backdropFilter:"blur(20px)",border:"1px solid rgba(255,255,255,0.25)",
          display:"flex",alignItems:"center",justifyContent:"center",
          margin:"0 auto 24px",
          overflow:"hidden",
          boxShadow:"0 16px 48px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.1) inset",
        }}>
          <img src={miramaxLogo} alt="Miramax MPP" style={{ width:"100%",height:"100%",objectFit:"cover" }} />
        </div>
        <h1 style={{ color:"white",fontSize:36,fontWeight:900,fontFamily:"'Plus Jakarta Sans',sans-serif",margin:"0 0 6px" }}>
          Miramax
        </h1>
        <p style={{ color:"rgba(148,163,184,0.8)",fontSize:15,margin:"0 0 8px" }}>Sodiqlik dasturi</p>
        <div style={{ display:"inline-flex",alignItems:"center",gap:6,background:"rgba(34,197,94,0.15)",border:"1px solid rgba(34,197,94,0.25)",borderRadius:99,padding:"4px 14px" }}>
          <span style={{ width:6,height:6,borderRadius:"50%",background:"#22c55e",display:"inline-block" }} />
          <span style={{ fontSize:11,color:"#4ade80",fontWeight:700,letterSpacing:"0.05em" }}>FAOL · 2 481 a'zo</span>
        </div>
      </div>

      {/* Role buttons */}
      <div style={{ width:"100%",position:"relative" }} className="anim-slideInUp">
        <p style={{ color:"rgba(148,163,184,0.7)",fontSize:13,fontWeight:700,textAlign:"center",marginBottom:16,letterSpacing:"0.05em",textTransform:"uppercase" }}>
          Davom etish
        </p>

        <button
          onClick={() => onSelect("customer")}
          style={{
            width:"100%",background:"white",borderRadius:22,padding:"16px 18px",
            display:"flex",alignItems:"center",gap:14,marginBottom:12,
            boxShadow:"0 8px 32px rgba(0,0,0,0.3)",border:"none",cursor:"pointer",
            transition:"transform 0.2s",
          }}
        >
          <div style={{
            width:52,height:52,borderRadius:18,
            background:"linear-gradient(135deg,#eff6ff,#dbeafe)",
            display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0,
          }}>
            <User size={26} color="#2563eb" />
          </div>
          <div style={{ textAlign:"left",flex:1 }}>
            <p style={{ fontSize:17,fontWeight:900,color:"#0f172a",fontFamily:"'Plus Jakarta Sans',sans-serif",margin:"0 0 2px" }}>Mijoz</p>
            <p style={{ fontSize:12,color:"#94a3b8",margin:0 }}>Ballar, sovg'alar va tarix</p>
          </div>
          <ChevronRight size={20} color="#d1d5db" />
        </button>

        <button
          onClick={() => onSelect("admin")}
          style={{
            width:"100%",
            background:"rgba(255,255,255,0.1)",backdropFilter:"blur(16px)",
            borderRadius:22,padding:"16px 18px",
            display:"flex",alignItems:"center",gap:14,
            border:"1px solid rgba(255,255,255,0.2)",cursor:"pointer",
            transition:"transform 0.2s",
          }}
        >
          <div style={{
            width:52,height:52,borderRadius:18,
            background:"rgba(255,255,255,0.15)",
            display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0,
          }}>
            <BarChart2 size={26} color="white" />
          </div>
          <div style={{ textAlign:"left",flex:1 }}>
            <p style={{ fontSize:17,fontWeight:900,color:"white",fontFamily:"'Plus Jakarta Sans',sans-serif",margin:"0 0 2px" }}>Admin</p>
            <p style={{ fontSize:12,color:"rgba(255,255,255,0.55)",margin:0 }}>Mijozlar va kampaniyalar</p>
          </div>
          <ChevronRight size={20} color="rgba(255,255,255,0.3)" />
        </button>
      </div>

      <p style={{ color:"rgba(100,116,139,0.6)",fontSize:11,position:"relative" }}>Miramax sodiqlik platformasi · v2.1</p>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   APP SHELLS
───────────────────────────────────────────────────────────── */
function CustomerApp({ onBack }: { onBack: () => void }) {
  const [tab, setTab] = useState<CustomerTab>("home");
  const tabs = [
    { id:"home" as const,     label:"Asosiy",    icon:<Home size={19} /> },
    { id:"rewards" as const,  label:"Sovg'a", icon:<Gift size={19} /> },
    { id:"discounts" as const,label:"Taklif",  icon:<Tag size={19} /> },
    { id:"history" as const,  label:"Tarix", icon:<Clock size={19} /> },
    { id:"profile" as const,  label:"Profil", icon:<User size={19} /> },
  ];
  return (
    <div style={{ position:"relative",minHeight:"100vh" }}>
      {/* Top bar */}
      <div style={{
        position:"sticky",top:0,zIndex:40,
        background:"rgba(255,255,255,0.92)",backdropFilter:"blur(20px)",
        borderBottom:"1px solid rgba(0,0,0,0.06)",
        padding:"10px 16px",display:"flex",alignItems:"center",gap:10,
        boxShadow:"0 1px 8px rgba(0,0,0,0.04)",
      }}>
        <button onClick={onBack} style={{ padding:4,background:"none",border:"none",cursor:"pointer",display:"flex" }}>
          <ArrowLeft size={20} color="#64748b" />
        </button>
        <div style={{ display:"flex",alignItems:"center",gap:8 }}>
          <div style={{ width:56,height:28,borderRadius:9,background:"#0ea5e9",display:"flex",alignItems:"center",justifyContent:"center",overflow:"hidden" }}>
            <img src={miramaxLogo} alt="Miramax" style={{ width:"100%",height:"100%",objectFit:"cover" }} />
          </div>
          <span style={{ fontWeight:800,fontSize:15,color:"#0f172a",fontFamily:"'Plus Jakarta Sans',sans-serif" }}>Miramax</span>
        </div>
        <span style={{ marginLeft:"auto",fontSize:10,color:"#2563eb",background:"#eff6ff",padding:"3px 10px",borderRadius:99,fontWeight:800 }}>
          MIJOZ
        </span>
      </div>

      {/* Screen content */}
      <div style={{ paddingBottom:96 }}>
        {tab === "home" && <CustomerHome onViewRewards={() => setTab("rewards")} />}
        {tab === "rewards" && <CustomerRewards />}
        {tab === "discounts" && <CustomerOffers />}
        {tab === "history" && <CustomerHistory />}
        {tab === "profile" && <CustomerProfile />}
      </div>

      <BottomNav tabs={tabs} active={tab} onSelect={setTab} />
    </div>
  );
}

function AdminApp({ onBack }: { onBack: () => void }) {
  const [tab, setTab] = useState<AdminTab>("dashboard");
  const tabs = [
    { id:"dashboard" as const,  label:"Asosiy",     icon:<LayoutDashboard size={19} /> },
    { id:"purchases" as const,  label:"POS",      icon:<ShoppingBag size={19} /> },
    { id:"customers" as const,  label:"Mijoz",icon:<Users size={19} /> },
    { id:"rewards" as const,    label:"Sovg'a",  icon:<Gift size={19} /> },
    { id:"promotions" as const, label:"Aksiya",   icon:<Megaphone size={19} /> },
  ];
  return (
    <div style={{ position:"relative",minHeight:"100vh" }}>
      <div style={{
        position:"sticky",top:0,zIndex:40,
        background:"rgba(255,255,255,0.92)",backdropFilter:"blur(20px)",
        borderBottom:"1px solid rgba(0,0,0,0.06)",
        padding:"10px 16px",display:"flex",alignItems:"center",gap:10,
        boxShadow:"0 1px 8px rgba(0,0,0,0.04)",
      }}>
        <button onClick={onBack} style={{ padding:4,background:"none",border:"none",cursor:"pointer",display:"flex" }}>
          <ArrowLeft size={20} color="#64748b" />
        </button>
        <div style={{ display:"flex",alignItems:"center",gap:8 }}>
          <div style={{ width:56,height:28,borderRadius:9,background:"#0ea5e9",display:"flex",alignItems:"center",justifyContent:"center",overflow:"hidden" }}>
            <img src={miramaxLogo} alt="Miramax" style={{ width:"100%",height:"100%",objectFit:"cover" }} />
          </div>
          <span style={{ fontWeight:800,fontSize:15,color:"#0f172a",fontFamily:"'Plus Jakarta Sans',sans-serif" }}>Admin panel</span>
        </div>
        <span style={{ marginLeft:"auto",fontSize:10,color:"white",background:"#0f172a",padding:"3px 10px",borderRadius:99,fontWeight:800 }}>
          ADMIN
        </span>
      </div>

      <div style={{ paddingBottom:96 }}>
        {tab === "dashboard" && <AdminDashboard />}
        {tab === "purchases" && <AdminPOS />}
        {tab === "customers" && <AdminCustomers />}
        {tab === "rewards" && <AdminRewards />}
        {tab === "promotions" && <AdminPromotions />}
      </div>

      <BottomNav tabs={tabs} active={tab} onSelect={setTab} />
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   ROOT
───────────────────────────────────────────────────────────── */
export default function App() {
  const [role, setRole] = useState<Role>(null);
  return (
    <>
      <style>{GLOBAL_CSS}</style>
      <div style={{
        minHeight:"100vh",background:"#e2e8f0",
        display:"flex",alignItems:"flex-start",justifyContent:"center",
      }}>
        <div style={{
          width:"100%",maxWidth:390,minHeight:"100vh",
          background:"#F8FAFC",position:"relative",overflowX:"hidden",
          fontFamily:"'Inter',system-ui,sans-serif",
        }}>
          {role === null && <RoleSelector onSelect={setRole} />}
          {role === "customer" && <CustomerApp onBack={() => setRole(null)} />}
          {role === "admin" && <AdminApp onBack={() => setRole(null)} />}
        </div>
      </div>
    </>
  );
}
