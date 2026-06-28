// Extracted verbatim from src/routes/_authenticated/app.tsx (R1) — no body changes.
import * as React from "react";
import { X } from "lucide-react";

export function Sheet({ children, title, onClose }: { children: React.ReactNode; title: string; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40" onClick={onClose}>
      <div onClick={e => e.stopPropagation()} className="w-full max-w-md bg-card rounded-t-3xl p-4 pb-6 max-h-[90vh] overflow-y-auto" dir="rtl">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-bold">{title}</h3>
          <button onClick={onClose} className="p-2 rounded-full hover:bg-muted"><X className="w-5 h-5" /></button>
        </div>
        {children}
      </div>
    </div>
  );
}
