import { ArrowLeft } from "lucide-react";
import type React from "react";

export function TopBar({ title, onBack, right }: { title: string; onBack?: () => void; right?: React.ReactNode }) {
  return (
    <div className="sticky top-0 z-30 bg-background/95 backdrop-blur border-b border-border px-4 py-3 flex items-center gap-3">
      {onBack && (
        <button onClick={onBack} className="p-2 -mr-2 rounded-full hover:bg-muted">
          <ArrowLeft className="w-5 h-5 rotate-180" />
        </button>
      )}
      <h1 className="text-lg font-bold flex-1">{title}</h1>
      {right}
    </div>
  );
}
