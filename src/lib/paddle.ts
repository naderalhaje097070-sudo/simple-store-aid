import { resolvePaddlePrice } from "@/utils/payments.functions";

const clientToken = import.meta.env.VITE_PAYMENTS_CLIENT_TOKEN;

declare global {
  interface Window {
    Paddle: {
      Environment: { set(environment: "sandbox" | "production"): void };
      Initialize(options: { token: string }): void;
      Checkout: {
        open(options: {
          items: { priceId: string; quantity: number }[];
          customer?: { email: string };
          customData?: Record<string, string>;
          settings: {
            displayMode: "overlay";
            successUrl: string;
            allowLogout: boolean;
            variant: "one-page";
            locale: string;
          };
        }): void;
      };
    };
  }
}

export function getPaddleEnvironment(): "sandbox" | "live" {
  return clientToken?.startsWith("test_") ? "sandbox" : "live";
}

let paddleInitialized = false;

export async function initializePaddle() {
  if (paddleInitialized) return;
  if (!clientToken) throw new Error("VITE_PAYMENTS_CLIENT_TOKEN is not set");
  return new Promise<void>((resolve, reject) => {
    const script = document.createElement("script");
    script.src = "https://cdn.paddle.com/paddle/v2/paddle.js";
    script.onload = () => {
      const paddleJsEnv = getPaddleEnvironment() === "sandbox" ? "sandbox" : "production";
      window.Paddle.Environment.set(paddleJsEnv);
      window.Paddle.Initialize({ token: clientToken });
      paddleInitialized = true;
      resolve();
    };
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

export async function getPaddlePriceId(priceId: string): Promise<string> {
  const environment = getPaddleEnvironment();
  return resolvePaddlePrice({ data: { priceId, environment } });
}
