// Extracted verbatim from src/routes/_authenticated/app.tsx (R1) — no body changes.
export function EmptyState({ text }: { text: string }) {
  return (
    <div className="rounded-2xl bg-card border border-border p-8 text-center text-sm text-muted-foreground">
      {text}
    </div>
  );
}
