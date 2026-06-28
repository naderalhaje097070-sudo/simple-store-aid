// Extracted verbatim from src/routes/_authenticated/app.tsx (R1) — no body changes.
export function Toast({ text, kind = "info" }: { text: string; kind?: "info" | "warn" | "success" }) {
  const colors = { info: "bg-foreground text-background", warn: "bg-warn text-white", success: "bg-success text-white" };
  return (
    <div className="fixed bottom-28 inset-x-0 z-50 flex justify-center pointer-events-none">
      <div className={`px-4 py-2 rounded-full text-sm font-bold shadow-lg ${colors[kind]}`}>{text}</div>
    </div>
  );
}
