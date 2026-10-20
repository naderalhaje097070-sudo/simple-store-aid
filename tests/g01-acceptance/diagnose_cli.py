"""Instrument only the exact observed official installer; bound its process group."""
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess

ACTION_SHA = 'afb1b15109756ea5cf9d8985a359d9095235ca2b'
SOURCE_SHA256 = '9ab8da10c0e6ac30dc793094383b973604e95598ccd6c81a05a83a3d1a55cd68'
MARKER = 'G1_CLI_PHASE:'


def instrument(source):
    assert hashlib.sha256(source.encode()).hexdigest() == SOURCE_SHA256, 'official source mismatch'
    replacements = {
        'const output = await $`ldd --version`.quiet().text();':
            'console.log("G1_CLI_PHASE:ldd_begin");\nconst output = await $`ldd --version`.quiet().text();\nconsole.log("G1_CLI_PHASE:ldd_done");',
        'const version = resolveVersion(core.getInput("version"));':
            'const version = resolveVersion(core.getInput("version"));\nconsole.log("G1_CLI_PHASE:resolved_version");',
        'const archive = await getDownloadArchive(version);':
            'console.log("G1_CLI_PHASE:archive_platform_begin");\nconst archive = await getDownloadArchive(version);\nconsole.log("G1_CLI_PHASE:archive_platform_done");',
        'const archivePath = await tc.downloadTool(archive.url);':
            'console.log("G1_CLI_PHASE:download_begin");\nconst archivePath = await tc.downloadTool(archive.url);\nconsole.log("G1_CLI_PHASE:download_done");',
        'const extractedPath =\n': 'console.log("G1_CLI_PHASE:extract_begin");\nconst extractedPath =\n',
        'const cliPath = getCliPath(extractedPath, archive.format);':
            'console.log("G1_CLI_PHASE:extract_done");\nconst cliPath = getCliPath(extractedPath, archive.format);',
        'const installedVersion = await determineInstalledVersion(cliPath);':
            'console.log("G1_CLI_PHASE:version_begin");\nconst installedVersion = await determineInstalledVersion(cliPath);\nconsole.log("G1_CLI_PHASE:version_done");',
        'core.addPath(cliPath);': 'core.addPath(cliPath);\nconsole.log("G1_CLI_PHASE:path_published");',
    }
    for old, new in replacements.items():
        assert source.count(old) == 1, 'instrumentation boundary changed'
        source = source.replace(old, new)
    return source


def main():
    root = Path(os.environ['RUNNER_TEMP'])
    action = Path('.g01-cli-action').resolve()
    assert subprocess.run(['git', '-C', str(action), 'rev-parse', 'HEAD'], capture_output=True,
                          text=True, check=True).stdout.strip() == ACTION_SHA
    path = action/'src/main.ts'
    source = path.read_text(); path.write_text(instrument(source))
    private = root/'g01-cli-installer-private.log'
    timed_out = False
    env = dict(os.environ, INPUT_VERSION='2.101.0', SUPABASE_CLI_GITHUB_TOKEN='')
    try:
        with private.open('wb') as log:
            process = subprocess.Popen(['bun', 'src/main.ts'], cwd=action, env=env,
                                       stdout=log, stderr=log, start_new_session=True)
            try:
                code = process.wait(timeout=120)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL); process.wait(timeout=5)
                # The parent may exit while a descendant ignores TERM.
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                code = 124
    finally:
        path.write_text(source)
    data = private.read_bytes()
    phases = re.findall(rb'G1_CLI_PHASE:([a-z_]+)', data)
    phases = [x.decode('ascii') for x in phases]
    value = {'source_sha': os.environ['EXPECTED_SOURCE'], 'action_sha': ACTION_SHA,
             'official_main_sha256': SOURCE_SHA256, 'cli_version': '2.101.0',
             'bun_version': subprocess.run(['bun', '--version'], capture_output=True,
                                           text=True, check=True).stdout.strip(),
             'phases': phases, 'timed_out': timed_out, 'exit_code': code,
             'private_log_sha256': hashlib.sha256(data).hexdigest(),
             'passed': code == 0 and phases[-1:] == ['path_published']}
    out = root/'g01-evidence'; out.mkdir(exist_ok=True)
    (out/'cli-installer.json').write_text(json.dumps(value, indent=2)+'\n')
    print(json.dumps(value))
    return 0 if value['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
