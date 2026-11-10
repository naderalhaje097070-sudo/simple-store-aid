// The real supabase-js client; the test answers its auth requests in the browser.
import { createClient } from "@supabase/supabase-js";
export const supabase = createClient("http://127.0.0.1:54321", "auth-signup-fixture-placeholder", {
  auth: { persistSession: false, autoRefreshToken: false, detectSessionInUrl: false },
});
