import unittest
from worker_progress_guard import transition, decision, worker_event

def batch(i, name="Read", text="ok"):
    return {"hook_event_name":"PostToolBatch", "tool_calls":[{"tool_use_id":str(i),"tool_name":name,"tool_response":text}]}

class GuardTests(unittest.TestCase):
    def test_read_loop_stops_before_next_model_call(self):
        s={}
        for i in range(39): s=transition(s,batch(i))
        self.assertNotIn("held",s)
        s=transition(s,batch(39));self.assertFalse(decision(s,batch(39))["continue"])
    def test_write_resets_budget_but_not_permission_refusal(self):
        s=transition({"without_artifact":39},{"hook_event_name":"PostToolUse","tool_name":"Write","tool_use_id":"1"});s=transition(s,batch(1,"Write"));self.assertEqual(s["without_artifact"],0)
        s=transition(s,{"hook_event_name":"PermissionDenied"})
        self.assertIn("held",transition(s,batch(2,"Write")))
    def test_duplicate_callbacks_do_not_consume_budget(self):
        s=transition({},batch(1));s=transition(s,batch(1));self.assertEqual(s["without_artifact"],1)
    def test_compaction_latch_does_not_reset(self):
        s=transition({}, {"hook_event_name":"PostCompact"})
        self.assertFalse(decision(s,{"hook_event_name":"PreToolUse","tool_name":"Read"})["continue"])
        self.assertIn("held",transition(s,batch(1,"Write")))
    def test_compaction_after_artifact_then_no_progress(self):
        s=transition({}, {"hook_event_name":"PostToolUse","tool_name":"Edit","tool_use_id":"1"});s=transition(s,batch(1,"Edit"));s=transition(s,{"hook_event_name":"PostCompact"});self.assertNotIn("held",s)
        s=transition(s,{"hook_event_name":"PostCompact"});self.assertIn("held",s)
    def test_refusal_in_batch(self):
        s=transition({},batch(1,"Bash","STOP what you are doing"));self.assertIn("native refusal",s["held"])
    def test_handback_remains_possible(self):
        self.assertEqual(decision({"held":"stop"},{"hook_event_name":"PreToolUse","tool_name":"SubagentHandback"}),{})
    def test_coordinator_excluded_worker_included(self):
        self.assertFalse(worker_event({"transcript_path":"/p/session.jsonl"}))
        self.assertTrue(worker_event({"transcript_path":"/p/subagents/agent-a.jsonl"}))


class FileHookTests(unittest.TestCase):
    def test_latch_survives_process_callbacks(self):
        import tempfile,json
        from pathlib import Path
        from worker_progress_guard import handle
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'agent.jsonl';p.write_text('{}\n')
            base={'agent_id':'a','session_id':'session','transcript_path':str(p),'tool_use_id':'pre'}
            for i in range(40): result=handle({**base,**batch(i)})
            self.assertFalse(result['continue'])
            self.assertFalse(handle({**base,'hook_event_name':'PreToolUse','tool_name':'Read'})['continue'])
            self.assertEqual(handle({**base,'hook_event_name':'PreToolUse','tool_name':'SubagentHandback'}),{})
    def test_unknown_or_symlinked_identity_is_not_trusted(self):
        import tempfile
        from pathlib import Path
        from worker_progress_guard import handle
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'real.jsonl';p.write_text('{}\n');q=Path(d)/'agent.jsonl';q.symlink_to(p)
            with self.assertRaises(ValueError):handle({'agent_id':'a','transcript_path':str(q)})
    def test_unconfirmed_write_does_not_reset_budget(self):
        s=transition({'without_artifact':39},batch(1,'Write'))
        self.assertIn('held',s)

class RefusalTests(unittest.TestCase):
    def test_source_text_discussing_refusals_is_not_itself_a_refusal(self):
        s=transition({},batch(1,"Read","1 docs: permission denied means stop what you are doing"))
        self.assertNotIn("held",s)
    def test_structured_native_refusal(self):
        from worker_progress_guard import native_refusal
        self.assertTrue(native_refusal([{"type":"text","text":"This agent is isolated in the worktree /p; refusing."}]))
    def test_malformed_event_cannot_pass(self):
        from worker_progress_guard import handle
        with self.assertRaises(ValueError):handle({})

class PersistenceTests(unittest.TestCase):
    def test_interrupted_replace_preserves_latch(self):
        import tempfile,json
        from pathlib import Path
        from unittest.mock import patch
        from worker_progress_guard import handle
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"agent.jsonl";p.write_text("{}")
            state=p.with_suffix(".restruct-progress.json");state.write_text(json.dumps({"held":"preserved"}))
            event={"agent_id":"a","session_id":"s","transcript_path":str(p),"hook_event_name":"PreToolUse","tool_name":"Read","tool_use_id":"pre"}
            with patch("worker_progress_guard.os.replace",side_effect=OSError("interrupted")):
                with self.assertRaises(OSError):handle(event)
            self.assertEqual(json.loads(state.read_text())["held"],"preserved")
    def test_empty_existing_state_and_missing_batch_fail(self):
        import tempfile
        from pathlib import Path
        from worker_progress_guard import handle
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"agent.jsonl";p.write_text("{}")
            event={"agent_id":"a","session_id":"s","transcript_path":str(p),"hook_event_name":"PostToolBatch"}
            with self.assertRaises(ValueError):handle(event)
            p.with_suffix(".restruct-progress.json").write_text("")
            with self.assertRaises(ValueError):handle({**event,**batch(1)})

if __name__ == "__main__": unittest.main()
