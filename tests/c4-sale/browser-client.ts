import type { saleRequest } from "@/lib/sale-operation";
const ACTOR = "11111111-1111-4111-8111-111111111111";
type Request = ReturnType<typeof saleRequest>;
type Reply = { success: true; order_id: string; number: number };
const listeners = new Set<() => void>();
declare global {
  interface Window {
    fixtureSwitch: (actor: string) => void;
  }
}
window.fixtureSwitch = (actor) => {
  sessionStorage.setItem("fixtureActor", actor);
  listeners.forEach((fn) => fn());
};
export const supabase = {
  auth: {
    async getUser() {
      return {
        data: { user: { id: sessionStorage.getItem("fixtureActor") || ACTOR } },
        error: null,
      };
    },
    onAuthStateChange(callback: () => void) {
      listeners.add(callback);
      setTimeout(callback, 0);
      return {
        data: {
          subscription: {
            unsubscribe() {
              listeners.delete(callback);
            },
          },
        },
      };
    },
  },
  rpc(name: string, request: Request) {
    if (name !== "create_sale_with_items_idempotent") throw Error("unexpected fixture RPC");
    return {
      async abortSignal() {
        const calls: Request[] = JSON.parse(localStorage.getItem("fixtureCalls") || "[]");
        calls.push(request);
        localStorage.setItem("fixtureCalls", JSON.stringify(calls));
        const effects: Record<string, Reply> = JSON.parse(
          localStorage.getItem("fixtureEffects") || "{}",
        );
        if (!effects[request.p_idempotency_key])
          effects[request.p_idempotency_key] = {
            success: true,
            order_id: crypto.randomUUID(),
            number: Object.keys(effects).length + 1,
          };
        localStorage.setItem("fixtureEffects", JSON.stringify(effects));
        if ((sessionStorage.getItem("fixtureMode") || "lost") === "lost")
          throw Error("modeled lost reply");
        return { data: effects[request.p_idempotency_key], error: null, status: 200 };
      },
    };
  },
};
