import { createRoot } from "react-dom/client";
import { Route } from "@/routes/auth";
const AuthPage = (Route as unknown as { options: { component: () => JSX.Element } }).options
  .component;
createRoot(document.getElementById("root")!).render(<AuthPage />);
(window as unknown as { authReady: boolean }).authReady = true;
