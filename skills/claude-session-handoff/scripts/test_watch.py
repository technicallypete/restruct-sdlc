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


class SizeAdvisory(Base):
    def grow(self, size):
        with self.transcript.open("a") as stream:
            stream.write(" " * max(0, size - self.transcript.stat().st_size - 1) + "\n")

    def advisories(self):
        return [c for c in self.codex.queues() if "transcript size advisory" in c[4]]

    def test_default_threshold_is_100_mib_and_status_reports_it(self):
        self.bind()
        self.assertEqual(watch.DEFAULT_SIZE_THRESHOLD, 104857600)
        self.poll()
        status = watch.main(["--repo", str(self.repo), "status"])
        self.assertEqual(status["size_threshold"], 104857600)
        self.assertEqual(status["transcript"]["bytes"], self.transcript.stat().st_size)
        self.assertFalse(status["transcript"]["advised"])
        self.assertEqual(self.codex.calls, [])

    def test_below_at_and_above_threshold(self):
        self.bind("--size-threshold", "4096")
        self.poll()
        self.grow(4095)
        self.assertEqual(self.poll()["queue_calls"], 0)
        self.grow(4096)
        self.assertEqual(self.poll()["queue_calls"], 1)
        message = self.advisories()[0][4]
        self.assertIn("4096 bytes", message)
        self.assertIn("4096-byte threshold", message)
        self.assertIn("safe session handoff or archive", message)
        self.grow(9000)
        self.assertEqual(self.poll()["queue_calls"], 0)  # already advised for this coordinator and threshold
        self.assertTrue(watch.main(["--repo", str(self.repo), "status"])["transcript"]["advised"])

    def test_first_poll_already_large_qualifies(self):
        self.grow(5000)
        self.bind("--size-threshold", "4096")
        self.assertEqual(self.poll()["queue_calls"], 1)
        self.assertEqual(len(self.advisories()), 1)

    def test_restart_rotation_and_decrease_do_not_repeat(self):
        self.bind("--size-threshold", "4096")
        self.grow(5000)
        self.poll()
        self.assertEqual(self.poll()["queue_calls"], 0)       # restart: same private state
        self.transcript.write_text(self.row("assistant", "Running tests.") + "\n")  # decrease / truncation
        self.assertEqual(self.poll()["queue_calls"], 0)
        rotated = self.transcript.with_suffix(".new")
        rotated.write_text(" " * 6000 + "\n")
        os.replace(rotated, self.transcript)                   # rotation, large again
        self.assertEqual(self.poll()["queue_calls"], 0)
        self.assertEqual(len(self.advisories()), 1)

    def test_changed_threshold_and_opt_out(self):
        self.bind("--size-threshold", "4096")
        self.grow(5000)
        self.poll()
        self.bind("--replace", "--size-threshold", "2048")     # a new configured threshold is a new advisory key
        self.assertEqual(self.poll()["queue_calls"], 1)
        self.bind("--replace", "--no-size-advisory")
        self.grow(100000)
        self.assertEqual(self.poll()["queue_calls"], 0)
        self.assertIsNone(watch.main(["--repo", str(self.repo), "status"])["size_threshold"])
        with self.assertRaises(handoff.Blocked):
            self.bind("--replace", "--size-threshold", "10")

    def test_replacement_coordinator_is_assessed_separately(self):
        self.bind("--size-threshold", "4096")
        self.grow(5000)
        self.poll()
        other = self.projects / f"{OTHER}.jsonl"
        other.write_text(" " * 6000 + "\n")
        self.status["pin"]["session"] = OTHER
        self.assertEqual(self.poll()["status"], "suspended")   # never retargets implicitly
        self.bind("--replace", "--size-threshold", "4096")
        self.assertEqual(self.poll()["queue_calls"], 1)
        self.assertEqual(len(self.advisories()), 2)

    def test_uncertain_advisory_delivery_is_not_retried(self):
        self.bind("--size-threshold", "4096")
        self.poll()
        self.codex.queue_rc = 1
        self.grow(5000)
        self.assertEqual(self.poll()["reason"], "queue-uncertain")
        self.codex.queue_rc = 0
        self.bind("--replace", "--size-threshold", "4096")
        self.assertEqual(self.poll()["queue_calls"], 0)
        self.assertEqual(self.state()["deliveries"][-1]["outcome"], "queue-uncertain-exit-1")

    def test_unverified_identity_blocks_advisory(self):
        self.grow(5000)
        self.bind("--size-threshold", "4096")
        self.status = {"status": "pinned-unverified", "pin": {"session": COORD}}
        self.assertEqual(self.poll()["status"], "suspended")
        self.assertEqual(self.codex.calls, [])


class DurableIntent(Base):
    """C4: the intent and dedup key are persisted before `codex queue`; interruption never causes a blind retry."""

    class Died(BaseException):
        pass

    def die_after_enqueue(self):
        real = self.codex.__call__

        def call(arguments, timeout):
            result = real(arguments, timeout)
            if arguments[:1] == ["queue"]:
                raise self.Died()  # the process dies right after the external enqueue
            return result
        return patch.object(watch, "run_codex", call)

    def fail_final_save(self):
        real = watch.save

        def save(directory, name, value):
            if name == "state.json" and self.codex.queues() and any(
                    d.get("outcome") != "pending-intent" for d in value.get("deliveries", [])[-1:]):
                raise OSError("disk full after enqueue")
            return real(directory, name, value)
        return patch.object(watch, "save", save)

    def fail_initial_save(self):
        real = watch.save

        def save(directory, name, value):
            if name == "state.json" and any(d.get("outcome") == "pending-intent"
                                            for d in value.get("deliveries", [])):
                raise OSError("cannot persist the intent")
            return real(directory, name, value)
        return patch.object(watch, "save", save)

    def trigger(self, kind):
        if kind == "milestone":
            self.append(self.row("assistant", "Result submitted for Codex review."))
            return self.poll
        if kind == "advisory":
            with self.transcript.open("a") as stream:
                stream.write(" " * 5000 + "\n")
            return self.poll
        return lambda: watch.main(["--repo", str(self.repo), "smoke", "--label", "AC13 smoke"])

    def prepare(self, kind):
        self.bind("--size-threshold", "4096") if kind == "advisory" else self.bind()
        if kind != "smoke":
            self.poll()

    def assert_recovered_without_retry(self, kind):
        if kind == "smoke":
            state = self.state()
            self.assertEqual(state["deliveries"][-1]["outcome"], "pending-intent")
            with self.assertRaises(handoff.Blocked):
                watch.main(["--repo", str(self.repo), "smoke", "--label", "AC13 smoke"])
            self.assertEqual(self.state()["smoke"]["outcome"], "uncertain-interrupted")
        else:
            result = self.poll()
            self.assertEqual((result["status"], result["reason"], result["queue_calls"]),
                             ("suspended", "interrupted-delivery-uncertain", 0))
        self.assertEqual(self.state()["deliveries"][-1]["outcome"], "uncertain-interrupted")
        self.bind("--replace", "--size-threshold", "4096")
        if kind != "smoke":
            self.assertEqual(self.poll()["queue_calls"], 0)  # never retried, even after explicit rebinding
        self.assertEqual(len(self.codex.queues()), 1)

    def test_interruption_after_enqueue_never_retries(self):
        for kind in ("milestone", "advisory", "smoke"):
            with self.subTest(kind=kind):
                self.setUp()
                self.prepare(kind)
                run = self.trigger(kind)
                with self.die_after_enqueue(), self.assertRaises(self.Died):
                    run()
                self.assertEqual(len(self.codex.queues()), 1)
                self.assert_recovered_without_retry(kind)

    def test_failed_final_persistence_never_retries(self):
        for kind in ("milestone", "advisory", "smoke"):
            with self.subTest(kind=kind):
                self.setUp()
                self.prepare(kind)
                run = self.trigger(kind)
                with self.fail_final_save(), self.assertRaises(OSError):
                    run()
                self.assertEqual(len(self.codex.queues()), 1)
                self.assert_recovered_without_retry(kind)

    def test_failed_initial_persistence_never_queues(self):
        for kind in ("milestone", "advisory", "smoke"):
            with self.subTest(kind=kind):
                self.setUp()
                self.prepare(kind)
                run = self.trigger(kind)
                with self.fail_initial_save(), self.assertRaises(OSError):
                    run()
                self.assertEqual(self.codex.queues(), [])

    def test_later_events_in_the_same_poll_are_not_lost(self):
        self.bind()
        self.poll()
        self.append(self.row("assistant", "Plan is review-ready."), self.row("assistant", "Now blocked on input."))
        with self.die_after_enqueue(), self.assertRaises(self.Died):
            self.poll()
        self.bind("--replace")
        self.assertEqual(self.poll()["queue_calls"], 1)  # the unattempted second milestone, offsets not advanced
        self.assertIn("(blocked", self.codex.queues()[-1][4])


class OversizedRows(Base):
    """C5: bounded progress through rows longer than the read limit, with explicit parse-limit reporting."""

    def setUp(self):
        super().setUp()
        for name, value in (("MAX_READ", 1024), ("MAX_SCAN", 4096), ("PREFIX_BYTES", 256)):
            p = patch.object(watch, name, value)
            p.start()
            self.addCleanup(p.stop)
        self.bind()
        self.poll()

    def big(self, kind, size, text="padding"):
        row = json.loads(self.row(kind, text))
        row["pad"] = "x" * size
        return json.dumps(row)

    def offset(self):
        return self.state()["offsets"][str(self.transcript)]

    def test_complete_oversized_nonmilestone_row_then_milestone(self):
        self.append(self.big("user", 3000, "Incoming text says review-ready"),
                    self.row("assistant", "Result submitted for Codex review."))
        result = self.poll()
        self.assertEqual(result["queue_calls"], 1)
        self.assertIn("review-ready", self.codex.queues()[0][4])
        self.assertEqual(self.offset()["offset"], self.transcript.stat().st_size)
        self.assertNotIn("oversized", self.offset())
        limit = watch.main(["--repo", str(self.repo), "status"])["parse_limit"]
        self.assertEqual((limit["oversized_rows"], limit["last"]["coordinator_output"], limit["row_bytes"]),
                         (1, False, 1024))

    def test_oversized_coordinator_row_is_reported_not_silently_dropped(self):
        self.append(self.big("assistant", 3000, "Handback: work is complete."))
        self.assertEqual(self.poll()["queue_calls"], 1)
        notice = self.codex.queues()[0][4]
        self.assertIn("parse-limit", notice)
        self.assertIn("exceeded the 1024-byte parsing limit", notice)
        self.assertEqual(self.poll()["queue_calls"], 0)

    def test_growing_partial_oversized_row_progresses_and_completes(self):
        row = self.big("assistant", 9000, "Plan is review-ready.")
        start = self.transcript.stat().st_size
        with self.transcript.open("a") as stream:
            stream.write(row[:2500])
        self.assertEqual(self.poll()["queue_calls"], 0)
        first = self.offset()
        self.assertEqual((first["offset"], first["oversized"]["start"], first["oversized"]["scanned"]),
                         (start, start, start + 2500))
        with self.transcript.open("a") as stream:
            stream.write(row[2500:8000])
        self.assertEqual(self.poll()["queue_calls"], 0)
        second = self.offset()
        self.assertEqual(second["oversized"]["start"], start)
        self.assertGreater(second["oversized"]["scanned"], first["oversized"]["scanned"])  # resumes, no reread
        self.assertLessEqual(second["oversized"]["scanned"] - first["oversized"]["scanned"],
                             watch.MAX_SCAN + watch.MAX_READ)                   # bounded work per poll
        with self.transcript.open("a") as stream:
            stream.write(row[8000:] + "\n")
        self.append(self.row("assistant", "Now blocked on a decision."))
        calls = 0
        for _ in range(4):
            calls += self.poll()["queue_calls"]
        self.assertEqual(calls, 2)  # one parse-limit report and the following milestone; no fragment records
        kinds = [c[4] for c in self.codex.queues()]
        self.assertTrue(any("parse-limit" in k for k in kinds) and any("(blocked" in k for k in kinds))
        self.assertEqual(self.offset()["offset"], self.transcript.stat().st_size)
        self.assertEqual(watch.main(["--repo", str(self.repo), "status"])["parse_limit"]["oversized_rows"], 1)

    def test_same_inode_truncation_below_pending_oversized_scan_recovers(self):
        row_start = self.transcript.stat().st_size
        with self.transcript.open("a") as stream:
            stream.write(self.big("user", 9000)[:5000])          # partial oversized row
        self.poll()
        scanned = self.offset()["oversized"]["scanned"]
        self.assertEqual(self.offset()["oversized"]["start"], row_start)
        self.assertGreater(scanned, row_start + 2000)                # the scan already passed the truncation point
        inode = self.transcript.stat().st_ino
        with self.transcript.open("r+") as stream:               # in-place truncation, same inode
            stream.truncate(row_start + 2000)
            stream.seek(row_start + 2000)
            stream.write("\n")                                   # ends the truncated fragment
        self.append(self.row("assistant", "Result submitted for Codex review."))
        self.assertEqual(self.transcript.stat().st_ino, inode)
        self.assertGreater(self.transcript.stat().st_size, row_start)
        self.assertLess(self.transcript.stat().st_size, scanned)
        calls = sum(self.poll()["queue_calls"] for _ in range(4))
        self.assertEqual(calls, 1)                                # delivered exactly once, eventually
        self.assertIn("review-ready", self.codex.queues()[0][4])
        self.assertEqual(self.offset()["offset"], self.transcript.stat().st_size)
        self.assertNotIn("oversized", self.offset())

    def test_rotation_clears_a_pending_oversized_row(self):
        with self.transcript.open("a") as stream:
            stream.write(self.big("user", 3000)[:2000])
        self.poll()
        self.assertIn("oversized", self.offset())
        rotated = self.transcript.with_suffix(".new")
        rotated.write_text(self.row("assistant", "Ready for review after rotation.") + "\n")
        os.replace(rotated, self.transcript)
        self.assertEqual(self.poll()["queue_calls"], 1)
        self.assertNotIn("oversized", self.offset())


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

    def test_default_interval_is_thirty_and_override_is_honoured(self):
        self.assertEqual(watch.DEFAULT_INTERVAL, 30)
        self.assertEqual(watch.parser().parse_args(["--repo", "x", "start"]).interval, 30)
        self.assertEqual(watch.parser().parse_args(["--repo", "x", "run"]).interval, 30)
        self.bind()
        directory = watch.observer_dir(self.root)
        with patch.object(watch, "child_argv", self.fake_child):
            for argv, expected in ((["start"], 30), (["start", "--interval", "45"], 45)):
                started = watch.main(["--repo", str(self.repo), *argv])
                record = watch.load(directory, "process.json")
                self.assertEqual((started["interval"], record["interval"], record["argv"][-1]),
                                 (expected, expected, str(expected)))
                self.assertEqual(watch.main(["--repo", str(self.repo), "stop"])["status"], "stopped")
                os.waitpid(started["pid"], 0)

    def test_start_stays_inactive_without_a_verified_pair(self):
        self.bind()
        self.status = {"status": "discovery-unknown"}
        with patch.object(watch, "child_argv", self.fake_child):
            result = watch.main(["--repo", str(self.repo), "start"])
        self.assertEqual((result["status"], result["reason"]), ("inactive", "coordinator-discovery-unknown"))
        self.assertIsNone(watch.load(watch.observer_dir(self.root), "process.json"))

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
