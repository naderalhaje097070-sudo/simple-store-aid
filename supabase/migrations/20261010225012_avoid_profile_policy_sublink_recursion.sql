-- Forward compensation for the immutable, isolated-tested migration42.
-- profiles' existing UPDATE check reads profiles. An additional SELECT SubLink
-- in an ALL policy makes PostgreSQL recursively expand that self-reference.
-- Keep exactly the same private predicate; use a direct call on this table only.
BEGIN;
ALTER POLICY monjez_live_actor ON public.profiles
  USING (monjez_private.actor_is_active())
  WITH CHECK (monjez_private.actor_is_active());
COMMIT;
