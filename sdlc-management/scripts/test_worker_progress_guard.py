import unittest
from worker_progress_guard import transition, decision, worker_event

def workerpath(root, ident="a", session="session"):
    from pathlib import Path
    p = Path(root) / session / "subagents" / ("agent-" + ident + ".jsonl")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{}\n")
    return p

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


class CheckpointTests(unittest.TestCase):
    def test_checkpoint_precedes_hard_stop(self):
        s = {}
        for i in range(29):
            e = batch(i)
            s = transition(s, e)
            self.assertEqual(decision(s, e), {})
        e = batch(29)
        s = transition(s, e)
        output = decision(s, e)["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "PostToolBatch")
        self.assertIn("checkpoint", output["additionalContext"])
        self.assertNotIn("held", s)
        self.assertEqual(s["without_artifact"], 30)
        for i in range(30, 39):
            e = batch(i, "SendMessage", "Still reading")
            s = transition(s, e)
            self.assertEqual(decision(s, e), {})
        e = batch(39)
        s = transition(s, e)
        self.assertFalse(decision(s, e)["continue"])

    def test_duplicate_callback_does_not_repeat_notice(self):
        e = batch("notice")
        s = transition({"without_artifact": 29}, e)
        self.assertIn("hookSpecificOutput", decision(s, e))
        s = transition(s, e)
        self.assertEqual(s["without_artifact"], 30)
        self.assertEqual(decision(s, e), {})

    def test_artifact_starts_new_stretch(self):
        s = transition({"without_artifact": 29}, batch("notice"))
        s = transition(s, {"hook_event_name": "PostToolUse", "tool_name": "Write", "tool_use_id": "draft"})
        s = transition(s, batch("draft", "Write"))
        self.assertEqual(s["without_artifact"], 0)
        self.assertNotIn("checkpoint_requested", s)
        for i in range(30):
            e = batch(i)
            s = transition(s, e)
        self.assertIn("hookSpecificOutput", decision(s, e))

    def test_batch_crossing_threshold_then_writing_has_no_stale_notice(self):
        s = transition({"without_artifact": 29}, {"hook_event_name": "PostToolUse", "tool_name": "Edit", "tool_use_id": "draft"})
        e = batch("read")
        e["tool_calls"] += batch("draft", "Edit")["tool_calls"]
        s = transition(s, e)
        self.assertEqual(s["without_artifact"], 0)
        self.assertEqual(decision(s, e), {})

    def test_parallel_batch_crossing_thirty_warns_once_and_forty_stops(self):
        e = batch("a")
        e["tool_calls"] += batch("b")["tool_calls"] + batch("c")["tool_calls"]
        s = transition({"without_artifact": 29}, e)
        self.assertEqual(s["without_artifact"], 32)
        self.assertIn("hookSpecificOutput", decision(s, e))
        s = transition({"without_artifact": 39}, e)
        self.assertFalse(decision(s, e)["continue"])

    def test_existing_refusal_takes_precedence(self):
        e = batch("notice")
        s = transition({"without_artifact": 29}, e)
        s = transition(s, {"hook_event_name": "PermissionDenied"})
        self.assertFalse(decision(s, e)["continue"])
        self.assertIn("native refusal", s["held"])

    def test_notice_and_counter_survive_separate_file_callbacks(self):
        import tempfile, json
        from worker_progress_guard import handle
        with tempfile.TemporaryDirectory() as d:
            p = workerpath(d)
            base = {"agent_id": "a", "session_id": "session", "transcript_path": str(p)}
            for i in range(30):
                result = handle({**base, **batch(i)})
            self.assertIn("hookSpecificOutput", result)
            self.assertEqual(handle({**base, **batch(29)}), {})
            self.assertEqual(handle({**base, **batch(30, "SendMessage", "checkpoint reply")}), {})
            state = json.loads(p.with_suffix(".restruct-progress.json").read_text())
            self.assertEqual(state["without_artifact"], 31)
            self.assertTrue(state["checkpoint_requested"])
            for i in range(31, 40):
                result = handle({**base, **batch(i)})
            self.assertFalse(result["continue"])


class FileHookTests(unittest.TestCase):
    def test_latch_survives_process_callbacks(self):
        import tempfile,json
        from pathlib import Path
        from worker_progress_guard import handle
        with tempfile.TemporaryDirectory() as d:
            p=workerpath(d)
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
            p=workerpath(d,session="s")
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
            p=workerpath(d,session="s")
            event={"agent_id":"a","session_id":"s","transcript_path":str(p),"hook_event_name":"PostToolBatch"}
            with self.assertRaises(ValueError):handle(event)
            p.with_suffix(".restruct-progress.json").write_text("")
            with self.assertRaises(ValueError):handle({**event,**batch(1)})

class WorkerIsolationTests(unittest.TestCase):
    def test_parent_callbacks_do_not_share_latches_or_budgets(self):
        import tempfile,json
        from pathlib import Path
        from worker_progress_guard import handle
        with tempfile.TemporaryDirectory() as d:
            parent=Path(d)/"session.jsonl";parent.write_text("{}")
            a=workerpath(d,"a"); b=workerpath(d,"b")
            base={"session_id":"session","transcript_path":str(parent)}
            for i in range(40): result=handle({**base,"agent_id":"a",**batch(i)})
            self.assertFalse(result["continue"])
            self.assertEqual(handle({**base,"agent_id":"b",**batch("b1")}),{})
            self.assertEqual(json.loads(b.with_suffix(".restruct-progress.json").read_text())["without_artifact"],1)
            self.assertIn("held",json.loads(a.with_suffix(".restruct-progress.json").read_text()))
    def test_parent_and_direct_callbacks_share_one_worker_state(self):
        import tempfile,json
        from pathlib import Path
        from worker_progress_guard import handle
        with tempfile.TemporaryDirectory() as d:
            parent=Path(d)/"session.jsonl";parent.write_text("{}")
            p=workerpath(d)
            base={"session_id":"session","agent_id":"a"}
            handle({**base,"transcript_path":str(parent),**batch("1")})
            handle({**base,"transcript_path":str(p),**batch("2")})
            self.assertEqual(json.loads(p.with_suffix(".restruct-progress.json").read_text())["without_artifact"],2)
    def test_missing_worker_trace_cannot_create_a_fresh_allowance(self):
        import tempfile
        from pathlib import Path
        from worker_progress_guard import handle
        with tempfile.TemporaryDirectory() as d:
            parent=Path(d)/"session.jsonl";parent.write_text("{}")
            with self.assertRaises(ValueError):
                handle({"session_id":"session","agent_id":"a","transcript_path":str(parent),**batch(1)})
            self.assertEqual(list(Path(d).rglob("*.restruct-progress.json")),[])
    def test_legacy_shared_state_is_preserved_and_requires_review(self):
        import tempfile
        from pathlib import Path
        from worker_progress_guard import handle
        with tempfile.TemporaryDirectory() as d:
            parent=Path(d)/"session.jsonl";parent.write_text("{}")
            p=workerpath(d)
            legacy=parent.with_suffix(".restruct-progress.json");legacy.write_text('{"held":"keep"}')
            for path in (parent,p):
                with self.assertRaises(ValueError):
                    handle({"session_id":"session","agent_id":"a","transcript_path":str(path),**batch(1)})
            self.assertEqual(legacy.read_text(),'{"held":"keep"}')
            self.assertFalse(p.with_suffix(".restruct-progress.json").exists())
            legacy.unlink()
            legacy.with_suffix(".lock").touch()
            for path in (parent,p):
                with self.assertRaises(ValueError):
                    handle({"session_id":"session","agent_id":"a","transcript_path":str(path),**batch(2)})
    def test_wrong_id_session_and_traversal_are_rejected(self):
        import tempfile
        from worker_progress_guard import handle
        with tempfile.TemporaryDirectory() as d:
            p=workerpath(d)
            for ident, session in (("b","session"),("a","other"),("../a","session")):
                with self.assertRaises(ValueError):
                    handle({"session_id":session,"agent_id":ident,"transcript_path":str(p),**batch(1)})
    def test_child_path_without_agent_id_uses_verified_basename(self):
        import tempfile
        from worker_progress_guard import handle
        with tempfile.TemporaryDirectory() as d:
            p=workerpath(d)
            self.assertEqual(handle({"session_id":"session","transcript_path":str(p),**batch(1)}),{})

if __name__ == "__main__": unittest.main()
