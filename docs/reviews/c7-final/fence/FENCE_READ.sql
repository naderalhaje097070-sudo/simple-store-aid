-- C7 final fence: read the current attempt number (read only). NULL means the fence does not exist.
begin transaction read only;
select json_build_object(
  'ro', current_setting('transaction_read_only'),
  'fence_exists', to_regclass('monjez_private.c7_final_fence') is not null,
  'current_attempt', case when to_regclass('monjez_private.c7_final_fence') is not null
    then ((xpath('/row/attempt/text()', query_to_xml('select attempt from monjez_private.c7_final_fence', false, true, '')))[1])::text::integer end
) as c7_final_fence;
rollback;
