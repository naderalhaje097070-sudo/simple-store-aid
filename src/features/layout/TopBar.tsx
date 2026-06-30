import { ArrowLeft, Home } from "lucide-react";
import type React from "react";

export function TopBar({
  title,
  onBack,
  onHome,
  right,
}: {
  title: string;
  onBack?: () => void;
  onHome?: () => void;
  right?: React.ReactNode;
}) {
  return (
    <div className="sticky top-0 z-30 bg-background/95 backdrop-blur border-b border-border px-4 py-3 flex items-center gap-2">
      {onBack && (
        <button onClick={onBack} aria-label="رجوع" className="p-2 -mr-2 rounded-full hover:bg-muted">
          <ArrowLeft className="w-5 h-5 rotate-180" />
        </button>
      )}
      <h1 className="text-lg font-bold flex-1 truncate">{title}</h1>
      {right}
      {onHome && (
        <button onClick={onHome} aria-label="الرئيسية" className="p-2 rounded-full hover:bg-muted text-muted-foreground">
          <Home className="w-5 h-5" />
        </button>
      )}
    </div>
  );
}
