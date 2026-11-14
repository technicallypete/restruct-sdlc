import json
import tempfile
import unittest
from pathlib import Path
from check_token_controls import inspect, latest_usage

GOOD = {"env": {"CLAUDE_CODE_AUTO_COMPACT_WINDOW": "250000", "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "80"}}

class ControlsTests(unittest.TestCase):
    def test_valid_native_configuration(self):
        self.assertTrue(inspect(GOOD)["ok"])
    def test_missing_or_disabled_or_widened_settings(self):
        for config in [{}, {**GOOD, "env": {**GOOD["env"], "DISABLE_AUTO_COMPACT": "1"}},
                       {**GOOD, "modelSettings": {"opus": {"autoCompactWindow": 1000000}}}]:
            self.assertFalse(inspect(config)["ok"])
    def test_checkpoint_and_ceiling(self):
        for count, ok, due in [(199999, True, False), (200000, True, True), (249999, True, True), (250000, False, True), (656413, False, True)]:
            result = inspect(GOOD, {"input_context": count, "effort": "high"}, "high")
            self.assertEqual((result["ok"], result["checkpoint_due"]), (ok, due))
    def test_effort_mismatch_and_explicit_role_override(self):
        row = {"input_context": 70000, "effort": "xhigh"}
        self.assertFalse(inspect(GOOD, row, "high")["ok"])
        self.assertTrue(inspect(GOOD, row, "xhigh")["ok"])
    def test_missing_effort_is_not_verified(self):
        result = inspect(GOOD, {"input_context": 1}, "high")
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "unverified")
        self.assertEqual(result["errors"], [])
        self.assertFalse(result["blocked"])
        self.assertTrue(result["unverified"])
    def test_known_violation_wins_over_missing_effort(self):
        for settings, telemetry in [(GOOD, {"input_context": 250000}),
                                    ({}, {"input_context": 1})]:
            result = inspect(settings, telemetry, "high")
            self.assertEqual(result["status"], "blocked")
            self.assertTrue(result["blocked"])
            self.assertFalse(result["ok"])
    def test_cli_separates_unavailable_telemetry_from_bad_settings(self):
        import subprocess, sys
        with tempfile.TemporaryDirectory() as d:
            settings = Path(d)/"settings.json"
            trace = Path(d)/"worker.jsonl"
            trace.write_text("{}\n")
            cmd = [sys.executable, str(Path(__file__).with_name("check_token_controls.py")),
                   "--settings", str(settings), "--transcript", str(trace),
                   "--expected-effort", "high"]
            settings.write_text(json.dumps(GOOD))
            run = subprocess.run(cmd, capture_output=True, text=True)
            result = json.loads(run.stdout)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(result["status"], "unverified")
            self.assertFalse(result["ok"])
            self.assertEqual(result["errors"], [])
            settings.write_text("{}")
            run = subprocess.run(cmd, capture_output=True, text=True)
            result = json.loads(run.stdout)
            self.assertEqual(run.returncode, 1)
            self.assertEqual(result["status"], "blocked")
    def test_latest_usage_is_context_not_cumulative(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"t.jsonl"
            def row(n): return {"type": "assistant", "effort": "high", "message": {"usage": {"input_tokens": 2, "cache_creation_input_tokens": 8, "cache_read_input_tokens": n}}}
            p.write_text(json.dumps(row(600000))+"\n"+json.dumps({"type":"system", "subtype":"compact_boundary"})+"\n"+json.dumps(row(10000))+"\n{partial")
            self.assertEqual(latest_usage(p)["input_context"], 10010)
    def test_unknown_telemetry_refuses_verification(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"t";p.write_text("{}\n")
            with self.assertRaises(ValueError): latest_usage(p)
    def test_partial_usage_preserves_observed_ceiling_lower_bound(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"worker.jsonl"
            for usage, blocked in [({"input_tokens": 250000}, True),
                                   ({"input_tokens": 100000, "cache_read_input_tokens": 160000}, True),
                                   ({"input_tokens": 100000}, False)]:
                p.write_text(json.dumps({"type": "assistant", "effort": "high",
                                         "message": {"usage": usage}})+"\n")
                result = inspect(GOOD, latest_usage(p), "high")
                self.assertEqual(result["blocked"], blocked)
                self.assertEqual(result["status"], "blocked" if blocked else "unverified")
                self.assertFalse(result["ok"])

if __name__ == "__main__": unittest.main()
