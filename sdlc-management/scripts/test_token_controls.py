import json
import tempfile
import unittest
from pathlib import Path
from check_token_controls import inspect, latest_usage

GOOD = {"env": {"CLAUDE_CODE_AUTO_COMPACT_WINDOW": "200000", "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "75"}}

class ControlsTests(unittest.TestCase):
    def test_valid_native_configuration(self):
        self.assertTrue(inspect(GOOD)["ok"])
    def test_missing_or_disabled_or_widened_settings(self):
        for config in [{}, {**GOOD, "env": {**GOOD["env"], "DISABLE_AUTO_COMPACT": "1"}},
                       {**GOOD, "modelSettings": {"opus": {"autoCompactWindow": 1000000}}}]:
            self.assertFalse(inspect(config)["ok"])
    def test_checkpoint_and_ceiling(self):
        for count, ok, due in [(149999, True, False), (150000, True, True), (199999, True, True), (200000, False, True), (656413, False, True)]:
            result = inspect(GOOD, {"input_context": count, "effort": "high"}, "high")
            self.assertEqual((result["ok"], result["checkpoint_due"]), (ok, due))
    def test_effort_mismatch_and_explicit_role_override(self):
        row = {"input_context": 70000, "effort": "xhigh"}
        self.assertFalse(inspect(GOOD, row, "high")["ok"])
        self.assertTrue(inspect(GOOD, row, "xhigh")["ok"])
    def test_missing_effort_is_not_verified(self):
        self.assertFalse(inspect(GOOD, {"input_context": 1}, "high")["ok"])
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

if __name__ == "__main__": unittest.main()
