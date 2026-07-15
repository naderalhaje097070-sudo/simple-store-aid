-- Local/ephemeral test users only. This file is never applied as a migration.
-- Password login is covered by isolated-auth-smoke; database rules only need
-- stable auth.users identities for auth.uid() and role/RLS simulation.

INSERT INTO auth.users (
  instance_id,
  id,
  aud,
  role,
  email,
  encrypted_password,
  email_confirmed_at,
  raw_app_meta_data,
  raw_user_meta_data,
  created_at,
  updated_at,
  confirmation_token,
  recovery_token,
  email_change_token_new,
  email_change
)
VALUES
  (
    '00000000-0000-0000-0000-000000000000'::uuid,
    'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'::uuid,
    'authenticated',
    'authenticated',
    'employee.a@mongezz.test',
    '',
    now(),
    '{"provider":"email","providers":["email"]}'::jsonb,
    '{"display_name":"Employee A"}'::jsonb,
    now(),
    now(),
    '', '', '', ''
  ),
  (
    '00000000-0000-0000-0000-000000000000'::uuid,
    'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'::uuid,
    'authenticated',
    'authenticated',
    'employee.b@mongezz.test',
    '',
    now(),
    '{"provider":"email","providers":["email"]}'::jsonb,
    '{"display_name":"Employee B"}'::jsonb,
    now(),
    now(),
    '', '', '', ''
  )
ON CONFLICT (id) DO NOTHING;

INSERT INTO public.profiles(id, tenant_id, display_name)
VALUES
  ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'::uuid, NULL, 'Employee A'),
  ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'::uuid, NULL, 'Employee B')
ON CONFLICT (id) DO UPDATE
SET display_name = EXCLUDED.display_name;
