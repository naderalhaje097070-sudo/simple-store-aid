"""Procfs lifecycle fixtures; never inspect cmdline, environment or real processes."""
import json
import os
from pathlib import Path
from subprocess import CompletedProcess, TimeoutExpired
import tempfile
import unittest
from unittest.mock import patch

import egress_trace


class DormantThread:
    def __init__(self, **kwargs):
        pass
    def start(self):
        pass
    def join(self, timeout=None):
        pass
    def is_alive(self):
        return False


class OnePass:
    def __init__(self):
        self.done = False
    def is_set(self):
        return self.done
    def wait(self, timeout):
        self.done = True
    def set(self):
        self.done = True


class ProcessMapContract(unittest.TestCase):
    def exercise(self, states, *, readable=(), timeout=False, already_failed=False, after_read=None):
        with tempfile.TemporaryDirectory(prefix="monjez-proc-") as directory:
            root = Path(directory)
            proc = root / "1000"
            for tid, state in states.items():
                task = proc / "task" / str(tid)
                task.mkdir(parents=True)
                if state is not None:
                    (task / "status").write_text(
                        f"Name:\tfixture\nState:\t{state}\nTgid:\t1000\nPPid:\t1\nUid:\t{os.getuid()} 0 0 0\n"
                    )
            def paths(value):
                return root if str(value) == "/proc" else Path(value)
            calls = []
            def readlink(command, **kwargs):
                calls.append(command[-1])
                if after_read is not None:
                    tid = int(Path(command[-1]).parent.name)
                    status = proc / "task" / str(tid) / "status"
                    if after_read == "gone":
                        status.unlink()
                    else:
                        status.write_text(status.read_text().replace(states[tid], after_read))
                if timeout:
                    raise TimeoutExpired("readlink", 2)
                ok = any(command[-1].endswith(f"task/{tid}/exe") for tid in readable)
                return CompletedProcess(command, 0 if ok else 1,
                                        stdout="/usr/bin/node\n" if ok else "",
                                        stderr="private_fixture_needle")
            with patch.object(egress_trace.threading, "Thread", DormantThread), \
                 patch.object(egress_trace, "Path", side_effect=paths), \
                 patch.object(egress_trace.subprocess, "run", side_effect=readlink):
                mapper = egress_trace.ProcessMap(os.getuid())
                mapper.done = OnePass()
                mapper.failed = already_failed
                mapper.monitor()
                result = mapper.stop()
            self.assertNotIn("private_fixture_needle", json.dumps(result))
            return result, calls

    def test_zombie_without_executable_is_not_an_observer_read_failure(self):
        result, calls = self.exercise({1000: "Z (zombie)"})
        self.assertFalse(result["read_failed"])
        self.assertEqual(result["processes"], [])
        self.assertEqual(calls, [])

    def test_dead_leader_does_not_hide_a_live_worker(self):
        result, calls = self.exercise({1000: "Z (zombie)", 1001: "S (sleeping)"}, readable=(1001,))
        self.assertFalse(result["read_failed"])
        self.assertEqual([x["tid"] for x in result["processes"]], [1001])
        self.assertTrue(any(x.endswith("task/1001/exe") for x in calls))

    def test_live_unreadable_worker_still_fails_closed(self):
        result, _ = self.exercise({1000: "Z (zombie)", 1001: "S (sleeping)"})
        self.assertTrue(result["read_failed"])
        self.assertEqual(result["processes"], [])

    def test_live_executable_failure_still_fails(self):
        result, _ = self.exercise({1000: "R (running)"})
        self.assertTrue(result["read_failed"])

    def test_timeout_still_fails_closed(self):
        result, _ = self.exercise({1000: "R (running)"}, timeout=True)
        self.assertTrue(result["read_failed"])

    def test_disappearing_thread_does_not_erase_an_earlier_failure(self):
        result, _ = self.exercise({1000: None}, already_failed=True)
        self.assertTrue(result["read_failed"])

    def test_confirmed_exit_during_executable_read_is_recorded(self):
        result, _ = self.exercise({1000: "R (running)"}, after_read="Z (zombie)")
        self.assertFalse(result["read_failed"])
        self.assertEqual(result["terminal_tasks"], [{"tid": 1000, "tgid": 1000, "state": "Z"}])
        self.assertEqual(result["processes"], [])

    def test_disappearance_during_executable_read_has_no_fabricated_row(self):
        result, _ = self.exercise({1000: "R (running)"}, after_read="gone")
        self.assertFalse(result["read_failed"])
        self.assertEqual(result["processes"], [])

    def test_failure_receipt_has_only_bounded_category_and_tid(self):
        result, _ = self.exercise({1000: "R (running)"})
        self.assertEqual(result["read_failures"], [{"reason": "live_executable_unreadable", "tid": 1000}])

    def test_terminal_observation_does_not_fabricate_attribution(self):
        result, _ = self.exercise({1000: "Z (zombie)"})
        mapped = {x["tid"] for x in result["processes"]}
        nonloopback_event = {"tid": 1000, "loopback": False}
        self.assertEqual([nonloopback_event["tid"]] if nonloopback_event["tid"] not in mapped else [], [1000])


if __name__ == "__main__":
    unittest.main()
