/* eslint-disable @typescript-eslint/no-explicit-any */
import {
  Users,
  Boxes,
  Truck,
  Activity,
  Settings as SettingsIcon,
  ArrowDownCircle,
  CircleDollarSign,
  Banknote,
  Wallet,
  TrendingUp,
  ChevronLeft,
} from "lucide-react";
import type { Screen } from "@/features/shared/types";
import type { AppCtx } from "@/features/shared/AppContext";
import { TopBar } from "@/features/layout/TopBar";

export function ShopHubScreen(p: AppCtx) {
  const mgmtItems: { id: Screen; l: string; Icon: any; hint?: string }[] = [
    { id: "customers", l: "العملاء", Icon: Users },
    { id: "inventory", l: "المنتجات", Icon: Boxes },
    { id: "couriers", l: "المندوبون", Icon: Truck },
  ];
  if (p.myRole === "owner") {
    mgmtItems.push({ id: "pilot", l: "صحة النظام", Icon: Activity, hint: "أخطاء ومقاييس" });
  }
  mgmtItems.push({ id: "settings", l: "إعدادات المحل", Icon: SettingsIcon });
  const groups: { title: string; items: { id: Screen; l: string; Icon: any; hint?: string }[] }[] =
    [
      {
        title: "يومي",
        items: [
          { id: "expenses", l: "المصروفات", Icon: ArrowDownCircle },
          { id: "debts", l: "تحصيل دين", Icon: CircleDollarSign, hint: "ديون العملاء" },
          { id: "settlements", l: "تسوية مندوب", Icon: Banknote, hint: "تصفية العهدة" },
          { id: "collected", l: "المحصّل فعليًا", Icon: Wallet },
          { id: "profit", l: "الربح التقديري", Icon: TrendingUp, hint: "قد يشمل ديون" },
        ],
      },
      {
        title: "إدارة",
        items: mgmtItems,
      },
    ];
  return (
    <>
      <TopBar title="أقسام المحل" />
      <div className="px-4 pt-3">
        <div className="text-xs text-muted-foreground mb-3">
          الأرقام اليومية في «الرئيسية». هنا التنقّل بين أقسام المحل.
        </div>
        {/* Billing link hidden — Paddle integration kept in repo but not user-facing yet */}
        {groups.map((g) => (
          <div key={g.title} className="mb-4">
            <div className="text-xs font-bold text-muted-foreground mb-2 px-1">{g.title}</div>
            <div className="rounded-2xl bg-card border border-border divide-y divide-border overflow-hidden">
              {g.items.map((s) => (
                <button
                  key={s.id}
                  onClick={() => p.go(s.id)}
                  className="w-full flex items-center gap-3 px-4 py-3 text-right hover:bg-muted active:bg-muted"
                >
                  <s.Icon className="w-5 h-5 text-primary" />
                  <span className="flex-1 text-sm font-medium">{s.l}</span>
                  {s.hint && <span className="text-[10px] text-muted-foreground">{s.hint}</span>}
                  <ChevronLeft className="w-4 h-4 text-muted-foreground" />
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
