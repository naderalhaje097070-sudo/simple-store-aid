// Minimal stand-in for @tanstack/react-router: the real AuthPage component runs
// unchanged; navigation is recorded instead of performed.
import type { ReactNode } from "react";
declare global {
  interface Window {
    authNavigations: unknown[];
  }
}
window.authNavigations = [];
export const createFileRoute = () => (options: Record<string, unknown>) => ({
  options,
  useSearch: () => ({}),
});
export const useNavigate = () => (target: unknown) => {
  window.authNavigations.push(target);
};
export const Link = ({ children }: { children: ReactNode }) => <a>{children}</a>;
