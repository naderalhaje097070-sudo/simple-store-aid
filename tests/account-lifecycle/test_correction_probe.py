import importlib.util
from pathlib import Path
import unittest

from correction_probe import HarnessFailure, SUCCESS, green_result, rpc_payloads, strict_guard_denial


class CorrectionContractTest(unittest.TestCase):
    def test_rpc_denial_requires_named_guard_not_generic_permission_or_server_error(self):
        good={'code':'42501','message':'account_inactive'}
        self.assertTrue(strict_guard_denial(403,good))
        for status,body in [(500,good),(400,good),(200,good),(403,{'code':'42501','message':'other'}),(403,[]),(403,{'message':'account_inactive'})]:
            with self.subTest(status=status,body=body):self.assertFalse(strict_guard_denial(status,body))

    def test_all_ten_regressions_and_active_controls_are_required(self):
        names={f'banned_{a}_{c}' for a in ('owner','staff') for c in
               ('old_jwt_own_tenant','old_jwt_own_profiles','old_jwt_own_user_roles','summary','direct_rls')}
        names|={'active_after_ban_owner_A','active_after_ban_staff_A','public_history_preserved'}
        checks=[{'name':n,'passed':True} for n in names]
        self.assertEqual(green_result(checks),SUCCESS)
        for i in range(len(checks)):
            with self.subTest(removed=checks[i]['name']):
                with self.assertRaises(HarnessFailure):green_result(checks[:i]+checks[i+1:])
        for bad in [[],checks+[checks[0]],[dict(c,passed=False) if i==0 else c for i,c in enumerate(checks)]]:
            with self.assertRaises(HarnessFailure):green_result(bad)

    def test_rpc_surface_is_exact_without_financial_fixtures(self):
        import json
        catalog=json.loads(Path('changes/env-native-01/evidence/clean-baseline/catalog.json').read_text())
        expected={f['name'] for f in catalog['functions'] if f['definer'] and 'authenticated=X/' in f['acl']}
        payload=rpc_payloads({'tenant':'fixture_tid'},{'uid':'other_uid'})
        self.assertEqual(set(payload),expected)
        self.assertEqual(len(payload),30)
        self.assertEqual(payload['has_owner_role']['_uid'],'other_uid')

    def test_generator_rejects_wrong_catalog_before_sql(self):
        p=Path('changes/env-native-01/generate-correction.py')
        spec=importlib.util.spec_from_file_location('correction_generator',p)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with self.assertRaisesRegex(ValueError,'digest mismatch'):module.render(b'{}')

    def test_generator_preserves_inner_financial_body_and_only_injects_outer_guard(self):
        p=Path('changes/env-native-01/generate-correction.py')
        spec=importlib.util.spec_from_file_location('correction_generator',p)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        definition="CREATE OR REPLACE FUNCTION public.example() RETURNS void LANGUAGE plpgsql AS $function$\nBEGIN\n  BEGIN\n    PERFORM 1;\n  END;\nEND;\n$function$\n"
        rendered=module.guarded(definition)
        self.assertEqual(rendered.replace(module.GUARD,'').rstrip(';\n'),definition.rstrip('\n'))
        self.assertEqual(rendered.count(module.GUARD),1)


if __name__=='__main__':unittest.main()
