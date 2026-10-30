const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const ts = require("typescript");
const assert = require("node:assert/strict");
const { webcrypto } = require("node:crypto");

const root = path.resolve(__dirname, "../..");
function memoryStorage() {
  const values = new Map();
  return {
    values,
    getItem(key) {
      return values.get(key) ?? null;
    },
    setItem(key, value) {
      values.set(key, String(value));
    },
    removeItem(key) {
      values.delete(key);
    },
  };
}
function serialLocks() {
  const queues = new Map();
  return {
    request(name, callback) {
      const previous = queues.get(name) ?? Promise.resolve();
      const next = previous.catch(() => {}).then(callback);
      queues.set(name, next);
      return next;
    },
  };
}
function loadApplication({
  client,
  store = memoryStorage(),
  session = memoryStorage(),
  locks = serialLocks(),
  now = () => Date.now(),
  environment = "http://127.0.0.1:54321",
} = {}) {
  const events = [];
  const window = {
    localStorage: store,
    sessionStorage: session,
    dispatchEvent: (event) => {
      events.push(event.type);
      return true;
    },
  };
  class Clock extends Date {
    static now() {
      return now();
    }
  }
  const context = vm.createContext({
    console,
    URL,
    Event,
    AbortSignal,
    crypto: webcrypto,
    window,
    navigator: { locks },
    Date: Clock,
  });
  const cache = new Map(),
    invalidations = [];
  function load(file) {
    file = path.resolve(root, file);
    if (cache.has(file)) return cache.get(file).exports;
    let source = fs.readFileSync(file, "utf8");
    if (file.endsWith("/sale-operation.ts")) {
      assert.equal(source.split("import.meta.env.VITE_SUPABASE_URL").length - 1, 1);
      source = source.replace("import.meta.env.VITE_SUPABASE_URL", JSON.stringify(environment));
    }
    const js = ts.transpileModule(source, {
      fileName: file,
      compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS },
    }).outputText;
    const module = { exports: {} };
    cache.set(file, module);
    const requireLocal = (name) => {
      if (name === "@tanstack/react-query")
        return {
          useQuery: (x) => x,
          useMutation: (x) => x,
          useQueryClient: () => ({ invalidateQueries: (x) => invalidations.push(x) }),
        };
      if (name === "@/integrations/supabase/client") return { supabase: client };
      if (name.startsWith("@/")) return load("src/" + name.slice(2) + ".ts");
      if (name.startsWith("./")) return load(path.resolve(path.dirname(file), name + ".ts"));
      throw Error("Unexpected actual module dependency: " + name);
    };
    const run = vm.runInContext("(function(require,module,exports){" + js + "\n})", context, {
      filename: file,
    });
    run(requireLocal, module, module.exports);
    return module.exports;
  }
  return { load, store, session, events, invalidations };
}
module.exports = { loadApplication, memoryStorage, serialLocks };
