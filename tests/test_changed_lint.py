"""Exercise the actual lint entrypoint in disposable local Git repositories."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
script = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else root / "scripts/lint-changed.sh"
out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
results = []


def command(args, cwd, **kwargs):
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, **kwargs)


with tempfile.TemporaryDirectory(prefix="monjez-lint-") as tmp:
    repo = Path(tmp)
    command(["git", "init", "-q"], repo, check=True)
    command(["git", "config", "user.name", "Synthetic Test"], repo, check=True)
    command(["git", "config", "user.email", "synthetic@example.invalid"], repo, check=True)
    (repo / "README.md").write_text("synthetic fixture\n")

    def commit():
        command(["git", "add", "."], repo, check=True)
        command(["git", "commit", "-qm", "synthetic fixture"], repo, check=True)
        return command(["git", "rev-parse", "HEAD"], repo, check=True).stdout.strip()

    initial = commit()
    bin_dir = repo / "bin"
    bin_dir.mkdir()
    runner = bin_dir / "bunx"
    runner.write_text('#!/usr/bin/env bash\nset -eu\nprintf "%s\\n" "$@" >> "$LINT_FIXTURE_CALLS"\nif [[ "${LINT_FIXTURE_REAL:-0}" == 1 ]]; then\n shift\n exec node "$LINT_FIXTURE_ESLINT" "$@"\nfi\n')
    runner.chmod(0o755)
    calls = repo / "calls.txt"
    env = {**os.environ, "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
           "LINT_FIXTURE_CALLS": str(calls), "LINT_FIXTURE_ESLINT": str(root / "node_modules/eslint/bin/eslint.js")}

    def run(base, real=False):
        calls.unlink(missing_ok=True)
        return command(["bash", str(script)], repo, env={**env, "BASE_SHA": base, "LINT_FIXTURE_REAL": "1" if real else "0"})

    def check(name, fn):
        try:
            fn()
            results.append({"name": name, "passed": True})
        except Exception as error:
            results.append({"name": name, "passed": False, "error": str(error)})

    def invalid():
        r = run("definitely-not-a-commit")
        (out / "invalid-base.txt").write_text(r.stdout + r.stderr)
        assert r.returncode != 0, "git diff failure passed as no changed source"
        assert not calls.exists()

    def no_parent():
        assert run("").returncode != 0

    check("invalid base fails closed", invalid)
    check("missing fallback parent fails closed", no_parent)
    (repo / "README.md").write_text("synthetic documentation change\n")
    docs = commit()

    def no_source():
        r = run(initial)
        assert r.returncode == 0, r.stderr
        assert not calls.exists(), "documentation-only change invoked lint"

    check("valid documentation-only diff succeeds", no_source)
    src = repo / "src"
    src.mkdir()
    names = ["a.ts", "a.tsx", "a.js", "a.jsx", "a.mjs", "a.cjs", "with space.js"]
    for name in names:
        (src / name).write_text("// synthetic\n")
    commit()

    def extensions():
        r = run(docs)
        assert r.returncode == 0, r.stderr
        args = calls.read_text().splitlines()
        assert args[0] == "eslint"
        assert sorted(args[1:]) == sorted("src/" + n for n in names), args

    check("all six extensions and filename spaces survive", extensions)
    # This invokes the actual installed ESLint, not the recording stub.
    (repo / "eslint.config.mjs").write_text('export default [{files:["**/*.js"],rules:{"no-constant-condition":"error"}}];\n')
    (src / "bad.js").write_text("if (true) {}\n")
    good_base = command(["git", "rev-parse", "HEAD"], repo, check=True).stdout.strip()
    commit()

    def actual_lint():
        r = run(good_base, real=True)
        (out / "actual-eslint-failure.txt").write_text(r.stdout + r.stderr)
        assert "no-constant-condition" in r.stdout + r.stderr, r.stderr
        assert r.returncode != 0, "actual lint error passed"

    check("real ESLint failure fails the gate", actual_lint)

(out / "lint-tests.json").write_text(json.dumps({"results": results,
    "passed": sum(x["passed"] for x in results), "total": len(results)}, indent=2))
print(json.dumps(results, indent=2))
if not all(x["passed"] for x in results):
    raise SystemExit(1)
