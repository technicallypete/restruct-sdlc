# Validation and integration

## Epic integration branches

Unless the owner directs otherwise for an epic or task, create a dedicated epic
integration branch from the current staging tip (or the repository's configured
long-lived integration target). Record the branch, baseline and target in the
existing epic records. Give each Goal/task its own work branch or worktree and
target its MR at the epic branch. Review and qualify child MRs under the existing
rules against that target. A child merge lands on the epic branch and its proof
can inform subsequent tasks.

Open one epic MR from the epic branch to staging **as the final epic task is
finishing**, once the composed candidate is reviewable. Use Draft while final
work is pending. Review and CI can overlap with the last task. Reconcile any
final source and staging changes, confirm the final task is integrated and the
epic's required reviews and validation are satisfied before merging. Reuse
attributable unchanged checks and select coverage for the actual composed delta.
This branch strategy uses the existing CI and release rules.

Child tasks clean up at their own acceptance. Start the final
[epic cleanup audit](closeout-risks.md#epic-integration-branch-cleanup) when the
epic MR opens or reaches readiness. Verify child cleanup against actual
resources, then finish reclaiming epic-owned integration resources and removing
the epic branch after merge and release of its live uses. Preserve existing
active branch bindings and runs when adopting the default.

**Epic integration qualification.** Unless the owner directs otherwise, start
the full local suite when the epic integration MR to staging (or its configured
equivalent) opens with a reviewable candidate. If it opens before the composed
candidate is ready, start at readiness. The coordinator freezes the exact
candidate and staging baseline, runs qualification in an isolated checkout,
and records the evidence in the existing Plan/Result. Review can proceed in
parallel. Reconcile changes from the tested candidate through merge and run
affected checks, reusing attributable passes. Child feature/task MRs into the
epic branch retain focused pre-merge checks and affected post-merge checks.
This default applies to future epic integration MRs and preserves explicit
qualification choices and active run bindings.

## Post-merge qualification runs locally

Default sequence for implementation MRs: focused pre-merge checks and current hosted fast/supervisor/Duo review → authorized merge → affected local batches/suites on the exact merged integration SHA. The existing implementer coordinator automatically launches, owns and tracks those selected checks; no extra owner command or full pre-merge gate. Select from the actual change and integration delta, including affected dependencies, shared fixtures, migrations, disabled variants and security boundaries. Record executable selectors and coverage rationale in the existing Plan/Result; preserve immutable inputs, actual outcomes and cleanup. Final Goal ACCEPT requires that attributable affected coverage and the other Goal gates, rather than a blanket full run per feature.

Outside the epic MR default, run full local qualification on the integration branch tip when the owner requests it **or the supervisor recommends it**, recording the reason and freezing the exact observed tip for the run. Full staging runs and full hosted RC-promotion runs provide broader opportunities to find gaps in feature selection; unexecuted checks are never reported as passing. Ordinary feature MRs retain hosted fast checks; RC promotion MRs retain required full hosted qualification. Automatic integration/release-branch post-merge and tag-push pipelines remain disabled, including lightweight checks; separately authorized diagnostic/provider runs remain distinct.

After a failure, rerun the failed checks and checks affected by the fix, reusing attributable unchanged passes. A broad local selection needs a concrete coverage reason; explicit technically justified full-run requirements remain binding. Reconcile active work at a safe boundary without restarting running batches or rewriting approved snapshots. Ready authorized successor implementation may overlap post-merge checks in isolation, respecting resource reservations; predecessor final ACCEPT still gates successor integration/final acceptance. Preserve owner holds, manual/security gates, documentation-only exemptions and failure history. This supersedes the blanket full-local-run-after-every-feature default.

## Ordinary feature registration does not require full CI controls

Routine product work may update product-specific assertions and test registration
inside shared validation scripts: permitted routes/imports, migration versions,
schema/catalog inventories, browser scenario matrices, test invocations, required
check IDs and expected totals in control fixtures. These edits do not by themselves
change the generic runner's execution behavior or invalidate every control.

For such changes, exclude the full `ci-controls` suite from ordinary feature
qualification. Run the affected application/security/migration checks and the
specific control cases whose inputs, assertions or expected totals changed, using
the existing focused selector. Record the changed guarantee and exact selector in
the existing Plan/Result. Reuse attributable unaffected passes. A harness pathname,
a copied fixture, mechanical registration/count-pin changes, or a missing full-suite
PASS row is not justification for selecting every control.

Changes to shared execution semantics (dispatch/profile selection, gate enforcement,
process supervision, isolation, resource accounting/cleanup or evidence handling)
require their affected control cases. The supervisor may select the whole control
suite only with a concrete recorded dependency/coverage reason explaining why the
focused set is insufficient. Do not replace that analysis with "harness changed".
An explicitly requested/recommended full staging run and required full hosted RC
qualification retain their complete coverage.

Required-check accounting does not create a new coverage requirement merely to
obtain an aggregate PASS: select checks from actual impact first. In adapters where
`B-CI-CONTROLS` represents the entire suite, do not select that umbrella suite just
to satisfy its own row; preserve focused control evidence in the existing Result.
Report an unexecuted suite as unexecuted, never as PASS. A genuine adapter limit
needs a bounded stated remedy/disposition; it must not silently force every feature
through the entire control suite. Apply this rule before the first qualification
run and when reviewing remaining selections at a safe boundary.

## Owner mandate and stop bounds

Check [recorded mandates/stops](roles-lifecycle.md#bounded-specification-authority-and-owner-stop-boundaries)
before every continuation. A ready Spec/accepted Plan or green pipeline does not
override an owner stop. Do not start successor lookahead while finishing the
endpoint task's CI/closeout. Auto-specification needs explicit bounded owner
authority; an epic mandate neither expands membership nor resets Goal budgets.

## Planning overlap

At planning and dispatch boundaries, default to [safe parallel batches](coordination.md#default-to-safe-parallel-work-lanes)
when their dependencies, ownership, bound inputs and resource reservations permit.
Finish → diagnose/fix → rerun → advance applies within each dependency chain;
unrelated safe batches may proceed while a failed batch and its dependents are held.
Do not parallelize an intentionally ordered proof or conflicting shared resources,
mutate a frozen validation source, or bypass task-specific sequencing/required gates.

At the first predecessor implementation MR (drafts included), apply
[automatic planning](roles-lifecycle.md#automatic-planning-after-integration)
for the next eligible existing Goal/Spec; integration is fallback discovery only. Provisional planning may overlap CI,
acceptance and cleanup. Implementation may overlap predecessor staging CI after
reviewed source integration and supervisor release under the policy below. Do not reserve the shared test
stack or repeat predecessor validation merely to write the next Plan.

## Reassessment and execution release

After reviewed predecessor source is merged, automatically reassess the
provisional Plan; permit isolated implementation during its affected local qualification using [the release policy](roles-lifecycle.md#automatic-reassessment-and-execution-release).
Material Plan changes require bounded implementer updates and review; unchanged
design requires reconciliation only. Verify every execution gate and record/
relay the supervisor release before work, without another routine owner prompt.
Predecessor final ACCEPT still gates successor integration/final acceptance. A failed
predecessor gate pauses affected work only. The predecessor implementation owner
keeps its staging repairs and attempt ledger, working in parallel with the successor;
do not shift repair responsibility to successor workers. Preserve separate resources. Use existing binding and focused validation; no unchanged full rerun for a SHA.

## Git-first provenance

For new work, Git is the source of truth for committed code and management
artifacts. Bind reviewed inputs by repository, commit and path; record the tested
candidate and fetched target commit in the Result. A commit identifies bytes, not
approval or passing tests. Check for relevant tracked/untracked changes before
claiming a run tested that commit; commit scoped implementation checkpoints before
final qualification rather than building another source-tracking framework.

Record actual commands, outcomes (including failures/interruptions), relevant tool
versions, image IDs/digests and non-secret runtime configuration references in a
compact Result. Link required CI jobs and selected proof artifacts. Git does not
capture external runtime inputs or establish what executed.

Snapshot/hash only relevant inputs not identified by Git: reviewed uncommitted
changes, external configuration/fixtures or mutable artifacts. Preserve necessary
bytes when verification or a dependent task needs them; a hash alone is not
recoverability. Use existing secret-safe private handling for credentials; never
commit secrets. Do not inventory/hash every committed file again, archive whole
checkout copies or create a parallel evidence registry by default.

Retain compact attributable outcomes and necessary proof, then use the existing
closeout policy to purge disposable local bulk output. Do not erase failed-run
history or treat a changed commit SHA alone as reason to repeat unchanged tests.

This default applies to new Goals/Plans. Existing approved snapshots, wrappers,
retention rules and exact input bindings remain required unless explicitly amended
and reviewed; active work is not silently rebound or replanned. Security/authority,
acceptance, rebase, CI and resource-safety gates are unchanged.

## Early focused feedback and fixture prerequisites

At the first coherent source checkpoint, run relevant inexpensive compile,
type/lint and focused unit checks before expensive database/browser validation.
Use the existing commands and evidence; do not repeat an unchanged pass merely
for this rule or require every check after every commit. The writer may execute
only within its released native/resource permissions. If it is source-only,
the existing coordinator owns prompt static feedback through the authorized
validator and existing reservations; "source-only" must not leave this step
until the end of combined integration validation. Repair static failures before
dependent expensive batches; unrelated safe lanes remain runnable.

For selected browser/integration cases, inspect and bind fixture prerequisites
in the existing dispatch/packet. Establish the required setup directly or select
its exact supported prerequisite chain, including sign-in and role/state changes.
Check a setup mutation's actual expected response before waiting for its UI
consequence; an unexpected refusal fails promptly with bounded diagnostic output
that preserves privacy. Keep the existing overall timeout, authorization negatives
and required coverage. Do not waive failures, silently broaden to a whole suite
or introduce another fixture framework/approval stage.

## Coherent review slices and executable coverage closure

Use the existing Plan contracts, AC map and phase handback to close a coherent
producer/consumer behavior. Include settled semantics, actual caller/fixture
state, implementation, directly affected checks and executable registrations.
Check the required ID, actual runner invocation, lane inventory and child/count
pins together when a check changes; a source test file alone does not put it in
CI. Reconcile omissions at coherent checkpoints rather than discovering them
only during final MR preparation. Map behavior to actual assertions and outcomes;
a missing label is not a new coverage gap, and a differently named PASS is not
proof without equivalent assertions. Keep deferred/failed cases visible until
attributable evidence closes them.

Batch related source corrections and cheap checks on one frozen coherent slice
where ownership permits. Do not turn every child assertion or mechanical pin
into a new worker, DB run or supervisor permission round. The coordinator handles
already-authorized mechanical fixes and verifies exact conditional-review recipes;
formal source/architecture/security reviews and native refusals retain their
existing gates. New or unresolved contract decisions still need the owning review.
Independent ready lanes continue while a dependent proof or review waits.

Before costly selected UI runs, resolve fixture roles, current/default object
semantics, dates, navigation and HTML-versus-rendered-text expectations from the
actual path. Reuse existing helpers and cheap checks; this adds no fixture
framework, mandatory smoke campaign or extra stage. When a failure is confined
to test setup/assertion mechanics, preserve it, correct the cause and rerun failed
or affected checks while retaining attributable unchanged passes. Distinguish
implementation time from setup/build, execution and review/queue cost in the
existing Result when explaining churn. Apply at safe boundaries; never rebind
frozen runs, waive required coverage or retrospectively expand accepted tests.

## Feasibility before expensive expansion

For nontrivial changes, planning and Plan review identify assumptions that could
invalidate the approach, using existing source, fixtures and prior measurements.
Put the smallest relevant feasibility check in the first released implementation
slice, with concrete success/failure criteria in the existing Plan/AC map. Where
applicable prove actual query access/work bounds (including sparse/duplicate and
reused-connection cases), fixture construction cost, and a working measurement
example before expanding maximal fixtures or dependent UI. Reuse sufficient prior
proof; routine changes need no artificial spike or new approval stage. Planning
alone authorizes no runtime experiment, and this creates no separate test campaign.

At handback, the coordinator checks actual assertions, fixture prerequisites,
selectors and registration/count pins against the operative AC map before
launching dependent expensive runs. The supervisor checks the same at the existing
review. A named test, touched file or aggregate pass is not evidence for a missing
assertion. Resolve omissions in one bounded correction, keeping attributable
passes; a genuine design/contract change follows existing review and scope gates.
Apply only to the remaining delta at a safe boundary, without restarting accepted
work, rebinding frozen runs or releasing held successors.

## Realistic test scope and independent Spec review

For new Specs and substantive validation expansions, choose representative product
scenarios and risk-proportionate coverage. A technical ceiling alone does not
justify repeatedly materializing maximum-scale fixtures in routine integration.
Tie expensive scale, concurrency and combination cases to a concrete product,
correctness, security or bounded-work requirement; prefer the smallest fixture
that proves that requirement. Do not invent large product limits merely to make
validation finite. Unresolved product limits remain owner decisions.

Before accepting a supervisor-authored Spec that introduces or materially expands
tests, obtain one bounded independent read-only subagent review explicitly covering
test reasonableness and cost. Reuse the existing Spec reviewer with this remit
where possible, rather than adding another reviewer or approval stage. Give it the
proposed requirements/ACs, intended product usage, relevant limits and attributable
prior timings. It checks fixture realism, duplicated assertions/matrices, total
parent cost and whether rare maximum-scale checks need routine execution. Preserve
necessary boundary/security guarantees; an expensive justified case is not grounds
to silently remove its assertion or reduce an accepted maximum.

Record the findings and supervisor disposition in the existing Spec validation
section or review. The supervisor remains accountable for scope and acceptance.
If delegation is unavailable, record the limitation and perform an explicit second
pass directly; do not leave authorized work idle. No runtime benchmark, new review
artifact, approval chain or monitoring agent is required for this assessment.

Estimate aggregate runtime including fixture construction, process/list/build
startup, selected children and cleanup on the intended runner. Flag unexplained
30+ minute routine parents before planning approval and apply the prospective
parent-runtime guidance below. Partitioning improves visibility but does not reduce
total work: also avoid redundant fixture rebuilding and speculative combinations.
Cite comparable measurements or mark estimates/unknowns; do not run experiments
merely to fill a Spec timing field. Justified costly coverage may use a separately
selected scale check under the existing CI/owner policy, without silently dropping
required qualification.

This guidance is prospective only. It does not change current tests/assertions,
product limits, approved coverage, timeout settings or frozen inputs; it releases
no retrospective test cleanup or optimization task. Reconcile substantive future
changes through the normal owner/Spec/Plan process.

## Parent runtime budgets and existing baselines

Default planning/review ceiling for a new or substantially expanded reported
parent check is **15 minutes (900 seconds)** on its intended runner. Include
parent-specific fixture/setup, all selected children and teardown attributable
to it. Report shared bootstrap/build phases separately; do not hide parent work
there. Whole jobs/suites may be longer when composed of independently reported
parents; a per-Go-command timeout alone does not bound a visible harness parent.

Preserve existing approved long parents and their recorded budgets/baselines,
including 20–30-minute checks. This is not a retrospective timeout reduction,
mass split or reason to reject an unchanged legacy parent. Material new coverage
must not silently enlarge a grandfathered parent: split the new work or review
its runtime impact. A genuinely indivisible new parent needing more than 15
minutes requires a specific owner-approved variance, not an automatic timeout bump.

In the existing Spec/Plan validation mapping, cite attributable completed-run
timings with source/fixture version, runner/environment, setup/child time where
available, sample count and measured versus estimated status. Reuse retained
timings, test reports and job traces; completion gaps are estimates and concurrent
events cannot be subtracted as if sequential. Keep local/hosted and cold/warm
baselines distinct. Missing data is unknown, not a fabricated default or a new
benchmark campaign; validate it in the smallest already-authorized early slice.

If a new parent is predicted/measured above budget, optimize its setup or split
it into meaningful independently selected/reported parents with exact required
coverage, failure attribution and cleanup. Renaming an umbrella while leaving
the same silent long-running parent does not satisfy the rule. Preserve unique
boundary assertions and fixture isolation; do not shrink maxima or skip security
checks solely to meet the budget. Review any required-check/selection/aggregation
changes together so required coverage is neither lost nor duplicated.

Emit event-driven parent/child start, end and elapsed/setup progress as appropriate
using the existing reporting paths; retain unfinished/failure evidence. A quiet
aggregate log alone does not establish a hang. Implement deadline/reporting
changes through normal reviewed source work; do not mutate frozen runs, lower
existing timeouts, cancel jobs or restart tests merely to adopt this guidance.
No polling agent, new telemetry framework or separate inventory is required.

## Before every batch

A batch is a named group of local checks (focused tests, builds, lint, controls, full runs). Before launching each
batch on a temporary Goal branch:

1. Fetch the remote target (`origin/<INTEGRATION_BRANCH>`).
2. Assess the exact fetched target delta against tested behavior, check dependencies,
   fixtures/contracts, build/runtime configuration, external inputs and required evidence,
   plus the task's authority, dependencies, approved bindings and governance. If all are
   demonstrably unaffected, record target range/candidate/reason in the existing Result
   and defer rebase/input reconstruction. Otherwise rebase/reconcile before testing.
   Unknown impact follows reconciliation. Preserve dirty work and immutable bindings;
   never rewrite a protected branch or change a running test's checkout.
3. Run `PRE_BATCH_ENV_CHECK` when configured; if it fails, do not launch.
4. Record target and candidate SHAs and the binding provenance with the batch evidence.

Read-only Git, input-integrity and resource-safety inspections may precede the rebase. No redundant rebase when the
target has not moved. Always reconcile before final qualification and again before
MR opening, rerunning affected checks only. No directory-wide management/skills exemption.
Existing approved active contracts retain their required sequence until explicitly amended.

## Reuse existing coverage during planning

### Early risk review and short correction loops

Use the existing Plan and review, rather than another checklist artifact:

- Review changed trust boundaries first: what can a malicious tenant, domain/DNS
  owner or credential holder now control, capture or replay? Check global identity
  separately from credential authority. Include affected migration/legacy-row,
  revocation and downgrade behavior when durable security state changes.
- Order approved implementation to prove the riskiest end-to-end path and its
  principal denial early, before surrounding features. Use existing fixtures and
  a thin functional slice; no planning-time build/probe or extra test campaign.
- For nontrivial changes, distinguish settled design decisions from unproven
  assumptions in the existing Plan. Name the highest-risk assumption, the smallest
  executable proof and its success/failure criteria; reuse existing evidence when
  sufficient. Run that proof early in approved implementation before building the
  surrounding solution. Planning remains inspection-only unless execution was
  separately authorized; routine changes need no artificial spike or extra gate.
- Give executable validation selectors, dependency order and independent parallel
  batches. Estimate implementation effort separately from elapsed build/test time
  and review/queue waits. Cite available timings or mark estimates/unknowns honestly;
  identify required resource slots, serial builds and safe overlap. These are compact
  planning estimates, not guarantees or a new measurement/benchmark campaign.
- Keep execution inside the approved scope. A material addition needs a bounded
  delta stating its design, timing, resource, validation and budget effects, with
  the applicable approval before affected implementation. Defer unrelated extras;
  do not absorb them silently into an active task or reset its attempt ledger.
- If an early proof fails or execution materially exceeds the estimate, checkpoint
  the cause and remaining work in the existing Result. Distinguish coding/rework,
  validation elapsed time and coordination/waiting using available evidence; mark
  unavailable timings unknown. Review a bounded correction or justified split
  rather than repeating the whole Plan or adding more process. Implementation
  need not take less time than planning; repeated surprises require reassessment.
- Inventory affected callers, schema/version/count pins and actual executable
  selectors during planning using bounded searches. Include necessary paths in
  the approved touch-list; discovered design/scope gaps still stop affected work
  for review, rather than granting unrestricted file access.
- Keep a worker on a bounded coherent phase, with the existing context checkpoint
  and compact handoff at safe boundaries. Do not rotate useful workers merely
  per phase, forward entire transcripts or restart attributable tests/budgets.
- Diagnose and rerun the failed selector first. Reuse unchanged passing evidence;
  broaden only for a concrete changed dependency/guarantee under the existing
  supervisor exception rule. No broad run just for a fresh wrapper PASS.
- Batch related findings from the current bounded review into one actionable
  correction handoff with the guarantee, relevant files and minimum evidence.
  Consolidate available independent findings; do not serialize avoidable nudges
  or delay an urgent security hold waiting for unrelated review completion.

Apply these as improvements to existing execution, not a new approval stage,
mandatory phase-agent scheme, monitoring system, separate timing report or
framework. For active work, assess only the remaining delta at a safe boundary;
do not restart completed planning or running validation to satisfy this guidance.

Before proposing tests, inspect the relevant existing suites and fixtures. In the
Plan's existing validation/AC mapping, cite test paths or check IDs and distinguish
**reuse**, **extend**, and **new** coverage. State the actual uncovered behavior or
regression that each new case proves; prefer extending the existing fixture/test
at that boundary. One existing test may cover several acceptance criteria.

Do not clone a suite/fixture, rebuild an accepted invariant or add Goal-named
checks merely to give the new task its own evidence. Similar scenarios at distinct
boundaries (for example policy unit, runtime RLS and browser integration) may be
necessary: explain the distinct failure each catches. The supervisor requests a
bounded correction when proposed duplication has no such justification.

Record this in the normal Plan, not a new inventory/framework or planning-time
test campaign. Relevant regressions and required local/hosted/security coverage
remain mandatory; reuse of earlier passing results still requires reconciliation
of actual changed code, dependencies and runtime inputs. Test reuse is not a waiver
of current validation, manual feedback or evidence requirements.

## Proportionate coverage

Committed test/approval inputs use Git commit/path. Unconsumed status documents
need no duplicate test snapshot; approval/governance changes still require review.
Size local coverage to changed behavior, required security criteria and the actual
path/profile selection. Hosted staging is path-selected, docs-only pipelines may
be omitted, and cancellation is not passing-test evidence. Keep required local
coverage and honest failed/interrupted records; reuse unchanged attributable evidence.
The expensive CI meta-tests are distinct from application tests and may be selected
only for affected CI/harness/control dependencies; dependency and wrapper controls
remain separate obligations. Unknown dependencies select CI meta-tests. Existing
approved snapshots and Goal validation requirements are not silently waived.

## Finish, fix, rerun, advance

Within a batch, let ordinary failures finish collecting results. At the boundary, preserve every outcome and verify
owned cleanup. Gather all outstanding failures, fix them, rerun failed cases/controls and checks affected by the fixes,
then advance. Keep an outstanding-findings checklist in the Result. Unsafe or invalid work (resource or security
failures, corrupted evidence, fail-closed gates) stops immediately; dependent checks that cannot run are recorded as
blocked or skipped, never passing.

## Order of work

implementation → reconcile → focused checks → **required manual tests and operator feedback** → resolve findings
and repeat affected checks → reconcile again → push and open the merge request → hosted fast checks and required
supervisor/Duo review → authorized merge → final qualification at the configured placement. Under the default
`local-after-merge` placement, the coordinator runs affected local batches/suites on the exact merged integration SHA;
it is not a full pre-MR gate. An adopting owner may explicitly select another placement in the repository's
parameters. Final qualification never starts while required feedback is pending. Evidence is reused only for
unchanged relevant content and inputs, with recorded provenance; a changed commit SHA alone does not demand an
unchanged full rerun.

## Live review against design mocks

**Sequence mixed backend and frontend tasks by dependency.** Use the usual workflow for backend implementation, focused tests and review. In the Spec, identify the data, actions, permissions and states the frontend needs. In the Plan, choose the order for each affected screen family and give a short reason. By default, implement and check the backend behavior first, then run the dependent frontend work and visual loop as the final implementation phase. Specify the smallest backend milestone that makes the real state available to the writer.

A family may start in parallel when its required contract and behavior are already stable and accessible in an authorized live preview. For example, a list can be polished while an unrelated worker changes a background job. A new approval state must be exercisable before its screen can be verified, even if the API shape stays the same. Carry forward attributable pairs and recheck only affected screens when backend and frontend are composed. A mock or stub can inform preparation; final comparison exercises the actual behavior. Backend-only tasks follow the usual workflow.

When a frontend task’s Spec identifies design mocks, the Plan assigns each in-scope screen family to one implementation writer. Identify the mock revision, frame or state, applicable viewports and a way to reach that state in the working app. Families can run in parallel within the agreed capacity. Give shared components one owner and check the affected consumers together.

Group related states into families that a writer can exercise in the same flow or preview, such as a list, detail and edit screen. A design inventory batch can cover several families, and a family can draw from several batches. Retain the original frame IDs for coverage. If a shared fix affects several families, its owner coordinates the change and each affected writer verifies their screens.

In the existing Plan or Result, report visually closed frames out of applicable frames **for each family**. Count each distinct frame once in the overall total, including frames referenced in several batches. A frame closes on a verified match or an explicitly accepted difference under the task’s acceptance rules. Link the evidence and name what remains. Track MR status separately. Move each reviewable family through the task’s normal MR process as soon as its own dependencies and checks clear. Assign available writers to the next ready family while review runs.

1. At the first ready screen, open the reference beside the real app. Use the project’s hot-reload workflow on the writer’s checkout with an owned or authorized backend, isolated browser state and safe fixtures. Confirm that saving an actual UI edit updates the open page without rebuilding the app. Use the same role, data state, viewport and theme as the mock. If hot reload or a required state is unavailable, report the exact blocker to the coordinator. Agree on a supported alternative explicitly if needed.
2. The writer inspects the initial screenshot, makes a targeted edit, resets the page state when needed, exercises the affected control and inspects the refreshed screenshot beside the mock. Repeat until the screen matches. Save a sanitized live/reference pair for every in-scope frame and drawn viewport, with the source, state and any residual difference in the existing Plan or Result. Use the writer’s own comparison during editing and group independent review and focused committed-source checks at the task or MR boundary. Reuse the confirmed pairs for the MR gallery.
3. Stop as soon as a frame matches. The default ceiling is **15 correction rounds per frame**, unless the task specifies another limit. One round is an edit followed by a fresh visual comparison. The initial comparison can close an already matching frame with zero rounds. A shared correction can cover several frames in the same round when each is compared. Escalate earlier if repeated edits show no progress or a fixture, behavior or permission decision is needed.
4. At the ceiling, leave the row open. Send the coordinator the latest pair, rounds used, remaining discrepancy and the next change worth trying. The coordinator requests clearance from the supervisor for **up to five additional rounds** before further corrections to that frame. Record the decision and revised ceiling. Any further extension requires another explicit decision. Existing Goal, time, usage and permission limits still govern. Inner visual rounds use the Goal’s existing attempt accounting.
5. At a handoff or compaction, carry the family owner, current frame and source, preview or blocker, latest pair, round count, approved ceiling and next action in the existing handoff. Resume the same work at its next safe boundary. Let frozen runs finish and reuse attributable pairs. Keep a mismatch open until corrected or an explicit acceptance decision covers it. Independent families can advance meanwhile.

### Screen, family and integration checkpoints

At the end of a screen’s live review loop, the writer updates its existing evidence row with the mock frame ID, reached state, viewport, source revision and final live/reference pair. Record the next action for each unresolved difference.

At family review, the supervisor checks coverage of every applicable state and viewport, the screenshot pairs, the results for affected interactions and the decisions covering any accepted differences. Record the family verdict in the existing review record and MR when applicable. Lead owner updates with the family verdict, gallery and remaining named gaps. Report at acceptance or earlier when a blocker or decision needs attention.

After integration, verify that the merged revision contains the reviewed changes. Link the merge SHA and attributable evidence in the existing receipt. If integration or a later shared edit changes a screen’s appearance or behavior, reopen that comparison and refresh its affected evidence. Carry forward evidence for unchanged screens. Track release or staging qualification separately. These records supply the resume point after a session restart.

## Frontend UX merge-request screenshots

For changes that alter visible frontend UX, include a compact screenshot gallery
in the merge-request description. The implementer/coordinator owns the gallery:
upload representative actual-application captures through the configured provider
and embed them, normally desktop and phone for responsive changes, with the affected
state/panel open when relevant. Reuse captures from selected validation; do not add
a separate screenshot campaign, per-page/theme matrix or new suite solely for the
gallery. Frontend changes with no visible effect may state that briefly instead.

For mock-driven work, use the family MR gallery as the owner's spot-check point.
Place each representative live capture beside its corresponding design frame and
label both sides. Identify the mock revision and indicate whether the live image
comes from the current MR head or an earlier commit. When owner feedback changes
a screen, refresh that pair in the same MR and briefly say what changed so the
owner can verify the correction in place.

Caption the captured source commit, viewport, theme and meaningful state; identify
fixture/seed variants and link the existing Result/proof for the full inventory.
Before review/merge, refresh materially affected images when the candidate changes,
or establish that their relevant bytes/inputs are unchanged. Mark preliminary or
superseded images honestly; a Draft may identify pending captures without claiming
visual acceptance. Keep older evidence in the Result rather than growing a stale
gallery. Use authorized synthetic/sanitized states and omit credentials, private
user/customer content and internal runtime details from uploaded images.

Screenshots support human review; they do not replace functional/accessibility
checks or constitute mock-parity acceptance. If capture/upload is unavailable,
record the concrete limitation and existing evidence link for supervisor disposition,
without bypassing native/security gates or adding another owner approval stage.

## Integration

- **Safekeeping pushes.** After each implementation or correction round, commit scoped work and push a checkpoint
  to the temporary branch. A checkpoint opens no merge request and authorizes nothing.
- **Reviewed integration.** After the supervisor's pre-integration review, check the target again; if it advanced,
  rebase and rerun only affected checks. Push and open the merge request to `INTEGRATION_BRANCH` with source-branch
  deletion enabled. Before merging, inspect outstanding automated review findings and unresolved threads; passing
  CI does not dispose of them. Follow the adopting owner's recorded integration mode; see
  [staging auto-merge](#owner-selected-staging-auto-merge).
- **Promotion** from `INTEGRATION_BRANCH` to `RELEASE_BRANCH` uses a separate merge request that **retains** the
  source branch. Long-lived branches (`PROTECTED_BRANCHES`) are never deleted or rewritten.
- **Cleanup after merge or MR closure.** After a merge, verify the accepted target content and exact remote source tip; after an MR closes without merge, verify that it is unmerged, no other open MR or live task uses the branch, and unique commits/evidence are integrated or durably preserved in existing records, a tag, retained ref or bundle. Then delete only the exact task-owned disposable source branch. MR closure is not acceptance and does not justify deleting unique unpreserved work. Preserve long-lived/protected branches, immutable tags and failure evidence.
- **Target advances.** When the integration branch advances, the supervisor assesses the delta against every active
  task: unaffected work continues; relevant changes reconcile at a safe boundary; conflicts pause immediately.
  Interrupted tests stop, reap owned children, preserve evidence and release locks before any rebase.

## Options

| Option | Values | Meaning |
|---|---|---|
| `FINAL_VALIDATION_PLACEMENT` | `local-after-merge` (default) | Fast/supervisor/Duo review, then merge; existing coordinator automatically owns affected local qualification of the exact integrated SHA. Full local runs on the integration tip are owner-requested or supervisor-recommended. No automatic post-merge cloud pipeline; staging MR checks and explicitly configured release/diagnostic qualification remain. |
| | `mr-hosted` | Explicit adopting-owner alternative: full coverage hosted before merge. |
| | `local-before-mr` | Legacy explicitly selected alternative; not the current post-merge default. |
| `CANCELED_PIPELINE_SATISFIES` | `false` (default) | Final validation needs `success`. |
| | `true` | An owner-canceled post-merge pipeline also satisfies the gate. It is recorded as canceled, never as passing, and any failed job or known failing check still fails. Pending or running never qualifies. |

## GitLab/glab adapter (`CI_PROVIDER=gitlab`, `MR_TOOL=glab`)

```sh
git fetch origin || exit 1                                       # stop: never rebase against stale refs
git merge-base --is-ancestor origin/INTEGRATION_BRANCH HEAD || git rebase origin/INTEGRATION_BRANCH
git push origin HEAD:refs/heads/TEMP_BRANCH                      # safekeeping checkpoint
glab mr list --source-branch TEMP_BRANCH --target-branch INTEGRATION_BRANCH   # avoid a duplicate MR
glab mr create --source-branch TEMP_BRANCH --target-branch INTEGRATION_BRANCH \
  --title "TITLE" --description "Evidence: see the Goal Result." --remove-source-branch --yes
glab mr view MR_IID --comments                                    # automated review findings before merge
glab mr merge MR_IID --auto-merge --sha REVIEWED_SHA --remove-source-branch --yes # when owner policy authorizes
git fetch origin INTEGRATION_BRANCH                              # freeze the merged SHA for coordinator-owned affected local qualification
glab mr create --source-branch INTEGRATION_BRANCH --target-branch RELEASE_BRANCH --title "Promote"
```

For the promotion request, confirm that source-branch deletion is **off**; a project-wide deletion default also
applies to that target, so check the setting rather than assuming the target changes it.

A published, owned temporary branch that must be rebased is pushed with an exact expected-tip
`--force-with-lease=TEMP_BRANCH:<old-sha>`, never an unconditional force. Hosted quota exhaustion is a resource
stop, reported as such.

## Owner-selected staging auto-merge

An adopting owner may set all non-promotion MRs targeting the integration branch
to auto-merge once required supervisor review, applicable Duo review/findings
disposition, target/input reconciliation, required pre-merge evidence and
manual/owner holds are clear. Record the policy in the repository's live
governance and branch runbook. When enabled, this is standing integration
authority; do not request another routine merge prompt. Early/draft MRs may
record the intent but cannot arm it until every gate clears. A specific owner
hold or opt-out takes precedence. Reassess on any new source commit or blocking
finding. This policy does not apply to integration-to-release/RC promotion MRs,
release tags, final Goal ACCEPT or post-merge qualification. GitLab may merge
immediately when native checks are already green, so verify every repository
review/evidence gate before enabling auto-merge.


## Owner-controlled RC promotion option

When an adopting owner selects release-candidate qualification, use this release flow: owner requests an annotated SemVer RC at the reviewed integration snapshot → coordinator internally opens a temporary tag-pinned source branch/MR to the release branch → that MR runs mandatory complete hosted qualification → owner-authorized promotion (manual after success by default, or explicit owner-selected auto-merge) → verify integrated content and remove only the temporary source branch, or remove it after the MR is closed without merge once the RC tag and all pass/failure evidence are preserved → owner separately decides when to create the final release tag. The temporary branch is provider plumbing, not another owner-managed step; retain long-lived branches, immutable RC tags and qualification evidence. Closing an unqualified/failed promotion MR never promotes or qualifies the RC.

For this option, RC/final tag pushes and release-branch pushes start no automatic pipeline. Admit the promotion MR even for documentation-only candidates and make its full coverage required rather than optional/manual. Verify actual tag object/peeled commit, MR source, complete project/pipeline/job/artifact coverage and prospective/actual integrated content. A branch-name prefix or green partial report is insufficient. Present target-movement checks honestly; do not claim an atomic target guarantee the provider does not support. Never create the final tag automatically from merge success.

The adopting owner may explicitly waive Duo/automated review for this promotion of already integrated content; record the confined waiver and preserve ordinary feature-review, security/manual acceptance and source-proof gates. It grants no general review bypass or project-wide permission change. Keep normal coordinator-owned local-after-merge integration qualification separate. The adopting CI/provider adapter must implement and verify this option before use; these instructions alone do not install tag/MR rules or authorize a concrete release.

### Standing authority within an owner-authorized RC series

When an owner authorizes a named RC series, or directly requests its next
candidate, that authorization covers bounded coordinator work for the series
without per-step or per-candidate reconfirmation: diagnose and repair
qualification failures within already approved scope, integrate repairs through
normal staging review and merge gates, create the next sequential immutable RC
tag from the configured integration branch's latest commit observed at cut
time, open the tag-pinned promotion MR, and run required full qualification.
Preserve every failed run and its evidence. A failed qualification is never
waived or represented as passing; after an in-scope repair, the coordinator may
continue with the next candidate under the same series authority. An owner
instruction given to the supervisor remains authoritative when faithfully
relayed to the coordinator; do not require the owner to repeat it in another
session. Existing scope, budget, security, architecture, and escalation stops
remain binding. This standing series authority does not authorize merging the
promotion MR to the release branch, arming auto-merge without its separate
owner selection, creating a stable release tag, or deploying/publishing a
release. Those remain separate owner decisions.

## Autonomous mechanical repair

Apply [mechanical-correction authority](roles-lifecycle.md#autonomous-mechanical-corrections):
fix in-scope selectors, fixtures, approved-value catalog/count/version pins and
harness/import bookkeeping directly after diagnosis. Preserve assertions, negative
controls, scope and frozen inputs; record the focused failing/affected evidence in
the existing Result. No approval round, replan or new worker solely for such fixes.
Security/contracts, scope, unapproved production schema/constraints, budget and
native gates still escalate; full hosted retry authority is unchanged.

## Validation economy and recurring failures

Before a batch, choose the smallest checks covering the actual change and required
security/shared boundaries. During diagnosis run the failed scenario and adjacent
cases first; expand only for affected dependencies, unresolved failures or required
final coverage. Reuse valid unchanged evidence with source/input provenance. Do
not create another benchmark, harness proof campaign or duplicate full run merely
for a new SHA or policy edit. Existing path selection and Goal requirements govern.

A passing retry does not establish a root cause or prove a flake fixed. Inspect
failure output first. Under standing integration authority, the supervisor may
approve one retry of the failed job for an evidenced transient/unrelated failure,
within the existing Goal budget; retain both outcomes and record the hypothesis.
No blind repeated retries, whole-pipeline rerun when one job suffices, or treating
an unknown failure as unrelated. A recurrence requires focused diagnosis and a
bounded repair/disposition before another retry. Scope/security/budget and native
permission stops still apply; repeated-issue escalation remains in force.

On GitLab, for non-executable workflow-prose publication only, the supervisor may
use `git push -o ci.skip` after reviewing the entire staged delta and verifying no
application, tests/fixtures, executable scripts/templates, CI selectors, dependency
or runtime inputs changed. Markdown filename or management/skills location alone
is insufficient. Record the exact skipped publication and reason; skipped is not
passing and cannot satisfy or erase a required application staging gate. Unknown
impact follows normal CI. This exception does not change the path selector.

Cancel a superseded duplicate hosted run only after verifying the newer run covers
its exact changes and required suites, the older run has no failed required check,
and no independent qualification depends on it. Record both pipeline IDs and the
cancellation; preserve failed-run evidence and the still-required qualification.


## Preserve local validation evidence before cleanup

Use an explicit private evidence directory for every local qualification or repair run.
Before temporary cleanup, retain the scanned report: check ledger, detailed failing
suite/control logs, supplemental JUnit and relevant diagnostics, bound to the tested
commit and command. Verify those files remain readable after finalization before
retrying, handing back or closing the run. Preserve both failed and later outcomes;
raw logs and generated secrets still follow existing scans and secret cleanup.
If scanning withholds detail, retain only the safe marker/summary and record the
specific evidence gap; never copy unsafe raw files to defeat withholding. Distinguish
JUnit wrapper/aggregate/phase failures from underlying failing test IDs. If a wrapper
cannot retain diagnostics, report and repair that gap before another diagnostic run;
do not solve it with repeated full suites. Regress retention with a failed local run
and prove unsafe or unscanned evidence is still withheld. Purge retained reports only
under the existing terminal-task evidence cleanup policy.

## Complete repair inventory and supervisor verification

Before opening a staging/integration repair MR, reconcile every non-passing
required check across the task's failed runs, including earlier failures not
re-executed later. In the existing Result, record check/scenario, pipeline/job,
failing candidate, correction or evidenced disposition, and attributable passing
proof or remaining hold. Read suite logs as well as summaries; aggregate failures
must point to their underlying failures. Account for skipped/interrupted/canceled
checks without calling them product failures or passes. No entry may be silently
omitted or assumed cleared by a later subset.

Prove affected corrections with the smallest executable selector on the actual
candidate/inputs; a passing underlying test does not clear its failed wrapper or
pin. Derive pin expectations from actual catalog/output and inspect all affected
consumers. Reuse unchanged valid evidence after relevant-delta reconciliation.
If local proof is genuinely unavailable, use the existing supported pre-merge
integration entrypoint and require its success before merging; document why that
broader run is necessary. Do not default to a full suite or use post-merge staging
to discover whether an unproven repair works. Opening the necessary MR to access
its pre-merge job is distinct from merging it.

The supervisor independently compares that inventory with the failed artifacts,
verifies evidence attribution and records repair completeness before pre-integration
ACCEPT. Distinguish fixed/pass, unresolved, not rerun with valid evidence reuse,
derived aggregate and explicitly authorized retry/disposition. An unavailable
artifact, non-execution or timing hypothesis is not a pass. The existing one-job
retry rule still applies: retain both outcomes; recurrence needs focused diagnosis
and a bounded repair, not repeated unchanged runs. A passing retry does not prove
a root cause or repair. Final acceptance and post-integration gates remain.

Use existing Result/review records, one current failure inventory and existing
owners/budgets. No new tracking framework, duplicate full validation, retroactive
pass or permission bypass. Apply equally when the supervisor reviews its own
workflow/CI changes: inspect the actual delta and required self-checks.

## Theme-aware browser coverage

Choose and record one repository-defined primary theme for comprehensive browser
workflows. Run theme-independent permissions, authentication, CRUD, payload,
pagination, idempotency and state-transition matrices once in that theme. Do not
multiply every functional scenario by each supported palette merely because
themes exist. The reusable workflow chooses no particular primary palette.

Retain coverage in every supported theme for theme selection/persistence/system
preference, first paint and hydration, contrast and focus indicators, visibility
and control states, overlays/portals, native controls, theme-dependent assets and
charts, responsive layout and representative critical interactions. Preserve
mixed functional/visual cases when they uniquely cover those states; a case title
without an accessibility label does not establish that its second-theme pass is
redundant. Shared theme/component changes may justify wider paired regressions;
record the actual affected guarantee rather than a default full cross-product.

Use existing project selectors/tags and Plan/Result mapping to explain retained
second-theme coverage and functional coverage in the primary theme. Keep shared
test definitions and all assertions; remove redundant project expansions rather
than adding blanket skips, expected failures or artificial PASS rows. Reconcile
discovery counts, required IDs, probe/report consumers, project dependencies and
documentation together through normal source review. Unselected cases are not
passing cases. Theme changes do not isolate shared server data: fixture ownership
and state preconditions remain mandatory across projects.

Apply a changed selection at a reviewed source boundary. Frozen runs retain their
original matrix and failure history; do not cancel, rewrite or retrospectively
qualify them using a later selection. Required full hosted qualification still
runs the complete accepted matrix. This rule waives no security, release, native
permission, budget or acceptance gate and adds no separate approval framework.

## Focused selection before the first run

Focused checks are the default for **every local run**, including initial
implementation, corrections and final local qualification. Start with changed
behavior and required technical guarantees, then choose the smallest existing
package/test filters, service checks, browser projects and integration entrypoints
that cover them. Inspect what the command actually runs; a narrow task name or
"focused batch" label does not make an umbrella command narrow.

Before Plan approval and before launching a batch, the supervisor/coordinator
checks the proposed executable selectors against that scope. Reject unexplained
`all`, generic unit/migration/ops suites or full control suites when they include
unaffected work. Prefer supported filtered/direct existing test commands; record
coverage and required setup in the normal Plan/Result, without a new checklist,
manifest, test wrapper or reporting stage. Reuse valid attributable prior passes.

A broad local run is an exception requiring a concrete technical reason and
supervisor disposition **before launch**: for example a changed shared boundary,
a specified indivisible guarantee, or an identified unresolved dependency impact.
State what wider coverage is needed and why the narrower checks cannot establish
it. Existing reviewed Plan justification can supply that disposition; do not ask
again for an unchanged approved exception. Tool convenience, "to be safe", a fresh
wrapper PASS, or an unavailable narrow harness selector alone is not justification.
If selection is unavailable, report the exact limitation once and propose the
smallest safe existing command for supervisor disposition; do not automatically
fall back to the broad suite or modify the harness to add another framework.

If an overbroad run is already active, retain completed evidence and narrow its
remaining work at a supported safe boundary with owned cleanup. Required schema
setup, real affected regressions and atomic/global guarantees remain; never mark
unexecuted checks passed. Mandatory hosted MR/integration jobs retain their actual
configured scope. This is local selection policy, not permission to skip required
CI, weaken security evidence or change budgets. Apply to active tasks at the next
safe boundary; reassess inherited umbrella selections without a full replan.

### Change-impact selection before merge

Owner direction, 2026-10-18: choose local checks from the consequences of a
change, not only its feature/package directory. In the existing Plan validation
mapping, use bounded searches of the actual diff, callers and CI/harness selectors
to connect each affected guarantee to an existing executable check. Consider only
applicable dependencies: shared authentication/authorization fixtures; historical
migration paths and upgrade/down preconditions; schema/catalog/version/count pins;
startup imports and disabled-feature/copy variants; and concurrent or timing-sensitive
paths. Extend existing coverage only where it leaves a concrete gap.

For schema/migration changes, explicitly inspect applicable shared reset/cleanup
helpers, upgrade/Down ladders, schema/catalog/version/count/ACL expectations and
dependent test fixtures, including older-feature consumers. Record the actual
selected runner's starting database/fixture state in that same map: a migrated
CI template, empty database and historical upgrade fixture are different inputs.
Use the relevant state for focused proof; an empty-database pass does not establish
that reset from the migrated template works. Select only states affected by the
change, not an automatic matrix or new full-suite campaign.

For changed request contracts, include test callers that bypass the UI (direct
service/raw calls, forced HTTP posts and replay/security fixtures). Supply or
assert the required current/captured tuple, provenance and actor context so a
negative test reaches its intended refusal rather than failing an earlier setup
or parsing gate. Derive expected transition values from the actual fixture; a
column's initial default may change during setup. Preserve exact status, reason,
no-write and permission assertions; do not loosen them merely to obtain a pass.

The coordinator checks that mapping before the first affected batch and refreshes
it for material implementation or integration deltas. Codex reviews coverage of
those effects, not merely whether the selected commands look narrow. Reconcile
against the actual target integration before merge; run newly affected checks or
cite attributable unchanged evidence. A known omitted impact must be resolved
before merge, rather than delegated to staging discovery. Record a real harness
limitation and the smallest justified exception under the existing selection rule.

This is smarter selection within the current Plan/Result, not another inventory,
approval stage, mandatory matrix or broad local suite. Preserve running batches
and assess remaining active work at its next safe boundary; no full replan or
rerun of completed unaffected work. Report exactly what passed locally and what
any separately authorized provider qualification covers. The required combined staging qualification now runs locally on the exact merged revision; it is not inferred from hosted fast checks. Record its actual local environment and coverage.

## Targeted reruns and attributable coverage default

After failures, rerun the smallest failed case/control and checks affected by the
fix. Reuse unrelated passing results with unchanged relevant code, schema,
fixtures, dependencies, configuration and runtime inputs. A suite, batch or job
name is not itself a reason to repeat every case. CI/harness self-tests follow
the same dependency rule; ordinary feature work does not automatically invalidate
the entire control suite. Unknown impact or a real shared dependency requires
broader relevant coverage, with the reason recorded.

Complete local coverage may combine earlier attributable passes and later focused
reruns. Record the original/rerun source and input provenance and outstanding IDs
in the existing Result/review, not a new registry or aggregation framework. Never
rewrite failed/canceled runs as successful, synthesize a full-pass report or use
an older pass to conceal a new substantive failure. Preserve known root-cause
uncertainty; a passing retry does not prove a flake fixed. Required atomic/global
checks still need their actual evidence, and required hosted jobs remain unchanged.

If a rerun is unnecessarily broad, preserve its completed outcomes and use
supported cancellation at a safe case/control boundary with owned cleanup; do not
interrupt unsafe-to-stop work or declare unexecuted cases passed. Required coverage
and unresolved failures remain gates. No full restart solely for a new SHA,
management edit, wrapper tally or clean summary when attributable coverage suffices.

When implementation is frozen, perform bounded read-only source review in
parallel with independent validation. Label preliminary source findings honestly;
final acceptance still waits for the Result, reconciled code/inputs, required
checks and automated-review findings. Review later changes as deltas rather than
repeating the unchanged source review. Preserve the current task, owner and budget.

Apply this default to active tasks at the next safe boundary and future tasks;
it supersedes generic wording to rerun an entire failed batch. If a specific Goal
needs one indivisible run for a technical guarantee, preserve that guarantee and
record the bounded exception. This policy adds no script, test stage or monitor.


## First failure requires intervention — 2026-10-18

Each required GitLab MR pipeline has one explicitly named monitoring owner,
normally the coordinator, recorded with the MR/pipeline ID and immutable source
SHA when the MR is opened or the pipeline is created. The owner verifies the
expected pipeline started, tracks it to a terminal outcome, reports the outcome,
and routes the first failure for diagnosis. The Claude session watcher observes
coordinator-session notices; it does not monitor GitLab MRs, pipelines or jobs.
A general task assignment, watcher notice, review request or auto-merge setting
is not evidence that a pipeline has an active monitor. If ownership changes,
record a direct handoff and acknowledgment so monitoring has no gap. Keep updates
event-driven and concise; do not send repeated unchanged status polls. Auto-merge
does not replace monitoring or alter review/merge authority. Before another
CI-triggering push, the owner checks the previous outcome and records the
pipeline, SHA, failed job/test and correction owner in the existing Result.
The supervisor acts on a reported blocker/failure promptly instead of waiting for
a final handback. A failed CI run is executed-and-failed evidence even when local
execution was blocked; never summarize that state as tests not executed.

On the first failure, inspect its available log and run the smallest reproducer.
Do not repeatedly push or retry unchanged known-failing source to rediscover the
same error. The next validation run must test a specific correction or an evidenced
retry hypothesis within existing authority. Keep independent work and safekeeping
authority; explain an unavoidable checkpoint-triggered run rather than treating
it as another diagnostic attempt. Do not suppress required CI for application
changes or erase failed evidence. Existing MR supersession handles redundant runs.

On the first native permission refusal, separate configuration/resource scheduling
from product security: report the exact refused operation and propose the narrow
supported remedy immediately. The authorized operator uses existing owner authority to correct
workflow/configuration where authorized; ask only for genuinely missing authority.
Verify an actual successful tool call. Do not repeatedly dispatch blocked workers,
require owner-run commands by default, or compensate with repeated CI runs.
Keep isolation and real security/permission boundaries; this is prompt diagnosis
and supported configuration, not permission to evade a native refusal.


## Isolated checks and shared resource locks

Where the adopting repository uses a shared harness lock, apply it to shared
mutable resources, not automatically to every container command. Focused unit or
static checks can run without that lock with read-only source and prepared
read-only dependency caches, disposable per-run writable build/temp state, no
network, database/Compose stack, published ports or shared mutable fixtures.
Dependency downloads/shared cache preparation and integration/browser stacks
retain their existing resource locks. Use supported native commands and keep
worker isolation, bounded resource ownership, cleanup and source/input attribution.
This scheduling distinction neither changes test expectations nor waives required
hosted checks, security evidence, task scope or native permissions.


## Owner-selected RC auto-merge — 2026-10-19

The owner may explicitly enable auto-merge for a named RC promotion MR or a clearly recorded scope of RC MRs. Manual promotion remains the default when no such instruction exists. This owner instruction authorizes queuing promotion before CI finishes; once every required full-qualification job succeeds, the provider may merge without another owner prompt. Record the owner instruction, MR, immutable source SHA and selected mode. Before arming, verify the tag/source identity, required complete pipeline, non-squash merge, and conflict-free prospective target tree equal to the RC tree; source-pin the request. Preserve target-movement monitoring and post-merge parent/tree verification without claiming an atomic target lock. Retain and independently verify full project/pipeline/job/artifact proof before claiming qualified release. No failed, skipped, optional or partial coverage counts as qualification. Do not fabricate manual-mode proof or change API snapshots to satisfy a verifier. A manual-only helper's refusal of queued/merged MRs is a mode limitation, not a passing auto-mode proof; use truthful independent verification or a separately reviewed mode-aware adapter. Final release tagging remains a separate owner decision. Feature-MR auto-merge defaults alone never authorize an RC-to-release merge.


## Optional RC Duo review and planned follow-ups — 2026-10-19

RC promotion MRs may use Duo as optional advisory review; Duo is not a required promotion approval gate. Triage every actionable finding and record its disposition in the existing release Result/review. Changes arising from that review must be scheduled and planned as bounded follow-up work: identify the responsible Goal/task or backlog item, intended milestone, scope, acceptance criteria and required focused validation under normal authority. Do not leave actionable recommendations only in an MR comment or silently claim them fixed. Do not change the code or move/recreate an existing RC tag to satisfy a review. If a follow-up changes the release candidate or must ship before promotion, integrate it through the normal staging workflow, then cut and fully qualify a new RC tag under the applicable release authorization. The owner may instead retain a documented prerelease follow-up while the current RC proceeds. Preserve ordinary feature-MR Duo requirements, required full RC CI, security/owner dispositions, selected auto/manual merge mode and the separate final-tag decision. This policy creates no automatic RC2, unbounded repair mandate or new tracker.


## Owner-waived canceled RC qualification — 2026-10-19

The owner may explicitly cancel a named RC promotion MR's pipeline and direct that cancellation to satisfy the current RC promotion gate, treating it as success for the workflow decision only. Record an owner-authorized qualification waiver with the RC/tag/source SHA, MR/pipeline IDs, actual canceled/partial/failed job states, any known findings and the owner's instruction. Never report the canceled pipeline or unexecuted tests as PASS, fabricate green evidence, erase prior failures or claim complete qualification. This exception is specific to the named candidate/pipeline; it is not the default cancellation policy for feature MRs or other RCs. Schedule a follow-up immutable RC tag to run the complete required suite, carrying forward unresolved findings and the qualification debt in the existing release Result/backlog/Plan. The follow-up RC's full suite is required unless the owner separately changes that instruction. The owner may choose this waiver alongside the recorded auto/manual promotion mode; provider auto-merge still depends on the provider's actual cancellation behavior. If existing provider rules prevent merging a canceled pipeline, report that concrete limitation rather than changing project-wide protections, manufacturing a success job or treating a queue as a completed merge. No pipeline is canceled merely because this option is documented, and final release tagging remains separately owner-controlled.


## RC source selection at cut time

For an owner-authorized RC cut, fetch the configured integration branch and tag
its latest remote commit observed at cut time (using the adopting repository’s configured branch). Do not
require an older acceptance/review SHA or exclude later integrated documentation
or implementation merely because it arrived after the cut was requested. No
additional owner confirmation or documentation-only ancestry check is needed
solely because staging advanced. An explicitly owner-pinned source or release
content exclusion still takes precedence.

Record the selected full commit SHA/tree and create the immutable annotated RC
tag there. A concurrent later staging push belongs to a later candidate; never
move the tag to chase it. The promotion branch/MR and required full qualification
use that exact tagged source. This source-selection rule does not accept pending
Goals, waive findings/CI, authorize an unrequested RC/main merge/final tag or
change the selected promotion mode. Existing tags and pipelines stay unchanged.


### Private per-run database test scheduling

Focused database tests may omit the shared harness lock when every run owns its
database, private network, credentials and disposable storage; publishes no host
ports; mounts source and prepared dependency caches read-only; and shares no
writable fixtures/cache or existing stack. Use plain supported native commands,
unique resource names/labels, exact run ownership and verified bounded cleanup.
Network access is limited to that run's test services. No alternate executor or
hidden wrapper may evade a native refusal.

Default to at most **two concurrent private database runs per adopted repository**,
across its coordinator and workers. A third needs explicit owner approval when
asked; do not infer higher concurrency. Reuse the existing coordinator/run
inventory for slot ownership; verify live runs before dispatch, release slots
after cleanup and queue on uncertain ownership. No extra scheduler is required.
The adopting owner may explicitly choose a different recorded limit.

This exception applies across tasks and supersedes blanket database-stack locking
only for qualifying private runs. Shared image builds, mutable cache preparation,
Compose/browser stacks, shared ports/data/fixtures and other shared mutations
retain their locks. Unavailable pinned images remain a separate preparation
blocker; do not substitute unpinned images or claim unexecuted tests passed.
Task scope, validation coverage, source binding, budgets and native guards remain.


### Private browser runs and sequential image builds

Private browser runs (including fully private Compose stacks) share the adopted
repository's private database-test concurrency pool: default **two total test
runs**, a third only with explicit owner approval. Count a browser stack and its
internal database once. Each run owns project/names/labels, containers, network,
credentials and writable storage/fixtures; mounts source and prepared caches
read-only; and reuses no live stack. Required host ports must be uniquely reserved,
nonconflicting loopback ports, never shared fixed ports. Record slots/resources,
exact tested source and verified cleanup. These qualifying runs omit the shared
harness lock; shared stacks/ports/data/fixtures retain their existing lock.

Image builds are **sequential, one at a time across the repository's coordinator
and workers**, including individual images in a multi-service build. Reserve one
build slot through the existing coordinator/run inventory, verify current owned
builds, queue on uncertain ownership and release on completion. A private build
can use native plain Docker commands without the harness lock under this exclusive
reservation: task-owned tags, bound context, disposable outputs, no active-tag
replacement or shared writable-cache preparation. Shared cache preparation/other
shared mutations retain their lock. Third-test-run approval does not expand build
concurrency. No extra scheduler, executor, hidden wrapper or native-check bypass.
Reconcile live work at a safe boundary without restart, budget reset or coverage
waiver. This supersedes earlier blanket browser/Compose/build locking only for
qualifying private reserved operations. Adopting owners may explicitly override
limits; preserve the recorded choice and real native permission boundaries.

## Descriptive release artifacts

Keep tag names canonical SemVer. Every new annotated tag message and GitLab
Release entry lists included Goal/task IDs and short titles, material changes
since the preceding candidate/release, and the exact source commit. Final
release notes summarize delivered scope since the previous stable release and
state qualification truthfully; never imply planned or unaccepted work shipped.
Published tags are immutable: improve an existing GitLab Release entry rather
than moving or recreating a tag.

## Bounded Duo recovery: owner-selected automation

This procedure is enabled only when the adopting owner selects it. Record the
adopting owner's enablement, integration target and scope. Default total deadline:
20 minutes from the first request for a given MR head; at most one retry. These
are recovery limits, not evidence that an absent review passed.

The existing coordinator owns recovery at CI completion, a delivered review
outcome, or another existing merge checkpoint. No polling agent, daemon, new
webhook service or repeated waiting loop is added. A deadline is evaluated at
such a checkpoint; these instructions do not install a timer or guarantee a
wake-up exactly at minute 20. Keep the lane owned until resolved.

1. In the existing Result/task record retain project/MR, exact head, actual
   request timestamp, session ID/link when available, retry count and outcome.
   Bind the session to this review request/head; never use a stale head's result.
   A changed head needs reconciliation under normal review/evidence rules.
2. Inspect the actual session status through the supported provider interface,
   not just bot comments. GitLab's documented `duoWorkflowWorkflows` GraphQL query
   returns session status; a session can fail while posting its final comments.
   Capture minimal nonsecret status/error provenance. If session lookup fails or
   its binding is uncertain, record UNKNOWN, not FAILED or PASS. Read actual MR
   discussions/findings as well; finished flow alone does not establish a
   complete published review. Never invent a session or timestamp.
3. On confirmed provider failure, retry once using the normal supported review
   request, only if this head has no live/possibly live review and no explicit
   owner stop. Preserve the failure. Record/verify the retry request; uncertain
   delivery is not permission to resend. Do not reset the original deadline or
   retry allowance after compaction, a handback or another bot comment.
4. A running review is not failed. Do not duplicate or cancel it merely because
   it is slow. At the next owned checkpoint after the total deadline, missing,
   unknown, failed or unpublished completion is REVIEW UNAVAILABLE; completed
   actionable findings always receive normal disposition, not an outage waiver.
5. With this owner-selected procedure, the coordinator automatically records a
   standing outage exception and continues ordinary integration without another
   owner prompt ONLY when current required CI passes, the supervisor and a
   separate independent source reviewer have accepted the complete current
   change, every received blocking finding is resolved/disposed, and all other
   source/target, security, native/protection, budget and manual gates clear.
   Record the exact head, reviews, CI, status/time/retry evidence and
   `Duo unavailable; standing exception applied` in the existing Result/review.
   This is not Duo approval or PASS. Missing prerequisites keep the MR held;
   they do not trigger an approval-bypass or another permission request to
   repeat already granted routine authority.
6. Recheck actual findings/source/CI before merge. A late blocking finding holds
   unmerged work; if it arrives after integration, route an owned bounded repair
   under existing policy rather than silently ignoring it. Never fabricate an
   approval, change branch protection/permissions, or override an owner-specific
   instruction to await Duo. Closed/merged MRs get no recovery retry.

The exception applies only to the adopted non-promotion integration scope. It
waives no CI, source review, real defect, qualification, cleanup or release gate.
RC/main promotion, final tags/deployment and explicit owner holds remain separate;
Duo on an RC remains advisory under its existing policy. Reuse the current task
records and coordinator, not a new tracker. No model/session restart is required.

GitLab adapter sources: Flows API, "Check the status of a flow", and the
GitLab Support article "Code Review Flow fails repeatedly on a specific merge
request". Verify the supported interface in the adopting environment.
