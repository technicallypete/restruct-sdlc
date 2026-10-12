# Closeout and risk reporting

Acceptance and cleanup are separate. Final ACCEPT completes a Goal; closeout then removes temporary resources
without losing unique work, live ownership or history.

## Verify before removing anything

Before removing a worktree, branch or in-flight marker, or closing a disposable merge request, verify:
- **Integrated content:** the integration branch contains the accepted changes (ancestry, or content and
  provenance reconciliation for rebased or squashed work).
- **Unique work:** no unmerged commits, dirty files or unpreserved evidence. Dirty work is reconciled or archived
  outside the checkout first; never force-remove it.
- **Live ownership:** no live session, process, validation run or required resource uses it. A live coordinator's
  directory is **never** deleted.

Then use `git worktree remove` for verified obsolete checkouts and `git worktree prune` for stale registrations.
Local branch deletion is separate; keep unique commits unless reconciled or archived. Close each disposable draft or
qualification merge request once nothing depends on it, keeping its discussion and pipeline links; a delivery
request that still carries unintegrated work stays open. Record removed paths, closed requests and retained
exceptions with reasons in the closeout record.

Clear an in-flight marker or lock only after verifying its owner ended; never clear another live run's marker.
Append a superseding status; never rewrite historical facts or turn withheld or failed evidence into a pass.

## Session records: archive before prune

Delivery records are private, machine-local and gitignored. After the supervisor or owner verifies a task's standing
terminal disposition from committed records, the companion helper's `compact` archives that task's whole delivery
groups into the private archive with a manifest, verifies it and only then prunes them from the live log (dry run
first; apply bound to the reviewed selection, from the main checkout, in a quiet window). Active, ambiguous, failed,
unconfirmed and incomplete records keep their bytes. Before removing a linked worktree, copy any worktree-local
delivery log byte for byte into the same archive and record both hashes. See
[claude-session-handoff](../../claude-session-handoff/SKILL.md) for exact commands and refusals.

## Progress compaction

After final ACCEPT and integration closeout, the supervisor assesses PROGRESS:
- keep one current entry per Goal with its disposition, acceptance and review links, dependencies, blockers and
  next gates;
- move superseded updates into a committed dated archive, `management/<release>/archive/PROGRESS-YYYY-MM-DD.md`
  (header template `templates/management/release/archive/PROGRESS-ARCHIVE.md.tmpl`), preserving original text,
  dates, decisions, failures and evidence references, and link it from PROGRESS;
- check moved links and anchors, adjusting relative references so they still resolve;
- if PROGRESS is a bound input of an active task, defer or notify that task's coordinator to reconcile before its
  next batch. Compaction alone never justifies another full test run.

## Risks and performance

Record risks in `docs/RISKS.md` (template `templates/docs/RISKS.md.tmpl`). Surface query, index, locking,
contention and other performance concerns there with the observed evidence, affected component and proposed
follow-up. Recording a concern does not impose a vendor-specific architecture and never authorizes silent tuning of
application code; changes go through a Goal.
