"""Format-insensitive exact guard message proof; publish only static categories."""
import hashlib
import re

EXPECTED = 'SEC_ENV_CONFIG_ERROR: runtime Supabase configuration does not match baked build configuration'
KEYS = ['MONGEZZ_DEPLOY_TARGET', 'VITE_SUPABASE_URL', 'VITE_SUPABASE_PUBLISHABLE_KEY',
        'VITE_SUPABASE_PROJECT_ID', 'SUPABASE_URL', 'SUPABASE_PUBLISHABLE_KEY',
        'SUPABASE_PROJECT_ID', 'SUPABASE_SERVICE_ROLE_KEY']
KNOWN = {'build_runtime_supabase_mismatch': EXPECTED,
         'build_runtime_target_mismatch': 'SEC_ENV_CONFIG_ERROR: runtime deployment target does not match baked build target',
         'url_alias_mismatch': 'SEC_ENV_CONFIG_ERROR: VITE_SUPABASE_URL and SUPABASE_URL must target the same project',
         'key_alias_mismatch': 'SEC_ENV_CONFIG_ERROR: VITE_SUPABASE_PUBLISHABLE_KEY and SUPABASE_PUBLISHABLE_KEY must match',
         'project_alias_mismatch': 'SEC_ENV_CONFIG_ERROR: VITE_SUPABASE_PROJECT_ID and SUPABASE_PROJECT_ID must match'}
KNOWN.update({'binding_conflict_'+k: 'SEC_ENV_BINDING_CONFLICT: '+k+' differs between runtime sources' for k in KEYS})


def normalize(text):
    return ' '.join(re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', text).split())


def receipt(status, body, log):
    text = normalize(log)
    matched = sorted(k for k, value in KNOWN.items() if value in text)
    return {'status': status, 'response_sha256': hashlib.sha256(body).hexdigest(),
            'private_log_sha256': hashlib.sha256(log.encode()).hexdigest(),
            'exact_expected_guard_present': EXPECTED in text, 'known_guard_categories': matched,
            'unclassified_error': not bool(matched),
            'passed': status == 500 and EXPECTED in text,
            'format_only_normalization': 'ANSI controls removed; whitespace collapsed; full phrase unchanged'}
