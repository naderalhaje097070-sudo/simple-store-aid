#!/bin/bash
# Local emulation of the release-finance restore step (C6/C7 plan 2.2): runs the step's own `run:` text from the
# committed YAML of the tested commit, with the layout the job builds before it: a c5finance-owned clone at
# /tmp/monjez-c5sale/repo, the evidence directory, the test browser build, EXPECTED_SOURCE = the tested commit.
# Not reproduced locally: the iptables firewall and the GitHub runner image.
# usage: run_step_local.sh REPO_WITH_COMMIT COMMIT SOURCE_STACK_WORKDIR NEW_RUNNER_TEMP [NODE_MODULES_DIR]
set -uo pipefail
REPO=$1; SHA=$2; SRC=$3; RT=$4; NM=${5:-}
[ -e "$RT" ] && { echo "RUNNER_TEMP exists: $RT"; exit 2; }
mkdir -p "$RT"; ln -s "$SRC" "$RT/monjez-c5sale-stack"
id c5finance >/dev/null 2>&1 || useradd --system --no-create-home --shell /usr/sbin/nologin c5finance
rm -rf /tmp/monjez-c5sale; install -d -m 711 -o c5finance -g c5finance /tmp/monjez-c5sale
git clone -q --no-checkout "$REPO" /tmp/monjez-c5sale/repo && git -C /tmp/monjez-c5sale/repo checkout -q "$SHA"
git -C /tmp/monjez-c5sale/repo remote set-url origin https://github.com/naderalhaje097070-sudo/simple-store-aid
git -C /tmp/monjez-c5sale/repo fetch -q "$REPO" refs/remotes/origin/main:refs/remotes/origin/main
[ -n "$NM" ] && cp -a "$NM" /tmp/monjez-c5sale/repo/node_modules
[ -d /tmp/monjez-c5sale-browser ] && cp -a /tmp/monjez-c5sale-browser /tmp/monjez-c5sale/browser
install -d -m 700 -o c5finance -g c5finance /tmp/monjez-c5sale/evidence
chown -R c5finance:c5finance /tmp/monjez-c5sale
git -C "$REPO" show "$SHA:.github/workflows/release-finance.yml" | python3 -c "
import yaml, sys
d = yaml.safe_load(sys.stdin)
st = [x for x in d['jobs']['suite']['steps'] if x.get('name', '').startswith('Logical backup and restore')][0]
open(sys.argv[1], 'w').write(st['run'])" "$RT/step.sh"
cd /tmp/monjez-c5sale/repo && env RUNNER_TEMP="$RT" GITHUB_WORKSPACE=/tmp/monjez-c5sale/repo EXPECTED_SOURCE="$SHA" bash "$RT/step.sh"
echo "STEP_EXIT=$?"
