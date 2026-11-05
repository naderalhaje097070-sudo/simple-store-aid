import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Route } from "@/routes/_authenticated/app";
import { ready } from "./client";
import "@/styles.css";
const ActualApp = Route.options.component!;
const client = new QueryClient({
  defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
});
ready.then(({ error }) => {
  if (error) throw Error("fixture Auth failed");
  createRoot(document.getElementById("root")!).render(
    <QueryClientProvider client={client}>
      <ActualApp />
    </QueryClientProvider>,
  );
  window.journeyReady = true;
});
