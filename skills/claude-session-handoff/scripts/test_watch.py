#!/usr/bin/env python3
"""Focused observer checks with fake coordinator-status, transcript and Codex CLI boundaries; no live messages.

Run: python3 -B -m unittest discover -s scripts -p 'test_watch.py' -v
"""
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import uuid

import handoff
import watch

COORD = "00000000-0000-4000-8000-0000000000c1"
OTHER = "00000000-0000-4000-8000-0000000000c2"
SUPER = "00000000-0000-4000-8000-0000000000d1"


class FakeCodex:
    def __init__(self):
        self.calls, self.queue_rc, self.cli, self.daemon, self.raise_timeout = [], 0, "0.160.0", "0.162.1", False

    def __call__(self, arguments, timeout):
        self.calls.append(list(arguments))
        if arguments[:1] == ["--version"]:
            return subprocess.CompletedProcess(arguments, 0, f"codex-cli {self.cli}\n", "")
        if arguments[:3] == ["app-server", "daemon", "version"]:
            return subprocess.CompletedProcess(arguments, 0, json.dumps({"appServerVersion": self.daemon}), "")
        if self.raise_timeout:
            raise subprocess.TimeoutExpired(arguments, timeout)
        return subprocess.CompletedProcess(arguments, self.queue_rc, "", "")

    def queues(self):
        return [c for c in self.calls if c[:1] == ["queue"]]


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="watch-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        env = patch.dict(os.environ, {"HOME": str(self.tmp / "home"), "GIT_CONFIG_GLOBAL": os.devnull,
                                      "GIT_CONFIG_NOSYSTEM": "1"})
        env.start()
        self.addCleanup(env.stop)
        (self.tmp / "home").mkdir()
        self.repo = self.tmp / "repo"
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.repo)], check=True)
        (self.repo / "management").mkdir()
        (self.repo / "management/PROGRESS.md").write_text("# Progress\n")
        self.root = handoff.repo_root(self.repo)
        self.projects = self.tmp / "home" / ".claude" / "projects" / "fixture"
        self.projects.mkdir(parents=True)
        self.transcript = self.projects / f"{COORD}.jsonl"
        self.transcript.write_text(self.row("assistant", "Earlier: ready for review (history, not replayed).") + "\n")
        self.status = {"status": "pinned-live-verified", "pin": {"session": COORD}, "registration_status": "busy"}
        self.codex = FakeCodex()
        p1 = patch.object(watch, "coordinator_status", lambda root: json.loads(json.dumps(self.status)))
        p2 = patch.object(watch, "run_codex", self.codex)
        for p in (p1, p2):
            p.start()
            self.addCleanup(p.stop)

    @staticmethod
    def row(kind, text, tool=None, sidechain=False):
        content = [{"type": "text", "text": text}]
        if tool:
            content.append({"type": "tool_use", "name": tool, "input": {}})
        return json.dumps({"type": kind, "uuid": str(uuid.uuid4()), "timestamp": "2026-10-12T00:00:00Z",
                           "isSidechain": sidechain, "message": {"role": kind, "content": content}})

    def append(self, *rows):
        with self.transcript.open("a") as stream:
            for row in rows:
                stream.write(row + "\n")

    def bind(self, *extra):
        return watch.main(["--repo", str(self.repo), "bind", "--supervisor", SUPER, *extra])

    def poll(self):
        return watch.main(["--repo", str(self.repo), "poll-once"])

    def state(self):
        return json.loads(handoff.read_private(watch.observer_dir(self.root) / "state.json"))


class Polling(Base):
    def test_idle_polling_makes_zero_queue_or_cli_calls(self):
        self.bind()
        for _ in range(3):
            self.assertEqual(self.poll()["queue_calls"], 0)
        self.assertEqual(self.codex.calls, [])

    def test_milestone_notifies_once_and_history_is_not_replayed(self):
        self.bind()
        self.poll()
        self.append(self.row("assistant", "Result submitted for Codex review."))
        result = self.poll()
        self.assertEqual((result["status"], result["queue_calls"]), ("polled", 1))
        call = self.codex.queues()[0]
        self.assertEqual(call[:3], ["queue", "--thread", SUPER])
        self.assertIn("[observer-notice:", call[4])
        self.assertIn("review-ready", call[4])
        self.assertIn("no approval or task authority", call[4])
        self.assertEqual(self.poll()["queue_calls"], 0)

    def test_restart_keeps_dedup_and_offsets(self):
        self.bind()
        self.poll()
        self.append(self.row("assistant", "Work is complete; handback sent."))
        self.poll()
        self.assertEqual(len(self.codex.queues()), 1)
        offsets = self.state()["offsets"]
        self.assertEqual(self.poll()["queue_calls"], 0)  # a fresh process reads the same private state
        self.assertEqual(self.state()["offsets"], offsets)
        self.append(self.row("assistant", "I am blocked on a missing input."))
        self.assertEqual(self.poll()["queue_calls"], 1)

    def test_partial_line_waits_until_complete(self):
        self.bind()
        self.poll()
        line = self.row("assistant", "Plan is review-ready.")
        with self.transcript.open("a") as stream:
            stream.write(line[:25])
        self.assertEqual(self.poll()["queue_calls"], 0)
        with self.transcript.open("a") as stream:
            stream.write(line[25:] + "\n")
        self.assertEqual(self.poll()["queue_calls"], 1)

    def test_rotated_and_truncated_transcripts(self):
        self.bind()
        self.poll()
        first = self.row("assistant", "Escalating a scope question.")
        self.append(first)
        self.poll()
        rotated = self.transcript.with_suffix(".new")
        rotated.write_text(first + "\n" + self.row("assistant", "Completed the attempt; handback ready.") + "\n")
        os.replace(rotated, self.transcript)
        self.assertEqual(self.poll()["queue_calls"], 1)  # only the new row; the old key is deduplicated
        self.transcript.write_text(self.row("assistant", "Result is review-ready again after fixes.") + "\n")
        self.assertEqual(self.poll()["queue_calls"], 1)

    def test_question_tool_sidechain_and_non_milestone_rows(self):
        self.bind()
        self.poll()
        self.append(self.row("assistant", "Choosing an option.", tool="AskUserQuestion"),
                    self.row("assistant", "Subagent says blocked.", sidechain=True),
                    self.row("assistant", "Running tests now."))
        self.assertEqual(self.poll()["queue_calls"], 1)
        self.assertIn("(question", self.codex.queues()[0][4])

    def test_waiting_requires_native_inspection_and_notifies_on_transition(self):
        self.bind()
        self.poll()
        self.status["registration_status"] = "waiting"
        self.assertEqual(self.poll()["queue_calls"], 1)
        self.assertIn("native prompt was not inspected", self.codex.queues()[0][4])
        self.assertEqual(self.poll()["queue_calls"], 0)
        self.status["registration_status"] = "busy"
        self.poll()
        self.status["registration_status"] = "waiting"
        self.assertEqual(self.poll()["queue_calls"], 1)


class NotificationSources(Base):
    def test_codex_repository_edits_cause_zero_queue_calls(self):
        self.bind()
        self.poll()
        (self.repo / "management/PROGRESS.md").write_text("# Progress\n\nG002 review-ready; blocked; handback.\n")
        (self.repo / "management/review.md").write_text("Outcome: ACCEPT; ready for review\n")
        self.assertEqual(self.poll()["queue_calls"], 0)
        self.assertEqual(self.codex.calls, [])

    def test_incoming_and_echoed_handoffs_cause_zero_queue_calls(self):
        self.bind()
        self.poll()
        incoming = "Codex correction: Result is review-ready? blocked? [handoff-id: 00000000-0000-4000-8000-0000000000e1]"
        self.append(self.row("user", incoming),
                    json.dumps({"type": "queue-operation", "operation": "enqueue", "content": incoming}),
                    self.row("assistant", "Received: " + incoming))
        self.assertEqual(self.poll()["queue_calls"], 0)

    def test_notice_echo_does_not_retrigger_then_genuine_milestone_notifies_once(self):
        self.bind()
        self.poll()
        self.append(self.row("assistant", "Implementation submitted for Codex review."))
        self.poll()
        notice = self.codex.queues()[0][4]
        self.append(self.row("user", "Supervisor replied to " + notice),
                    self.row("assistant", "Acknowledged " + notice + " (review-ready, handback)."))
        self.assertEqual(self.poll()["queue_calls"], 0)
        self.append(self.row("assistant", "Correction complete: work is complete and handed back."))
        self.assertEqual(self.poll()["queue_calls"], 1)
        self.assertEqual(len(self.codex.queues()), 2)

    def test_task_closeout_keeps_monitoring_and_dedup(self):
        self.bind()
        self.poll()
        self.append(self.row("assistant", "G001 handback sent."))
        self.poll()
        keys = len(self.state()["keys"])
        worktree = self.repo / ".claude" / "worktrees" / "g001-agent-x-impl"
        worktree.mkdir(parents=True)
        shutil.rmtree(worktree)                                     # task worktree cleanup
        (self.repo / "management/SESSION-HANDOFFS.jsonl").write_text("")  # delivery log compaction
        self.assertEqual(len(self.state()["keys"]), keys)
        self.assertEqual(self.poll()["queue_calls"], 0)
        self.append(self.row("assistant", "G002 plan is review-ready."))
        self.assertEqual(self.poll()["queue_calls"], 1)


class Identity(Base):
    def test_unknown_identity_suspends_until_explicit_rebind(self):
        self.bind()
        self.poll()
        self.status = {"status": "discovery-unknown"}
        self.append(self.row("assistant", "Ready for review."))
        result = self.poll()
        self.assertEqual((result["status"], result["reason"]), ("suspended", "coordinator-discovery-unknown"))
        self.status = {"status": "pinned-live-verified", "pin": {"session": COORD}, "registration_status": "busy"}
        self.assertEqual(self.poll()["status"], "suspended")
        self.assertEqual(self.codex.calls, [])
        self.bind("--replace")
        self.assertEqual(self.poll()["status"], "polled")

    def test_changed_coordinator_never_retargets(self):
        self.bind()
        self.poll()
        self.status["pin"]["session"] = OTHER
        result = self.poll()
        self.assertEqual(result["reason"], "coordinator-changed-rebind-required")
        self.assertEqual(self.codex.calls, [])
        with self.assertRaises(handoff.Blocked):
            self.bind()  # rebinding needs an explicit --replace

    def test_retired_session_blocks_delivery(self):
        self.bind()
        self.poll()
        self.status = {"status": "pinned-not-live", "pin": {"session": COORD}}
        self.append(self.row("assistant", "Completed the task."))
        self.assertEqual(self.poll()["status"], "suspended")
        self.status = {"status": "pinned-live-verified", "pin": {"session": COORD}, "registration_status": "busy"}
        self.assertEqual(self.poll()["status"], "suspended")
        self.assertEqual(self.codex.queues(), [])

    def test_bind_requires_verified_pin_and_canonical_uuid(self):
        self.status = {"status": "unpinned"}
        with self.assertRaises(handoff.Blocked):
            self.bind()
        self.status = {"status": "pinned-live-verified", "pin": {"session": COORD}}
        with self.assertRaises(handoff.Blocked):
            watch.main(["--repo", str(self.repo), "bind", "--supervisor", "supervisor-name"])

    def test_status_shows_fingerprint_not_uuid(self):
        self.bind()
        text = json.dumps(watch.main(["--repo", str(self.repo), "status"]))
        self.assertNotIn(SUPER, text)
        self.assertIn(watch.fingerprint(SUPER), text)


class StateAndQueue(Base):
    def test_unsafe_state_is_refused(self):
        self.bind()
        directory = watch.observer_dir(self.root)
        os.chmod(directory / "binding.json", 0o644)
        with self.assertRaises(handoff.Blocked):
            self.poll()
        os.chmod(directory / "binding.json", 0o600)
        target = self.tmp / "elsewhere.json"
        target.write_text("{}")
        os.chmod(target, 0o600)
        (directory / "state.json").unlink(missing_ok=True)
        os.symlink(target, directory / "state.json")
        with self.assertRaises(handoff.Blocked):
            self.poll()
        os.unlink(directory / "state.json")
        os.chmod(directory, 0o755)
        with self.assertRaises(handoff.Blocked):
            self.poll()
        self.assertEqual(self.codex.calls, [])

    def test_queue_failure_is_uncertain_and_never_retried(self):
        self.bind()
        self.poll()
        self.codex.queue_rc = 1
        self.append(self.row("assistant", "Ready for review."))
        result = self.poll()
        self.assertEqual((result["status"], result["reason"]), ("suspended", "queue-uncertain"))
        self.assertEqual(self.state()["deliveries"][-1]["outcome"], "queue-uncertain-exit-1")
        self.codex.queue_rc = 0
        self.append(self.row("assistant", "Blocked now."))
        self.assertEqual(self.poll()["queue_calls"], 0)
        self.assertEqual(len(self.codex.queues()), 1)

    def test_queue_timeout_is_uncertain(self):
        self.bind()
        self.poll()
        self.codex.raise_timeout = True
        self.append(self.row("assistant", "Handback sent."))
        self.assertEqual(self.poll()["reason"], "queue-uncertain")
        self.assertEqual(self.state()["deliveries"][-1]["outcome"], "queue-uncertain-error")

    def test_unverified_codex_version_sends_nothing(self):
        self.bind()
        self.poll()
        self.codex.daemon = "9.9.9"
        self.append(self.row("assistant", "Ready for review."))
        self.assertEqual(self.poll()["reason"], "unverified-codex-version")
        self.assertEqual(self.codex.queues(), [])

    def test_smoke_delivers_exactly_once(self):
        self.bind()
        result = watch.main(["--repo", str(self.repo), "smoke", "--label", "AC13 smoke"])
        self.assertEqual(result["status"], "queued-not-acknowledged")
        self.assertIn("OBSERVER SMOKE TEST", self.codex.queues()[0][4])
        with self.assertRaises(handoff.Blocked):
            watch.main(["--repo", str(self.repo), "smoke", "--label", "again"])
        self.assertEqual(len(self.codex.queues()), 1)


class Lifecycle(Base):
    def fake_child(self, root, interval):
        return [sys.executable, "-c", "import time; time.sleep(60)", "observer-fixture", str(interval)]

    def test_start_duplicate_stop_and_cleanup(self):
        self.bind()
        with patch.object(watch, "child_argv", self.fake_child):
            started = watch.main(["--repo", str(self.repo), "start", "--interval", "15"])
            self.assertEqual(started["status"], "started")
            self.assertEqual(watch.main(["--repo", str(self.repo), "start"])["status"], "already-running")
            self.assertEqual(watch.main(["--repo", str(self.repo), "status"])["status"], "running")
            stopped = watch.main(["--repo", str(self.repo), "stop"])
        self.assertEqual(stopped["status"], "stopped")
        # In the test the fixture process is our child: reap it to prove it exited (the CLI's would reparent).
        pid, status = os.waitpid(started["pid"], 0)
        self.assertEqual(pid, started["pid"])
        with self.assertRaises(ProcessLookupError):
            os.kill(started["pid"], 0)
        self.assertEqual(watch.main(["--repo", str(self.repo), "status"])["status"], "stopped")

    def test_stop_refuses_reused_pid(self):
        self.bind()
        other = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        self.addCleanup(other.wait)
        self.addCleanup(other.kill)
        directory = watch.observer_dir(self.root)
        watch.save(directory, "process.json", {"pid": other.pid, "start": handoff.process_start(other.pid),
                                               "argv": watch.child_argv(self.root, 20)})
        result = watch.main(["--repo", str(self.repo), "stop"])
        self.assertEqual(result["status"], "stale-record-not-signalled")
        self.assertIsNone(other.poll())

    def test_start_requires_binding_and_interval_bounds(self):
        with self.assertRaises(handoff.Blocked):
            watch.main(["--repo", str(self.repo), "start"])
        self.bind()
        with self.assertRaises(handoff.Blocked):
            watch.main(["--repo", str(self.repo), "start", "--interval", "1"])

    def test_run_loop_is_single_instance_and_stops_on_signal(self):
        self.bind()
        directory = watch.observer_dir(self.root)
        holder = os.open(directory / "run.lock", os.O_RDWR | os.O_CREAT, 0o600)
        fcntl.flock(holder, fcntl.LOCK_EX)
        self.assertEqual(watch.cmd_run(self.root, 5)["status"], "already-running")
        os.close(holder)
        polls = []

        def poll(root):
            polls.append(1)
            if len(polls) == 2:
                watch.STOP = True
            return {"status": "polled", "queue_calls": 0}
        with patch.object(watch, "poll_once", poll), patch.object(watch, "signal"):
            watch.STOP = False
            result = watch.cmd_run(self.root, 5)
        watch.STOP = False
        self.assertEqual((result["status"], len(polls)), ("stopped", 2))


if __name__ == "__main__":
    unittest.main()
