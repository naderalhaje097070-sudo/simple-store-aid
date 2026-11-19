#!/bin/bash
# Local emulation of the release-finance restore step (C6/C7 plan 2.2): runs the step's own `run:` text from the
# committed YAML of the tested commit, with the layout the job builds before it: a c5finance-owned clone at
# /tmp/monjez-c5sale/repo, the evidence directory, the test browser build, EXPECTED_SOURCE = the tested commit.
# Not reproduced locally: the iptables firewall and the GitHub runner image.
# Exit status (review fix #98, Graphify P2): any setup or step-extraction failure stops here with a nonzero status
# before the step runs; otherwise the helper exits with the step's own status (also printed as STEP_EXIT=).
# usage: run_step_local.sh REPO_WITH_COMMIT COMMIT SOURCE_STACK_WORKDIR NEW_RUNNER_TEMP [NODE_MODULES_DIR]
set -euo pipefail
[ $# -ge 4 ] || { echo "usage: $0 REPO COMMIT SOURCE_STACK_WORKDIR NEW_RUNNER_TEMP [NODE_MODULES_DIR]" >&2; exit 2; }
REPO=$1; SHA=$2; SRC=$3; RT=$4; NM=${5:-}
[ -e "$RT" ] && { echo "RUNNER_TEMP exists: $RT" >&2; exit 2; }
SHA=$(git -C "$REPO" rev-parse --verify --quiet "$SHA^{commit}") || { echo "SETUP_FAILED: not a commit in $REPO: $2" >&2; exit 2; }
mkdir -p "$RT"; ln -s "$SRC" "$RT/monjez-c5sale-stack"
id c5finance >/dev/null 2>&1 || useradd --system --no-create-home --shell /usr/sbin/nologin c5finance
rm -rf /tmp/monjez-c5sale; install -d -m 711 -o c5finance -g c5finance /tmp/monjez-c5sale
git clone -q --no-checkout "$REPO" /tmp/monjez-c5sale/repo
git -C /tmp/monjez-c5sale/repo checkout -q "$SHA"
git -C /tmp/monjez-c5sale/repo remote set-url origin https://github.com/naderalhaje097070-sudo/simple-store-aid
git -C /tmp/monjez-c5sale/repo fetch -q "$REPO" refs/remotes/origin/main:refs/remotes/origin/main
if [ -n "$NM" ]; then cp -a "$NM" /tmp/monjez-c5sale/repo/node_modules; fi
if [ -d /tmp/monjez-c5sale-browser ]; then cp -a /tmp/monjez-c5sale-browser /tmp/monjez-c5sale/browser; fi
install -d -m 700 -o c5finance -g c5finance /tmp/monjez-c5sale/evidence
chown -R c5finance:c5finance /tmp/monjez-c5sale
git -C "$REPO" show "$SHA:.github/workflows/release-finance.yml" | python3 -c "
import yaml, sys
d = yaml.safe_load(sys.stdin)
st = [x for x in d['jobs']['suite']['steps'] if x.get('name', '').startswith('Logical backup and restore')]
if len(st) != 1 or not str(st[0].get('run') or '').strip():
    sys.exit('STEP_EXTRACTION_FAILED: expected exactly one non-empty restore step, found %d' % len(st))
open(sys.argv[1], 'w').write(st[0]['run'])" "$RT/step.sh"
rc=0
(cd /tmp/monjez-c5sale/repo && env RUNNER_TEMP="$RT" GITHUB_WORKSPACE=/tmp/monjez-c5sale/repo EXPECTED_SOURCE="$SHA" bash "$RT/step.sh") || rc=$?
echo "STEP_EXIT=$rc"
exit "$rc"
