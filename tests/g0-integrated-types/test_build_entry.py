"""Exercise the real build entry with child-process fixtures, without a build."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class BuildEntry(unittest.TestCase):
    def test_failure_gating_and_forwarding(self):
        with tempfile.TemporaryDirectory(prefix="monjez-build-") as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "node_modules/vite/bin").mkdir(parents=True)
            source = Path(__file__).resolve().parents[2] / "scripts/build.mjs"
            shutil.copyfile(source, root / "scripts/build.mjs")
            (root / "node_modules/vite/bin/vite.js").write_text(
                "const fs=require('node:fs');"
                "fs.writeFileSync('vite-args.json',JSON.stringify(process.argv.slice(2)));"
                "process.exit(Number(process.env.FIXTURE_BUILD_STATUS||0));"
            )
            (root / "scripts/format-generated.mjs").write_text(
                "import fs from 'node:fs';fs.writeFileSync('format-ran','yes');"
                "process.exit(Number(process.env.FIXTURE_FORMAT_STATUS||0));"
            )
            for build, formatting, expected, ran in [(7, 0, 7, False), (0, 9, 9, True), (0, 0, 0, True)]:
                with self.subTest(build=build, formatting=formatting):
                    marker = root / "format-ran"
                    marker.unlink(missing_ok=True)
                    env = {**os.environ, "FIXTURE_BUILD_STATUS": str(build),
                           "FIXTURE_FORMAT_STATUS": str(formatting)}
                    result = subprocess.run(
                        ["node", str(root / "scripts/build.mjs"), "--mode", "fixture"],
                        cwd=root, env=env, capture_output=True, timeout=15,
                    )
                    self.assertEqual(result.returncode, expected, result.stderr.decode())
                    self.assertEqual(marker.exists(), ran)
                    self.assertEqual(json.loads((root / "vite-args.json").read_text()),
                                     ["build", "--mode", "fixture"])


if __name__ == "__main__":
    unittest.main()
