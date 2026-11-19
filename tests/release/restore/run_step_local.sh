#!/bin/bash
# Local emulation of the release-finance restore step: runs the step's own `run:` text from the YAML.
# $1 = worktree with the workflow, $2 = source stack workdir, $3 = new RUNNER_TEMP
set -uo pipefail
WT=$1; SRC=$2; RT=$3; S=$(dirname "$0")
[ -e "$RT" ] && { echo "RUNNER_TEMP exists: $RT"; exit 2; }
mkdir -p "$RT"; ln -s "$SRC" "$RT/monjez-c5sale-stack"
id c5finance >/dev/null 2>&1 || useradd --system --no-create-home --shell /usr/sbin/nologin c5finance
rm -rf /tmp/monjez-c5sale; install -d -m 711 -o c5finance -g c5finance /tmp/monjez-c5sale
cp -a "$WT/." /tmp/monjez-c5sale/repo; install -d -m 700 -o c5finance -g c5finance /tmp/monjez-c5sale/evidence
chown -R c5finance:c5finance /tmp/monjez-c5sale
python3 - "$WT" "$RT/step.sh" <<'PY'
import yaml, sys
d = yaml.safe_load(open(sys.argv[1] + '/.github/workflows/release-finance.yml'))
st = [x for x in d['jobs']['suite']['steps'] if x.get('name', '').startswith('Logical backup and restore')][0]
open(sys.argv[2], 'w').write(st['run'])
PY
cd "$WT" && env RUNNER_TEMP="$RT" GITHUB_WORKSPACE="$WT" PATH="$S/sbcli/node_modules/.bin:$PATH" bash "$RT/step.sh"
echo "STEP_EXIT=$?"
