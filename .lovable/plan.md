## Plan: Add Dark Mode to Mongezz

### Goal
Add a fully functional dark mode with a manual toggle, persisted to `localStorage`, without changing any financial or business logic.

---

### Step 1: Extend CSS tokens for dark mode
In `src/styles.css`, add a `.dark` block that redefines all semantic color variables with dark-appropriate OKLCH values:
- `--background`, `--foreground`, `--card`, `--muted`, `--border`, `--input`
- `--primary`, `--primary-soft`, `--debt`, `--warn`, `--success`, `--info`, `--profit` (and their `-soft` variants)
- Keep the same variable names so every component automatically adapts.

### Step 2: Create a theme hook
Create `src/hooks/useTheme.ts`:
- Reads `"mongezz-theme"` from `localStorage` (values: `"light" | "dark"`, default `"light"`).
- On mount, applies `document.documentElement.classList.toggle("dark", isDark)`.
- Exposes `theme`, `setTheme`, and `toggleTheme`.
- Updates the `<meta name="theme-color">` tag dynamically.

### Step 3: Wrap the app with the theme provider
In `src/routes/__root.tsx` (or `src/routes/_authenticated/app.tsx`):
- Call the theme hook so the `dark` class is applied before first paint.
- For authenticated routes, initialize inside the app shell; for the landing page, initialize in `RootComponent` so the landing page also respects the saved preference.

### Step 4: Add toggle in Settings
In `src/features/settings/SettingsScreen.tsx`:
- Add a new card/row with label "الوضع المظلم" and a switch/toggle button.
- Use the `toggleTheme` / `setTheme` from the hook.
- Show current state (مظلم / فاتح).

### Step 5: Fix hardcoded colors that break dark mode
Search and replace specific hardcoded classes that ignore semantic tokens:
- `bg-warn text-white` → use a semantic warn foreground or a dark-aware class.
- `bg-emerald-100 text-emerald-800` and `bg-amber-100 text-amber-800` in `platform-admin.tsx` → map to `--success-soft` / `--warn-soft` with corresponding foregrounds.
- Verify `bg-black/40` and `bg-black/80` overlays look acceptable in dark mode (usually fine).
- Verify `shadow-primary/20` still reads well on dark backgrounds.

### Step 6: Smoke test
- Toggle dark mode in Settings → verify the class is added to `<html>`.
- Refresh the page → verify localStorage preference is restored.
- Check key screens in dark mode: Dashboard, Sale Quick, Inventory, Settings, Auth, Landing page.
- Verify no unreadable text or invisible borders.

### Out of scope
- No DB migration or tenant profile field.
- No system-preference auto-detection.
- No financial logic changes.