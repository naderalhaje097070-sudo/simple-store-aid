begin;
\i /tmp/C3.sql
select pg_sleep(3);
rollback;
