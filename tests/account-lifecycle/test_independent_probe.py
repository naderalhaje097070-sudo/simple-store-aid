"""Contract checks for the independent token/error oracle, without live claims."""
import hashlib
import hmac
import json
import unittest

from independent_probe import (HarnessFailure, account_denial, decoded, encoded, foreign_denial, decode_diagnostic,
                               expiry_denial, metadata_denial, signature_denial, signed_twins)


class IndependentOracleTest(unittest.TestCase):
    secret = 'dummy-unit-secret-never-a-runtime-secret'
    uid = '00000000-0000-4000-8000-000000000003'

    def token(self, header=None, **changes):
        header = header or {'alg':'HS256','typ':'JWT'}
        claims = {'sub':self.uid,'role':'authenticated','exp':2000,'iat':900,'session_id':'dummy-session','aud':'authenticated'}
        claims.update(changes)
        unsigned = encoded(json.dumps(header).encode())+'.'+encoded(json.dumps(claims).encode())
        return unsigned+'.'+encoded(hmac.new(self.secret.encode(),unsigned.encode(),hashlib.sha256).digest())

    def test_twins_change_only_expiry_and_keep_real_verified_signature(self):
        original = self.token()
        future, expired, invalid, provenance = signed_twins(original,self.secret,self.uid,1000,self.uid)
        source_claims = json.loads(decoded(original.split('.')[1]))
        for token, expected_exp in [(future,1600),(expired,700)]:
            head,payload,sig = token.split('.')
            self.assertEqual(json.loads(decoded(head)),{'alg':'HS256','typ':'JWT'})
            self.assertEqual(json.loads(decoded(payload)),dict(source_claims,exp=expected_exp))
            self.assertTrue(hmac.compare_digest(decoded(sig),hmac.new(self.secret.encode(),(head+'.'+payload).encode(),hashlib.sha256).digest()))
        self.assertEqual(invalid.split('.')[:2],future.split('.')[:2])
        self.assertNotEqual(decoded(invalid.split('.')[2]),decoded(future.split('.')[2]))
        self.assertEqual(provenance['issuer_algorithm'],'HS256')

    def test_unsupported_alg_missing_secret_and_unverified_identity_fail_closed(self):
        for token, secret, uid in [(self.token({'alg':'none'}),self.secret,self.uid),
                (self.token({'alg':'unknown'}),self.secret,self.uid),
                (self.token(),None,self.uid),(self.token(),self.secret+'wrong',self.uid),
                (self.token(),self.secret,'other-uid'),(self.token(role='service_role'),self.secret,self.uid),
                (self.token(exp=999),self.secret,self.uid),('bad-token',self.secret,self.uid)]:
            with self.subTest(token_shape=token.count('.'),secret_present=secret is not None):
                with self.assertRaises(HarnessFailure):signed_twins(token,secret,uid,1000,self.uid)

    def test_asymmetric_claim_fixture_requires_provider_verification_and_clean_hs_header(self):
        original = self.token({'alg':'ES256','kid':'unit-only-issuer-kid'})
        for provider_uid in [None,'different-uid']:
            with self.assertRaises(HarnessFailure):signed_twins(original,self.secret,self.uid,1000,provider_uid)
        # Offline input represents claims only, not an ECDSA verification proof.
        future, expired, _, provenance = signed_twins(original,self.secret,self.uid,1000,self.uid)
        self.assertEqual(provenance['issuer_algorithm'],'ES256')
        self.assertFalse(provenance['asymmetric_signature_verified_locally'])
        self.assertEqual(provenance['issuer_validation'],'Auth GET/user')
        for token in (future,expired):
            self.assertEqual(json.loads(decoded(token.split('.')[0])),{'alg':'HS256','typ':'JWT'})

    def test_lifecycle_denial_never_accepts_expiry_or_generic_permissions(self):
        good = {'code':'42501','message':'account_inactive'}
        self.assertTrue(account_denial(403,good));self.assertTrue(metadata_denial(200,[]))
        for status, body in [(500,good),(401,{'code':'PGRST303','message':'JWT expired'}),
                            (403,{'code':'42501','message':'permission denied'}),(200,[{'id':'leaked'}]),(200,{}),(400,good)]:
            with self.subTest(status=status):self.assertFalse(metadata_denial(status,body))

    def test_expiry_and_signature_error_are_distinct_strict_provider_reasons(self):
        expired = {'code':'PGRST303','message':'JWT expired'}
        tampered = {'code':'PGRST301','message':'No suitable key or wrong key type','details':'None of the keys was able to decode the JWT'}
        self.assertTrue(expiry_denial(401,expired));self.assertTrue(signature_denial(401,tampered))
        self.assertFalse(signature_denial(401,expired));self.assertFalse(expiry_denial(401,tampered))
        self.assertFalse(signature_denial(401,dict(tampered,details='No suitable key was found to decode the JWT')))
        self.assertFalse(signature_denial(401,dict(tampered,details=None)))
        for status, body in [(500,expired),(403,expired),(401,{'code':'PGRST301','message':'JWT expired'}),
                            (401,{'code':'PGRST301','message':'unknown JWT error'}),(401,[])]:
            with self.subTest(status=status):self.assertFalse(expiry_denial(status,body))

    def test_provider_diagnostic_cannot_persist_raw_token_or_key_text(self):
        unsafe = {'code':'SECRET_TOKEN','message':'JWT abc.def.signature','details':'runtime-secret-or-token'}
        self.assertEqual(set(decode_diagnostic(unsafe).values()),{'unrecognized'})
        self.assertEqual(set(decode_diagnostic({'code':[],'message':[],'details':{}}).values()),{'unrecognized'})
        actual = {'code':'PGRST301','message':'No suitable key or wrong key type','details':'None of the keys was able to decode the JWT'}
        self.assertEqual(decode_diagnostic(actual),{'provider_code':actual['code'],'provider_message':actual['message'],'provider_details':actual['details']})

    def test_active_foreign_policy_denial_is_distinct_from_lifecycle_guard(self):
        ordinary_rls = {'code':'42501','message':'new row violates row-level security policy'}
        self.assertTrue(foreign_denial(403,ordinary_rls))
        self.assertFalse(metadata_denial(403,ordinary_rls))
        self.assertTrue(foreign_denial(200,[]))
        for status, body in [(500,ordinary_rls),(401,{'code':'PGRST303','message':'JWT expired'}),
                            (403,{'code':'other','message':'permission denied'}),(200,[{'id':'leaked'}])]:
            with self.subTest(status=status):self.assertFalse(foreign_denial(status,body))


if __name__ == '__main__':unittest.main()
