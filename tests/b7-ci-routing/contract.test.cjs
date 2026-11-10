const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");
const { test } = require("node:test");
const yaml = require("js-yaml");

const ROOT = path.resolve(__dirname, "../..");
const HEAD = "${{ github.event.pull_request.head.sha || github.sha }}";
const INTEGRATION = "integration/g0-g1-reconcile-2026-10-18";
const INTEGRATION_PR_CHECKS = [
  "b1-composition.yml",
  "integration-verification.yml",
  "release-finance.yml",
];
const CURRENT = [
  "b5-lifecycle.yml",
  "b1-composition.yml",
  "integration-verification.yml",
  "b-dep-verify.yml",
  "b50-natural-expiry.yml",
];
// Release acceptance: required checks for PRs into main.
const RELEASE = ["release-finance.yml", "release-gate-trusted.yml"];
// Required check names (docs/RELEASE_GATE_SETTINGS.md): each must be produced by
// exactly one job across all workflows, so no PR-added job can satisfy it.
const REQUIRED_CHECK_NAMES = ["trusted-release-gate", "integrated-quality"];
const HISTORICAL = [
  "account-lifecycle-baseline.yml",
  "account-lifecycle-correction.yml",
  "mcp-lifecycle-probe.yml",
  "mcp-tanstack-route.yml",
  "owner-retention-catalog.yml",
  "auth-natural-expiry.yml",
  "oc-app.yml",
];
const GENERAL = [
  "quality.yml",
  "mcp-issuer-contract.yml",
  "sec-ci-gate4-probe.yml",
  "sec-env-gate4-probe.yml",
  "ephemeral-financial-rules.yml",
  "isolated-auth-smoke.yml",
];
const IMPACT = [
  "src/**",
  "config/**",
  "scripts/**",
  "tests/**",
  "supabase/migrations/**",
  "package.json",
  "bun.lock",
  "vite.config.ts",
  "tsconfig.json",
  ".github/workflows/**",
];
function documents() {
  return Object.fromEntries(
    [...CURRENT, ...RELEASE, ...HISTORICAL, ...GENERAL].map((name) => [
      name,
      yaml.load(readFileSync(path.join(ROOT, ".github/workflows", name), "utf8")),
    ]),
  );
}
function validate(docs) {
  for (const name of CURRENT) {
    const doc = docs[name];
    assert.deepEqual(doc.permissions, { contents: "read" }, name);
    assert.deepEqual(
      doc.on.pull_request.branches,
      INTEGRATION_PR_CHECKS.includes(name) ? ["main", INTEGRATION] : ["main"],
      name,
    );
    if (INTEGRATION_PR_CHECKS.includes(name))
      assert.equal(
        doc.on.pull_request.paths,
        undefined,
        name + " must not filter required PR checks",
      );
    assert.deepEqual(doc.on.pull_request.types, ["opened", "synchronize", "reopened"], name);
    // Coverage rule: no path filter means every PR runs (full coverage). A path
    // filter is allowed only if it still includes every impact path, and
    // paths-ignore is never allowed, since it silently narrows acceptance.
    assert.equal(doc.on.pull_request["paths-ignore"], undefined, name + " must not ignore paths");
    if (doc.on.pull_request.paths !== undefined) {
      for (const impact of IMPACT)
        assert.ok(doc.on.pull_request.paths.includes(impact), name + impact);
      for (const entry of doc.on.pull_request.paths)
        assert.ok(!String(entry).startsWith("!"), name + " must not negate paths: " + entry);
    }
    for (const job of Object.values(doc.jobs)) {
      assert.equal(job["continue-on-error"], undefined, name);
      assert.equal(job.if, undefined, name + " must not skip current acceptance");
      if (job.strategy && "fail-fast" in job.strategy)
        assert.equal(typeof job.strategy["fail-fast"], "boolean");
      if (job.env?.EXPECTED_SOURCE) assert.equal(job.env.EXPECTED_SOURCE, HEAD, name);
      let applicationCheckouts = 0;
      for (const step of job.steps) {
        assert.equal(step["continue-on-error"], undefined, name);
        if (!step.uses?.startsWith("actions/checkout@")) continue;
        if (step.with?.repository) {
          assert.equal(step.with.repository, "supabase/setup-cli", name);
          continue;
        }
        applicationCheckouts++;
        assert.equal(step.with.ref, HEAD, name);
        assert.equal(step.with["fetch-depth"], 0, name);
        assert.ok(
          step.with["persist-credentials"] === false ||
            step.with["persist-credentials"] === "false",
          name,
        );
      }
      assert.equal(applicationCheckouts, 1, name);
    }
  }
  validateRelease(docs);
  const natural = docs["b50-natural-expiry.yml"].jobs["natural-expiry-b50"];
  assert.ok(natural.steps.some((s) => s.run?.includes("python tests/b50-natural-expiry/probe.py")));
  assert.ok(natural.steps.some((s) => s.run?.includes("python tests/b5-lifecycle/inventory.py")));
  for (const name of HISTORICAL) {
    const doc = docs[name];
    assert.match(doc.name, /^Historical (41|43|45) - /);
    assert.deepEqual(Object.keys(doc.on), ["workflow_dispatch"], name);
    assert.equal(doc.on.workflow_dispatch.inputs.historical_source.required, true, name);
    assert.equal(doc.on.workflow_dispatch.inputs.historical_source.type, "string", name);
    for (const job of Object.values(doc.jobs)) {
      assert.match(job.name, /^Historical (41|43|45) - /, name);
      assert.ok(job.name.includes("${{ inputs.historical_source }}"), name);
      assert.ok(job.steps[0].run.includes("re.fullmatch('[0-9a-f]{40}',source)"), name);
      if (job.env?.EXPECTED_SOURCE)
        assert.equal(job.env.EXPECTED_SOURCE, "${{ inputs.historical_source }}", name);
      assert.ok(
        job.steps.some(
          (step) =>
            step.name === "Verify historical checkout and phase inventory before credentials" &&
            step.run.includes("source==os.environ['HISTORICAL_SOURCE']") &&
            /assert len\(files\)==(?:41|43|45)/.test(step.run),
        ),
        name,
      );
      for (const step of job.steps.filter(
        (s) => s.uses?.startsWith("actions/checkout@") && !s.with?.repository,
      ))
        assert.equal(step.with.ref, "${{ inputs.historical_source }}", name);
    }
  }
  for (const name of GENERAL)
    assert.ok(
      Object.prototype.hasOwnProperty.call(docs[name].on, "pull_request"),
      name + " remains an automatic general gate",
    );
}

function noSkips(name, doc) {
  for (const job of Object.values(doc.jobs)) {
    assert.equal(job["continue-on-error"], undefined, name);
    assert.equal(job.if, undefined, name + " must not skip release acceptance");
    if (job.strategy && "fail-fast" in job.strategy)
      assert.equal(typeof job.strategy["fail-fast"], "boolean", name);
    for (const step of job.steps) assert.equal(step["continue-on-error"], undefined, name);
  }
}
function validateRelease(docs) {
  const finance = docs["release-finance.yml"];
  assert.deepEqual(finance.permissions, { contents: "read" });
  assert.deepEqual(finance.on.pull_request.branches, ["main", INTEGRATION]);
  for (const event of ["push", "pull_request"])
    for (const filter of ["paths", "paths-ignore"])
      assert.equal(finance.on[event][filter], undefined, "release-finance " + event + " " + filter);
  noSkips("release-finance.yml", finance);
  const suite = finance.jobs.suite;
  assert.equal(suite.env.EXPECTED_SOURCE, "${{ github.sha }}");
  assert.ok(suite.steps.some((s) => s.run?.includes("python tests/release/gate.py")));
  assert.ok(suite.steps.some((s) => s.name === "Required controls actually executed and passed"));

  const trusted = docs["release-gate-trusted.yml"];
  assert.deepEqual(Object.keys(trusted.on), ["pull_request_target"]);
  assert.deepEqual(trusted.on.pull_request_target.branches, ["main"]);
  assert.deepEqual(trusted.permissions, {
    contents: "read",
    issues: "read",
    "pull-requests": "read",
  });
  noSkips("release-gate-trusted.yml", trusted);
  const gateJob = trusted.jobs.gate;
  assert.equal(gateJob.name, "trusted-release-gate");
  const checkouts = gateJob.steps.filter((s) => s.uses?.startsWith("actions/checkout@"));
  assert.equal(checkouts.length, 1);
  assert.equal(checkouts[0].with.ref, "${{ github.event.pull_request.base.sha }}");
  assert.equal(checkouts[0].with["persist-credentials"], false);
  for (const step of gateJob.steps) {
    assert.ok(!JSON.stringify(step).includes("pull_request.head.ref"), "no PR branch checkout");
    assert.ok(!/\b(npm|bun|pip|node)\b/.test(step.run ?? ""), "trusted gate runs no PR code");
  }
  assert.ok(gateJob.steps.some((s) => s.run?.includes("--mode objects --governance")));
}
function checkNames() {
  const counts = {};
  const dir = path.join(ROOT, ".github/workflows");
  for (const file of require("node:fs")
    .readdirSync(dir)
    .filter((f) => /\.ya?ml$/.test(f))) {
    const doc = yaml.load(readFileSync(path.join(dir, file), "utf8"));
    for (const [id, job] of Object.entries(doc?.jobs ?? {})) {
      const name = typeof job.name === "string" ? job.name : id;
      counts[name] = (counts[name] ?? 0) + 1;
    }
  }
  return counts;
}

test("actual current head routing and explicit historical source boundaries", () =>
  validate(documents()));
test("missing current B5 PR event is rejected", () => {
  const docs = documents();
  delete docs["b5-lifecycle.yml"].on.pull_request;
  assert.throws(() => validate(docs));
});
test("synthetic merge checkout cannot masquerade as actual PR head", () => {
  const docs = documents();
  docs["b1-composition.yml"].jobs.compatibility.steps.find((s) =>
    s.uses?.startsWith("actions/checkout@"),
  ).with.ref = "${{ github.sha }}";
  assert.throws(() => validate(docs));
});
test("current acceptance cannot ignore failure or skip on PR number", () => {
  for (const mutation of ["continue-on-error", "if"]) {
    const docs = documents();
    docs["b5-lifecycle.yml"].jobs.ssr[mutation] =
      mutation === "if" ? "github.event.pull_request.number != 71" : true;
    assert.throws(() => validate(docs));
  }
});
test("historical automatic event and unbound checkout are rejected", () => {
  const docs = documents();
  docs["owner-retention-catalog.yml"].on.pull_request = {};
  assert.throws(() => validate(docs));
  const other = documents();
  other["owner-retention-catalog.yml"].jobs.catalog.steps.find((s) =>
    s.uses?.startsWith("actions/checkout@"),
  ).with.ref = "main";
  assert.throws(() => validate(other));
});
test("natural real expiry cannot point back at the phase43 runner", () => {
  const docs = documents();
  const step = docs["b50-natural-expiry.yml"].jobs["natural-expiry-b50"].steps.find((s) =>
    s.run?.includes("tests/b50-natural-expiry/probe.py"),
  );
  step.run = step.run.replace(
    "tests/b50-natural-expiry/probe.py",
    "tests/account-lifecycle/natural_expiry_probe.py",
  );
  assert.throws(() => validate(docs));
});
test("general security and financial gates cannot silently lose PR execution", () => {
  for (const name of GENERAL) {
    const docs = documents();
    delete docs[name].on.pull_request;
    assert.throws(() => validate(docs));
  }
});
test("actual historical validator accepts only explicit full hexadecimal commit", () => {
  const step = documents()["owner-retention-catalog.yml"].jobs.catalog.steps[0];
  for (const [source, accepted] of [
    ["a".repeat(40), true],
    ["main", false],
    ["a".repeat(39), false],
    ["a".repeat(41), false],
    ["$(touch /tmp/forbidden-b7-shell-execution)", false],
  ]) {
    const result = spawnSync("bash", ["-e", "-o", "pipefail", "-c", step.run], {
      env: {
        PATH: process.env.PATH,
        HISTORICAL_SOURCE: source,
        HISTORICAL_ROUTING_SOURCE: "b".repeat(40),
      },
      encoding: "utf8",
    });
    assert.equal(result.status === 0, accepted);
  }
});

test("quoted strategy boolean and ignored acceptance step are rejected", () => {
  const docs = documents();
  docs["b5-lifecycle.yml"].jobs.lifecycle.strategy["fail-fast"] = "false";
  assert.throws(() => validate(docs));
  const other = documents();
  other["b5-lifecycle.yml"].jobs.ssr.steps[0]["continue-on-error"] = true;
  assert.throws(() => validate(other));
});
test("historical phase preflight cannot disappear before local credentials", () => {
  const docs = documents();
  docs["owner-retention-catalog.yml"].jobs.catalog.steps = docs[
    "owner-retention-catalog.yml"
  ].jobs.catalog.steps.filter(
    (step) => step.name !== "Verify historical checkout and phase inventory before credentials",
  );
  assert.throws(() => validate(docs));
});

test("historical manual jobs cannot retain a current check-context name", () => {
  const docs = documents();
  docs["owner-retention-catalog.yml"].jobs.catalog.name = "catalog";
  assert.throws(() => validate(docs));
});
test("current PR acceptance may run unfiltered but never narrowed", () => {
  const unfiltered = documents();
  delete unfiltered["b5-lifecycle.yml"].on.pull_request.paths;
  validate(unfiltered);
  const narrowed = documents();
  narrowed["b5-lifecycle.yml"].on.pull_request.paths = IMPACT.filter(
    (impact) => impact !== "supabase/migrations/**",
  );
  assert.throws(() => validate(narrowed), /supabase\/migrations/);
  const ignored = documents();
  ignored["b5-lifecycle.yml"].on.pull_request["paths-ignore"] = ["supabase/**"];
  assert.throws(() => validate(ignored), /must not ignore paths/);
});
test("negated path filter cannot narrow current acceptance", () => {
  const docs = documents();
  docs["b5-lifecycle.yml"].on.pull_request.paths = [...IMPACT, "!supabase/migrations/**"];
  assert.throws(() => validate(docs), /must not negate/);
});
test("release workflows cannot be filtered, skipped or given PR checkout", () => {
  const mutations = [
    (d) => (d["release-finance.yml"].on.pull_request.paths = ["src/**"]),
    (d) => (d["release-finance.yml"].jobs.suite.if = "false"),
    (d) => (d["release-finance.yml"].jobs.suite.steps[1]["continue-on-error"] = true),
    (d) => (d["release-gate-trusted.yml"].permissions["contents"] = "write"),
    (d) =>
      (d["release-gate-trusted.yml"].jobs.gate.steps[0].with.ref =
        "${{ github.event.pull_request.head.sha }}"),
    (d) => (d["release-gate-trusted.yml"].jobs.gate.name = "gate"),
    (d) => (d["release-gate-trusted.yml"].on.pull_request = {}),
  ];
  for (const mutate of mutations) {
    const docs = documents();
    mutate(docs);
    assert.throws(() => validate(docs));
  }
});
test("required check names are produced by exactly one job", () => {
  const counts = checkNames();
  for (const name of REQUIRED_CHECK_NAMES) assert.equal(counts[name], 1, name);
});

// Integration branch-protection preparation: required checks must exist on every PR.
test("integration PR target cannot be removed from the three required workflows", () => {
  for (const name of INTEGRATION_PR_CHECKS) {
    const docs = documents();
    docs[name].on.pull_request.branches = ["main"];
    assert.throws(() => validate(docs), name);
  }
});
test("required integration PR workflows cannot introduce path filters", () => {
  for (const name of INTEGRATION_PR_CHECKS) {
    const docs = documents();
    docs[name].on.pull_request.paths = ["src/**"];
    assert.throws(() => validate(docs), name);
  }
});
