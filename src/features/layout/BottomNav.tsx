import { useState } from "react";
import { Home, ReceiptText, Plus, Boxes, Store, Loader2 } from "lucide-react";
import type { Screen } from "@/features/shared/types";

export function BottomNav({
  screen,
  setScreen,
  onSale,
  saleDisabled = false,
}: {
  screen: Screen;
  setScreen: (s: Screen) => void;
  onSale: () => void;
  saleDisabled?: boolean;
}) {
  const [busy, setBusy] = useState(false);
  const Tab = ({ id, label, Icon }: { id: Screen; label: string; Icon: typeof Home }) => {
    const active = screen === id;
    return (
      <button
        onClick={() => setScreen(id)}
        className="flex-1 flex flex-col items-center gap-1 py-2"
      >
        <Icon className={`w-5 h-5 ${active ? "text-primary" : "text-muted-foreground"}`} />
        <span
          className={`text-[11px] ${active ? "text-primary font-bold" : "text-muted-foreground"}`}
        >
          {label}
        </span>
      </button>
    );
  };
  return (
    <div className="fixed bottom-0 inset-x-0 z-40 pointer-events-none">
      <div className="mx-auto max-w-md relative">
        <div className="bg-card border-t border-border pointer-events-auto flex items-stretch px-2 pb-[max(env(safe-area-inset-bottom),8px)] pt-1">
          <Tab id="home" label="الرئيسية" Icon={Home} />
          <Tab id="invoices" label="الفواتير" Icon={ReceiptText} />
          <div className="w-16" />
          <Tab id="inventory" label="المخزون" Icon={Boxes} />
          <Tab id="shop" label="المحل" Icon={Store} />
        </div>
        <button
          onClick={() => {
            if (saleDisabled || busy) return;
            setBusy(true);
            onSale();
            window.setTimeout(() => setBusy(false), 600);
          }}
          disabled={saleDisabled || busy}
          aria-busy={busy}
          className="absolute left-1/2 -translate-x-1/2 -top-6 pointer-events-auto bg-primary text-primary-foreground rounded-full w-16 h-16 shadow-lg shadow-primary/30 flex flex-col items-center justify-center font-bold active:scale-95 transition disabled:opacity-60 disabled:active:scale-100"
          aria-label="بيع جديد"
        >
          {busy ? (
            <Loader2 className="w-6 h-6 animate-spin" />
          ) : (
            <>
              <Plus className="w-6 h-6" />
              <span className="text-[11px] -mt-0.5">بيع</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
