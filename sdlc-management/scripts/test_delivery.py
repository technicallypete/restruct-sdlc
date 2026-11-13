import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import subprocess

from check_delivery import validate, check_git_bindings


def sha(data):
    return hashlib.sha256(data).hexdigest()


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.code = b'func TestUpgrade() { assertReplayUnchanged() }\n'
        (self.root / 'proof.go').write_bytes(self.code)
        (self.root / 'run.log').write_bytes(b'TestUpgrade PASS\n')
        self.dispatch = {'source': 'a'*40, 'objective': 'prove genuine upgrade retry',
                         'role': 'test correction', 'phase': 'EP-2', 'unresolved': [],
                         'writable_paths': ['proof.go'],
                         'required_cases': [{'id': 'upgrade', 'expected': 'old request replays without writes'}]}
        self.handback = {'source': 'b'*40, 'dispatch_sha256': sha(json.dumps(
            self.dispatch, sort_keys=True, separators=(',', ':')).encode()),
            'outputs': [{'path': 'proof.go', 'sha256': sha(self.code)}],
            'cases': [{'id': 'upgrade', 'status': 'passed', 'selector': "go test -run '^TestUpgrade$'",
                       'assertion': {'path': 'proof.go', 'sha256': sha(self.code), 'excerpt': 'assertReplayUnchanged()'},
                       'evidence': {'path': 'run.log', 'sha256': sha(b'TestUpgrade PASS\n'), 'excerpt': 'TestUpgrade PASS'}}]}

    def run_check(self):
        return validate(self.dispatch, self.handback, self.root, self.root)

    def test_complete_dispatch_and_bound_handback(self):
        self.assertTrue(validate(self.dispatch)['ok'])
        result = self.run_check()
        self.assertTrue(result['ok'])
        self.assertTrue(result['semantic_review_required'])

    def test_no_artifact_is_not_a_successful_handback(self):
        self.handback['outputs'] = []
        with self.assertRaises(ValueError): self.run_check()

    def test_missing_duplicate_and_unknown_cases_rejected(self):
        for cases in ([], self.handback['cases']*2, [{'id': 'other'}]):
            self.handback['cases'] = cases
            with self.assertRaises(ValueError): self.run_check()

    def test_failed_unrun_and_unproven_never_become_pass(self):
        for outcome in ('failed', 'not_run', 'not_proven'):
            self.handback['cases'][0]['status'] = outcome
            self.assertFalse(self.run_check()['ok'])

    def test_missing_or_changed_evidence_is_rejected(self):
        (self.root/'run.log').write_text('different run')
        with self.assertRaises(ValueError): self.run_check()
        (self.root/'run.log').unlink()
        with self.assertRaises(ValueError): self.run_check()

    def test_assertion_must_exist_in_hash_bound_source(self):
        self.handback['cases'][0]['assertion']['excerpt'] = 'doesNotExist()'
        with self.assertRaises(ValueError): self.run_check()

    def test_outcome_excerpt_must_exist_in_bound_log(self):
        self.handback['cases'][0]['evidence']['excerpt'] = 'another test passed'
        with self.assertRaises(ValueError): self.run_check()

    def test_source_changes_invalidate_handback(self):
        (self.root/'proof.go').write_text('changed')
        with self.assertRaises(ValueError): self.run_check()

    def test_wrong_dispatch_binding_is_rejected(self):
        self.dispatch['required_cases'].append({'id':'second', 'expected':'reject explicit seats'})
        with self.assertRaises(ValueError): self.run_check()

    def test_unresolved_design_and_unbounded_paths_reject_dispatch(self):
        for field, value in (('unresolved', ['fixture unknown']), ('writable_paths', ['core/**']),
                             ('writable_paths', ['../outside']), ('required_cases', [])):
            dispatch = copy.deepcopy(self.dispatch); dispatch[field] = value
            with self.assertRaises(ValueError): validate(dispatch)

    def test_outside_output_and_symlink_evidence_are_rejected(self):
        self.handback['outputs'][0]['path'] = 'run.log'
        with self.assertRaises(ValueError): self.run_check()
        self.handback['outputs'][0]['path'] = 'proof.go'
        (self.root/'link.log').symlink_to(self.root/'run.log')
        self.handback['cases'][0]['evidence']['path'] = 'link.log'
        with self.assertRaises(ValueError): self.run_check()

    def test_committed_source_is_required_not_only_self_reported_hashes(self):
        def git(*args):
            return subprocess.check_output(['git', '-C', str(self.root), *args], stderr=subprocess.PIPE).decode().strip()
        git('init', '-q')
        git('add', 'proof.go')
        git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'fixture')
        self.handback['source'] = self.dispatch['source'] = git('rev-parse', 'HEAD')
        check_git_bindings(self.dispatch, self.handback, self.root)
        dirty = b'func TestUpgrade() { unrelatedAssertion() }\n'
        (self.root/'proof.go').write_bytes(dirty)
        self.handback['outputs'][0]['sha256'] = sha(dirty)
        self.handback['cases'][0]['assertion']['sha256'] = sha(dirty)
        with self.assertRaises(ValueError): check_git_bindings(self.dispatch, self.handback, self.root)
        self.handback['outputs'] = [{'path': 'untracked.go', 'sha256': sha(dirty)}]
        (self.root/'untracked.go').write_bytes(dirty)
        with self.assertRaises(subprocess.CalledProcessError): check_git_bindings(self.dispatch, self.handback, self.root)


if __name__ == '__main__': unittest.main()
