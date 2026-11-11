"""Negative and positive controls for the release gate, on throwaway git repos."""
from contextlib import redirect_stdout
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate  # noqa: E402

M = 'supabase/migrations/'
REMOTE = f'https://github.com/{gate.REPOSITORY}.git'


def run(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True).stdout.decode().strip()


class Repo:
    """origin/main with two migrations; tests then commit candidate changes on HEAD."""

    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        run(self.root, 'init', '-q', '-b', 'main')
        run(self.root, 'config', 'user.email', 'gate@test')
        run(self.root, 'config', 'user.name', 'gate')
        run(self.root, 'remote', 'add', 'origin', REMOTE)
        self.write(M + '20261001000000_a.sql', 'select 1;\n')
        self.write(M + '20261021000000_b.sql', 'select 2;\n')
        self.commit('base')
        run(self.root, 'update-ref', 'refs/remotes/origin/main', 'HEAD')
        run(self.root, 'checkout', '-q', '-b', 'candidate')

    def write(self, path, text):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    def commit(self, message):
        run(self.root, 'add', '-A')
        run(self.root, 'commit', '-q', '-m', message)
        return run(self.root, 'rev-parse', 'HEAD')

    def verify(self, **kw):
        head = run(self.root, 'rev-parse', 'HEAD')
        kw.setdefault('expected', head)
        return gate.verify(self.root, **kw)


class GateTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.tmp.cleanup)

    def assertRejects(self, message, **kw):
        with self.assertRaises(gate.GateFailure) as ctx:
            self.repo.verify(**kw)
        self.assertIn(message, str(ctx.exception))

    # positive controls
    def test_new_migration_in_order_passes(self):
        self.repo.write(M + '20261101000000_c.sql', 'select 3;\n')
        self.repo.commit('c')
        receipt = self.repo.verify()
        self.assertEqual(receipt['migration_count'], 3)
        self.assertIn(M + '20261101000000_c.sql', receipt['review_sensitive_paths'])

    def test_unchanged_candidate_passes_in_objects_mode(self):
        self.repo.write('src/app.ts', 'x\n')
        self.repo.commit('code')
        self.assertEqual(self.repo.verify(mode='objects')['changed_file_count'], 1)

    def test_pinned_legacy_order_file_passes(self):
        self.repo.write(M + '20260815000000_old.sql', 'select 0;\n')
        sha = self.repo.commit('legacy')
        blob = run(self.repo.root, 'rev-parse', sha + ':' + M + '20260815000000_old.sql')
        legacy = {M + '20260815000000_old.sql': blob}
        self.assertEqual(gate.verify_migrations(self.repo.root, 'HEAD', 'origin/main', legacy)[0], '20260815000000')

    # negative controls: migrations
    def test_edited_base_migration_rejected(self):
        self.repo.write(M + '20261001000000_a.sql', 'select 1; -- edited\n')
        self.repo.commit('edit')
        self.assertRejects('Base migration changed')

    def test_deleted_base_migration_rejected(self):
        (self.repo.root / M / '20261001000000_a.sql').unlink()
        self.repo.commit('delete')
        self.assertRejects('Base migration removed or renamed')

    def test_renamed_base_migration_rejected(self):
        run(self.repo.root, 'mv', M + '20261001000000_a.sql', M + '20261001000000_renamed.sql')
        self.repo.commit('rename')
        self.assertRejects('Base migration removed or renamed')

    def test_new_migration_out_of_order_rejected(self):
        self.repo.write(M + '20261010000000_late.sql', 'select 9;\n')
        self.repo.commit('late')
        self.assertRejects('New migration out of order')

    def test_legacy_name_with_other_bytes_rejected(self):
        self.repo.write(M + '20260815000000_old.sql', 'select 0;\n')
        self.repo.commit('legacy')
        legacy = {M + '20260815000000_old.sql': '0' * 40}
        with self.assertRaises(gate.GateFailure) as ctx:
            gate.verify_migrations(self.repo.root, 'HEAD', 'origin/main', legacy)
        self.assertIn('New migration out of order', str(ctx.exception))

    def test_duplicate_version_rejected(self):
        self.repo.write(M + '20261101000000_c.sql', 'select 3;\n')
        self.repo.write(M + '20261101000000_d.sql', 'select 4;\n')
        self.repo.commit('dup')
        self.assertRejects('Duplicate migration version')

    def test_bad_migration_name_rejected(self):
        self.repo.write(M + 'latest.sql', 'select 5;\n')
        self.repo.commit('name')
        self.assertRejects('Invalid migration name')

    def test_executable_migration_rejected(self):
        self.repo.write(M + '20261101000000_c.sql', 'select 3;\n')
        (self.repo.root / M / '20261101000000_c.sql').chmod(0o755)
        self.repo.commit('mode')
        self.assertRejects('Invalid migration mode')

    def test_far_future_migration_rejected(self):
        self.repo.write(M + '20991231000000_future.sql', 'select 9;\n')
        self.repo.commit('future')
        self.assertRejects('timestamp in the future')

    def test_impossible_timestamp_rejected(self):
        self.repo.write(M + '20261399000000_bad.sql', 'select 9;\n')
        self.repo.commit('bad date')
        self.assertRejects('Invalid migration timestamp')

    def test_near_future_slack_is_bounded(self):
        self.repo.write(M + '20261107000000_c.sql', 'select 3;\n')
        self.repo.commit('c')
        now = datetime(2026, 11, 6, tzinfo=timezone.utc)
        self.assertEqual(len(gate.verify_migrations(self.repo.root, now=now)), 3)
        with self.assertRaises(gate.GateFailure):
            gate.verify_migrations(self.repo.root, now=datetime(2026, 11, 1, tzinfo=timezone.utc))

    # negative controls: identity and checkout
    def test_expected_source_mismatch_rejected(self):
        self.assertRejects('Tested commit differs', expected='0' * 40)

    def test_missing_expected_source_rejected(self):
        self.assertRejects('EXPECTED_SOURCE required', expected='')

    def test_dirty_checkout_rejected(self):
        self.repo.write('src/app.ts', 'uncommitted\n')
        self.assertRejects('Checkout not clean')

    def test_uncommitted_migration_rejected(self):
        self.repo.write(M + '20261101000000_c.sql', 'select 3;\n')
        self.assertRejects('Checkout not clean')

    def test_wrong_repository_rejected(self):
        run(self.repo.root, 'remote', 'set-url', 'origin', 'https://github.com/someone/fork.git')
        self.assertRejects('Repository mismatch')

    def test_missing_migration_directory_is_a_gate_failure(self):
        run(self.repo.root, 'rm', '-q', '-r', M)
        self.repo.commit('no migrations')
        self.assertRejects('Migration directory missing')
        self.assertRejects('Base migration removed', mode='objects')

    def test_missing_base_rejected(self):
        run(self.repo.root, 'update-ref', '-d', 'refs/remotes/origin/main')
        self.assertRejects('Base reference unavailable')


def event(kind, label, login='owner', app=None, ts='2026-11-06T10:00:00Z', eid=1, user_type='User'):
    return {'id': eid, 'event': kind, 'label': {'name': label}, 'created_at': ts,
            'actor': {'login': login, 'type': user_type}, 'performed_via_github_app': app}


class GovernanceTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.tmp.cleanup)

    def blocked(self, path, text='x\n'):
        self.repo.write(path, text)
        self.repo.commit('change ' + path)
        with self.assertRaises(gate.GateFailure) as ctx:
            gate.verify_governance(self.repo.root, 'origin/main', 'HEAD', False)
        self.assertIn(path, str(ctx.exception))

    def test_ordinary_change_needs_no_approval(self):
        self.repo.write('src/app.ts', 'x\n')
        self.repo.write('docs/note.md', 'x\n')
        self.repo.write('README.md', 'x\n')
        self.repo.write('public/logo.svg', 'x\n')
        self.repo.commit('product')
        self.assertEqual(gate.verify_governance(self.repo.root, 'origin/main', 'HEAD', False), [])

    def test_workflow_change_blocked_without_approval(self):
        self.blocked('.github/workflows/release-finance.yml', 'jobs: {}\n')

    def test_suite_entrypoint_change_blocked_without_approval(self):
        self.blocked('tests/c4-sale/native.py', 'print(1)\n')

    def test_gate_change_blocked_without_approval(self):
        self.blocked('tests/release/gate.py', 'pass\n')

    # review finding 1: shared helpers, shadowing packages, dependencies, configs
    def test_shared_helper_blocked(self):
        self.blocked('tests/account-lifecycle/live_probe.py', 'class Probe: pass\n')

    def test_shadowing_package_blocked(self):
        self.blocked('tests/c5-journey/profit_contract/__init__.py', 'def run(*a): pass\n')

    def test_new_unknown_top_level_file_blocked(self):
        self.blocked('sitecustomize.py', 'import os\n')

    def test_dependency_and_build_config_blocked(self):
        for path in ('package.json', 'bun.lock', 'vite.config.ts', '.npmrc', 'scripts/build.mjs',
                     'supabase/config.toml', 'supabase/seed.sql', '.github/actions/x/action.yml'):
            with self.subTest(path=path):
                self.assertTrue(gate.governed(path))

    # financial core inside the product
    def test_new_migration_needs_approval(self):
        self.blocked(M + '20261101000000_c.sql', 'select 3;\n')

    def test_financial_core_files_need_approval(self):
        for path in ('src/lib/db.ts', 'src/lib/sale-operation.ts', 'src/lib/collection-operation.ts',
                     'src/domain/finance/quantity.ts', 'src/lib/account-state.server.ts',
                     'src/integrations/supabase/auth-middleware.ts', 'src/integrations/supabase/client.server.ts',
                     'src/lib/paddle.server.ts', 'src/lib/subscription-webhook.server.ts',
                     'src/routes/api/public/payments/webhook.ts', 'src/utils/payments.functions.ts'):
            with self.subTest(path=path):
                self.assertTrue(gate.financial_core(path))

    def test_ordinary_ui_and_display_stay_free(self):
        for path in ('src/features/reports/ProfitScreen.tsx', 'src/lib/day-close-report.ts', 'src/lib/paddle.ts',
                     'src/integrations/supabase/client.ts', 'src/integrations/supabase/types.ts',
                     'src/routes/index.tsx'):
            with self.subTest(path=path):
                self.assertFalse(gate.financial_core(path) or gate.governed(path))

    def test_new_file_reaching_service_role_needs_approval(self):
        self.blocked('src/routes/api/admin/new.ts', 'createClient(url, process.env.SUPABASE_SERVICE_ROLE_KEY)\n')

    def test_ordinary_src_change_still_free_with_core_rules(self):
        self.repo.write('src/features/reports/ProfitScreen.tsx', 'export {}\n')
        self.repo.commit('ui')
        self.assertEqual(gate.verify_governance(self.repo.root, 'origin/main', 'HEAD', False), [])

    def test_rename_of_governed_file_out_of_scope_is_seen(self):
        self.repo.write('tests/release/helper.py', 'x = 1\n')
        self.repo.commit('helper')
        run(self.repo.root, 'update-ref', 'refs/remotes/origin/main', 'HEAD')
        (self.repo.root / 'src').mkdir()
        run(self.repo.root, 'mv', 'tests/release/helper.py', 'src/helper.py')
        self.repo.commit('move out')
        # Default rename detection would list only the new, ungoverned name.
        self.assertEqual(run(self.repo.root, 'diff', '-M', '--name-only', 'origin/main...HEAD'), 'src/helper.py')
        changed = gate.governance_changes(self.repo.root, 'origin/main', 'HEAD')
        self.assertEqual(changed, ['tests/release/helper.py'])

    def test_approved_change_passes_and_is_listed(self):
        self.repo.write('.github/workflows/release-finance.yml', 'jobs: {}\n')
        self.repo.commit('reviewed')
        self.assertEqual(gate.verify_governance(self.repo.root, 'origin/main', 'HEAD', True),
                         ['.github/workflows/release-finance.yml'])


class ApprovalTests(unittest.TestCase):
    SHA = 'a' * 40
    LABEL = gate.approval_label(SHA)

    def test_label_is_bound_to_full_sha(self):
        self.assertEqual(self.LABEL, 'gov-ok-' + self.SHA)
        self.assertLessEqual(len(self.LABEL), 50)  # GitHub label name limit
        with self.assertRaises(gate.GateFailure):
            gate.approval_label('abc')

    def test_owner_direct_label_approves(self):
        self.assertTrue(gate.owner_approved([event('labeled', self.LABEL)], self.LABEL, 'owner'))

    def test_label_for_previous_commit_does_not_approve(self):
        old = gate.approval_label('b' * 40)
        self.assertFalse(gate.owner_approved([event('labeled', old)], self.LABEL, 'owner'))

    def test_label_added_through_an_app_rejected(self):
        app = {'slug': 'claude', 'id': 1}
        self.assertFalse(gate.owner_approved([event('labeled', self.LABEL, app=app)], self.LABEL, 'owner'))

    def test_label_by_other_account_or_bot_rejected(self):
        self.assertFalse(gate.owner_approved([event('labeled', self.LABEL, login='someone')], self.LABEL, 'owner'))
        self.assertFalse(gate.owner_approved([event('labeled', self.LABEL, user_type='Bot')], self.LABEL, 'owner'))

    def test_removed_label_does_not_approve(self):
        events = [event('labeled', self.LABEL, eid=1),
                  event('unlabeled', self.LABEL, ts='2026-11-06T11:00:00Z', eid=2)]
        self.assertFalse(gate.owner_approved(events, self.LABEL, 'owner'))

    def test_latest_event_decides(self):
        events = [event('labeled', self.LABEL, app={'slug': 'x'}, eid=1),
                  event('unlabeled', self.LABEL, ts='2026-11-06T11:00:00Z', eid=2),
                  event('labeled', self.LABEL, ts='2026-11-06T12:00:00Z', eid=3)]
        self.assertTrue(gate.owner_approved(events, self.LABEL, 'owner'))

    def test_event_without_app_field_fails_closed(self):
        e = event('labeled', self.LABEL)
        del e['performed_via_github_app']
        with self.assertRaises(gate.GateFailure):
            gate.owner_approved([e], self.LABEL, 'owner')

    def test_no_events_no_approval(self):
        self.assertFalse(gate.owner_approved([], self.LABEL, 'owner'))


class CliTests(unittest.TestCase):
    """End to end through main(), objects mode, as the trusted workflow calls it."""

    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.tmp.cleanup)
        self.events = self.repo.root.parent / (self.repo.root.name + '-events.json')
        self.addCleanup(lambda: self.events.unlink(missing_ok=True))

    def cli(self, events):
        self.events.write_text(json.dumps(events))
        head = run(self.repo.root, 'rev-parse', 'HEAD')
        out = io.StringIO()
        with redirect_stdout(out), unittest.mock.patch.dict(os.environ, {'EXPECTED_SOURCE': head}):
            code = gate.main(['--root', str(self.repo.root), '--mode', 'objects', '--head', head,
                              '--governance', '--approval-events', str(self.events), '--owner', 'owner'])
        return code, out.getvalue(), head

    def test_governed_change_needs_label_for_this_head(self):
        self.repo.write('tests/helper.py', 'x\n')
        head = self.repo.commit('helper')
        code, out, _ = self.cli([])
        self.assertEqual(code, 1)
        self.assertIn('gov-ok-' + head, out)
        code, out, _ = self.cli([event('labeled', 'gov-ok-' + head)])
        self.assertEqual(code, 0, out)

    def test_new_push_invalidates_earlier_approval(self):
        self.repo.write('tests/helper.py', 'x\n')
        first = self.repo.commit('helper')
        self.repo.write('tests/helper.py', 'y\n')
        self.repo.commit('helper again')
        code, out, _ = self.cli([event('labeled', 'gov-ok-' + first)])
        self.assertEqual(code, 1, out)

    def test_product_change_passes_without_label(self):
        self.repo.write('src/app.ts', 'x\n')
        self.repo.commit('code')
        code, out, _ = self.cli([])
        self.assertEqual(code, 0, out)
        self.assertIn('RELEASE_GATE_PASSED', out)

    def test_missing_events_file_argument_fails(self):
        out = io.StringIO()
        head = run(self.repo.root, 'rev-parse', 'HEAD')
        with redirect_stdout(out), unittest.mock.patch.dict(os.environ, {'EXPECTED_SOURCE': head}):
            code = gate.main(['--root', str(self.repo.root), '--mode', 'objects', '--head', head, '--governance'])
        self.assertEqual(code, 1)


class CurrentRepository(unittest.TestCase):
    def test_candidate_migrations_pass_against_main(self):
        root = Path(__file__).resolve().parents[2]
        if subprocess.run(['git', '-C', str(root), 'rev-parse', '--verify', 'origin/main'],
                          capture_output=True).returncode:
            self.skipTest('origin/main not fetched')
        versions = gate.verify_migrations(root, 'HEAD', 'origin/main')
        self.assertEqual(len(versions), len({p.name for p in (root / M).glob('*.sql')}))


if __name__ == '__main__':
    unittest.main()
