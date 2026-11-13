#!/usr/bin/env python3
"""Read-only completeness/binding check for private dispatch and handback records.

This does not execute tests or judge assertion semantics. It never grants authority.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def need(condition, message):
    if not condition:
        raise ValueError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def relative(value):
    need(text(value), "missing relative path")
    p = Path(value)
    need(not p.is_absolute() and ".." not in p.parts and p.parts, "unsafe relative path")
    return p


def bound_file(root, record, path_key="path", hash_key="sha256"):
    p = root / relative(record.get(path_key))
    need(p.resolve().is_relative_to(root.resolve()), "file escapes bound root")
    need(not any(x.is_symlink() for x in (p, *p.parents)), "symlinked evidence/source")
    need(p.is_file(), "missing bound file: " + str(record.get(path_key)))
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    need(digest == record.get(hash_key), "changed/unbound file: " + str(record.get(path_key)))
    return p


def validate(dispatch, handback=None, repo=None, evidence=None):
    need(isinstance(dispatch, dict), "dispatch must be an object")
    for key in ("objective", "role", "phase"):
        need(text(dispatch.get(key)), "missing " + key)
    need(re.fullmatch(r"[0-9a-f]{40}", str(dispatch.get("source", ""))), "unbound dispatch source")
    need(dispatch.get("unresolved") == [], "resolve design/dependency questions before writing dispatch")
    paths = dispatch.get("writable_paths")
    need(isinstance(paths, list) and paths, "missing exclusive writable paths")
    for path in paths:
        relative(path)
        need(not any(c in path for c in "*?[]"), "use exact writable files for this bounded dispatch")
    need(len(paths) == len(set(paths)), "duplicate writable path")
    cases = dispatch.get("required_cases")
    need(isinstance(cases, list) and cases, "missing named required cases")
    need(all(isinstance(c, dict) and text(c.get("id")) and text(c.get("expected")) for c in cases),
         "each required case needs an ID and observable expected behavior")
    ids = [c["id"] for c in cases]
    need(len(ids) == len(set(ids)), "duplicate required case")
    if handback is None:
        return {"ok": True, "scope": "dispatch-completeness", "required_cases": len(ids)}
    need(isinstance(handback, dict), "handback must be an object")
    need(handback.get("dispatch_sha256") == hashlib.sha256(
        json.dumps(dispatch, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "handback does not bind this exact dispatch")
    need(re.fullmatch(r"[0-9a-f]{40}", str(handback.get("source", ""))), "unbound handback source")
    outputs = handback.get("outputs")
    need(isinstance(outputs, list) and outputs, "no source artifact in handback")
    need(all(isinstance(o, dict) and o.get("path") in paths for o in outputs), "output outside write ownership")
    need(len(outputs) == len({o["path"] for o in outputs}), "duplicate output")
    for output in outputs:
        bound_file(repo, output)
    proofs = handback.get("cases")
    need(isinstance(proofs, list) and all(isinstance(p, dict) for p in proofs), "missing case proofs")
    need(len(proofs) == len(ids) and {p.get("id") for p in proofs} == set(ids),
         "missing, duplicate or unexpected required-case proof")
    incomplete = []
    for proof in proofs:
        need(proof.get("status") in ("passed", "failed", "not_run", "not_proven"), "unknown case outcome")
        if proof["status"] != "passed":
            incomplete.append(proof["id"] + ":" + proof["status"])
            continue
        need(text(proof.get("selector")), "missing executable selector")
        assertion = proof.get("assertion")
        need(isinstance(assertion, dict) and text(assertion.get("excerpt")), "missing assertion excerpt")
        p = bound_file(repo, assertion)
        need(assertion["excerpt"] in p.read_text(), "assertion excerpt absent from bound source")
        need(isinstance(proof.get("evidence"), dict), "missing outcome evidence")
        p = bound_file(evidence, proof["evidence"])
        need(text(proof["evidence"].get("excerpt")), "missing outcome excerpt")
        need(proof["evidence"]["excerpt"] in p.read_text(), "outcome excerpt absent from bound evidence")
    return {"ok": not incomplete, "scope": "handback-completeness-and-bindings",
            "incomplete": incomplete, "semantic_review_required": True}


def check_git_bindings(dispatch, handback, repo):
    git = ["git", "-C", str(repo)]
    head = subprocess.check_output(git + ["rev-parse", "HEAD"], text=True).strip()
    need(head == handback["source"], "checkout differs from handback source")
    subprocess.run(git + ["merge-base", "--is-ancestor", dispatch["source"], head],
                   check=True, capture_output=True)
    records = list(handback["outputs"])
    records += [p["assertion"] for p in handback["cases"] if p["status"] == "passed"]
    for record in records:
        relative(record["path"])
        blob = subprocess.check_output(git + ["show", head + ":" + record["path"]], stderr=subprocess.PIPE)
        need(hashlib.sha256(blob).hexdigest() == record["sha256"], "source file differs from claimed commit")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dispatch", type=Path, required=True)
    p.add_argument("--handback", type=Path)
    p.add_argument("--repo", type=Path)
    p.add_argument("--evidence-root", type=Path)
    args = p.parse_args()
    try:
        dispatch = json.loads(args.dispatch.read_text())
        handback = json.loads(args.handback.read_text()) if args.handback else None
        need(handback is None or (args.repo is not None and args.evidence_root is not None),
             "handback verification requires repo and evidence roots")
        result = validate(dispatch, handback, args.repo, args.evidence_root)
        if handback is not None:
            check_git_bindings(dispatch, handback, args.repo)
    except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError) as exc:
        result = {"ok": False, "scope": "unverified", "errors": [str(exc)]}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
