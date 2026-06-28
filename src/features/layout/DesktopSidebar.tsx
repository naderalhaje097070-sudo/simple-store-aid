import {
  Home, ReceiptText, Plus, Boxes, Store,
  Wallet, Banknote, Truck, Users, Settings as SettingsIcon,
  TrendingUp, ArrowDownCircle, CircleDollarSign, Activity,
} from "lucide-react";
import type React from "react";
import type { Screen } from "@/features/shared/types";

export function DesktopSidebar({
  screen, setScreen, myRole, onSale, onDayClose, onQuickExpense,
}: {
  screen: Screen; setScreen: (s: Screen) => void; myRole?: string;
  onSale: () => void; onDayClose: () => void; onQuickExpense: () => void;
}) {
  const Item = ({ id, label, Icon }: { id: Screen; label: string; Icon: typeof Home }) => {
    const active = screen === id;
    return (
      <button
        onClick={() => setScreen(id)}
        className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition ${
          active ? "bg-primary-soft text-primary font-bold" : "text-muted-foreground hover:bg-muted hover:text-foreground"
        }`}
      >
        <Icon className="w-4 h-4 shrink-0" />
        <span className="flex-1 text-right truncate">{label}</span>
      </button>
    );
  };
  const Group = ({ title, children }: { title: string; children: React.ReactNode }) => (
    <div className="mt-4">
      <div className="px-3 pb-1.5 text-[10px] font-bold text-muted-foreground/70 tracking-wider">{title}</div>
      <div className="space-y-0.5">{children}</div>
    </div>
  );
  return (
    <aside className="hidden md:flex md:flex-col md:w-64 md:shrink-0 md:sticky md:top-0 md:h-screen border-l border-border bg-card">
      <div className="px-5 py-4 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-2xl bg-primary text-primary-foreground grid place-items-center font-black">م</div>
          <div>
            <div className="text-sm font-black leading-tight">منجز</div>
            <div className="text-[10px] text-muted-foreground">دفتر المحل الذكي</div>
          </div>
        </div>
      </div>

      <div className="px-3 py-3 border-b border-border space-y-2">
        <button onClick={onSale} className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-primary text-primary-foreground text-sm font-bold hover:opacity-90">
          <Plus className="w-4 h-4" /> بيع سريع
        </button>
        <div className="grid grid-cols-2 gap-2">
          <button onClick={onQuickExpense} className="py-2 rounded-xl bg-muted text-xs font-bold hover:bg-muted/70">+ مصروف</button>
          <button onClick={onDayClose} className="py-2 rounded-xl bg-muted text-xs font-bold hover:bg-muted/70">إقفال اليوم</button>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto px-2 py-3">
        <Group title="اليومي">
          <Item id="home" label="الرئيسية" Icon={Home} />
          <Item id="invoices" label="الفواتير" Icon={ReceiptText} />
          <Item id="collected" label="المحصّل فعليًا" Icon={Wallet} />
          <Item id="profit" label="الربح" Icon={TrendingUp} />
          <Item id="expenses" label="المصروفات" Icon={ArrowDownCircle} />
        </Group>
        <Group title="الديون والعهدة">
          <Item id="debts" label="ديون العملاء" Icon={CircleDollarSign} />
          <Item id="courier_custody" label="عهدة المندوب" Icon={Truck} />
          <Item id="settlements" label="التسويات" Icon={Banknote} />
        </Group>
        <Group title="الإدارة">
          <Item id="inventory" label="المخزون" Icon={Boxes} />
          <Item id="customers" label="العملاء" Icon={Users} />
          <Item id="couriers" label="المندوبون" Icon={Truck} />
          <Item id="shop" label="أقسام المحل" Icon={Store} />
          <Item id="settings" label="الإعدادات" Icon={SettingsIcon} />
          {myRole === "owner" && <Item id="pilot" label="صحة النظام" Icon={Activity} />}
        </Group>
      </nav>

      <div className="px-4 py-3 border-t border-border text-[10px] text-muted-foreground text-center">
        نسخة تجريبية مغلقة
      </div>
    </aside>
  );
}
