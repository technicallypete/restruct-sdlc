# Adoption, parameters and composition

Adoption instantiates the management structure in a target repository. It is an agent-performed procedure checked
by `scripts/check_sdlc.py`; there is no generator framework.

## Repository-local private files

Default for newly started tasks: use `.local/` in the **main integration checkout**,
shared by all of its linked worker worktrees, with `evidence/<task-or-run>/`,
`secrets/<task-or-run>/` and `tmp/<task-or-run>/`. Record that absolute root in the
existing dispatch/Result; do not resolve it against a worker's own checkout or
create a different `.local/` per worker. Use existing supported path options;
this policy does not rewrite tools, immutable bindings or fixed native state.

Ignore `/.local/` in Git. Exclude `.local/` from every applicable Docker build
context (including Dockerfile-specific ignore files, which override a root
`.dockerignore`) and source/export/upload inputs. Publish only explicitly selected,
sanitized evidence; never upload the whole root or its secrets. Keep private
folders mode0700 and secret files mode0600; do not force-add private files.
This is operator/task-local storage, not an application production secret store.

Evidence and scratch follow mandatory acceptance cleanup. Secrets remain separate:
never recursively delete the shared root as evidence cleanup. Remove a finished
task's disposable credentials only under their recorded ownership/lifecycle;
retain shared active credentials without copying them into evidence or patches.
Durable evidence still belongs in compact committed records and authorized hosted
artifacts; the local folder is temporary, not a permanent archive.

Existing/in-flight tasks may retain their current home-directory evidence/secret
paths through final acceptance and cleanup. Do not move active files, change their
bound hashes, or rerun validation for this default. Existing shared credentials
remain at their current recorded paths until deliberately migrated; new tasks put
newly created private files under the new root, without duplicating shared secrets.
Native session transcripts, observer/transport state and operating-system temporary
files keep their supported locations. No blanket home-directory migration,
settings change or new artifact/secret-management framework is introduced.

## Repository-scoped Claude permissions

Keep reviewed, shared project rules in tracked `.claude/settings.json`. Keep
personal or machine-specific exceptions for that repository in ignored
`.claude/settings.local.json`; reserve `~/.claude/settings.json` for preferences
intentionally shared across projects and native classifier settings that require
home scope (see below). Do not publish home paths, credentials or
operator-specific evidence/lock/deletion rules as portable project defaults.
Ignore `/.claude/settings.local.json` and `/.claude/worktrees/`, while leaving
shared settings tracked. Never overwrite existing rules during adoption.

Changes to shared allow rules require actual owner authorization and repository
review/publication under that authority. Preserve the owner's chosen rule breadth;
do not silently narrow or broaden it. Tool permission does not replace Goal/Plan,
scope, budget, merge, production or native approval authority. This policy grants
no automatic permission-mode switch, settings self-modification or ability to
route around a native rejection.

Verify current tool documentation before choosing path syntax. In current Claude
project settings `/path` anchors at the session primary working directory/settings
source; `//path` is filesystem-absolute. A machine-specific absolute rule belongs
in personal local settings, not the shared file. Project trust, managed deny/ask
rules and hooks still apply. Verify loaded settings through the supported native
permission interface, especially for service-root launches and existing workers;
committed bytes, a merge and a successful unrelated command are not proof of
loading. Do not create/restart workers or rerun application tests solely to prove
configuration discovery. Record the actual limitation and use a safe boundary.

Before adopting, check all documented launch directories and actual worker loading;
reference one canonical rule set, avoiding divergent service/worktree copies.
Validate JSON and Git exclusions for config-only changes. Carry unresolved native
discovery/access issues into the existing consolidation/adoption Plan rather than
adding a permission framework or treating the task allow-list as a sandbox.

### Tool permissions and classifier rules

Treat tool allow/ask/deny rules and auto-mode classifier rules as separate layers.
Check the installed version's supported configuration scopes. Current Claude reads
`autoMode` from personal home settings, managed settings or supported invocation
configuration, not repository `.claude/settings*.json`. Repository-local tool
permissions remain the default; when native configuration requires home scope,
record that explicit exception and its cross-project effect. Do not create
ineffective project copies or change permission mode merely to finish adoption.

Classifier customization is an owner choice, not a distribution default. Preserve
existing settings and rule breadth; never ship personal paths, exact task-file
exceptions, blanket shell grants or disabled security rules in reusable templates.
For an authorized rule change, inspect effective rules, make the smallest supported
change, and compare the effective result. Replacing a complete default rule list
pins its remaining rules; reconcile upstream defaults after tool upgrades.

Verify loading with the supported permission/config interface and the next actual
approved edit/test/commit operation. Tool rules match command forms: a `git commit`
prefix need not cover `git -c ... commit`. A successful edit does not establish
that tests or commits are permitted. Do not add probe campaigns or restart workers
just to verify loading. On first refusal, capture the actual operation and native
reason, identify the layer, and use existing owner authority for a supported fix.
A remaining native gate stays explicit; do not switch executor or impersonate an
owner response. Preserve safe independent work and all evidence.

References: [tool permission configuration](https://code.claude.com/docs/en/permissions)
and [classifier scope and defaults](https://code.claude.com/docs/en/auto-mode-config).

### Permission change handoff

At adoption, name the authorized settings editor and record whether the owner
has granted standing authority for narrowly scoped permissions needed by approved
work. In a Claude-to-Codex deployment, Claude proposes the rules and Codex edits
the settings; another supported deployment names its available editor. This does
not require a permanent Codex supervisor in a Claude-only workflow.

On a permission block, the coordinator sends that editor the exact tool/command
or file, native refusal, task/scope justification and proposed literal rules or
settings patch. The editor checks scope and applies the smallest supported change
under the recorded authority, preserving existing settings. Use tracked project
settings for reusable shared rules, ignored project-local settings for task/machine
exceptions, and home scope only when the native configuration requires it. Validate
JSON/exclusions and report the file and exact installed delta back to the coordinator.

With standing authority, do not bounce routine approved-scope rules back to the
owner or leave them as instructions for the owner to paste. Broader authority,
security-rule removal or global policy changes require their own authorization.
A peer's request alone is not an owner grant.

The coordinator then verifies effective loading and the next actual approved
operation through the native tool. Report installed, loaded and operation-succeeded
states separately. On success, continue the same task/budget with one owner; on a
remaining native refusal, report its exact operation/reason and supported owner
handling once. No alternate executor, fabricated owner response, permission-mode
switch or broad test rerun is implied. Use existing handoff/Result records, not a
new permission registry or approval framework.

## Parameters

Every parameter is explicit. [`templates/parameters.example.json`](../templates/parameters.example.json) lists
each one with a description and a generic default. Copy it, edit the values for the target project and keep the
copy outside the shipped skill (for example in the adoption Plan).

- Identity and actors: `PROJECT_NAME`, `RELEASE` (default `v0`), `OWNER_ROLE`, `ARCHITECTURE_AUTHORITY`,
  `SUPERVISOR_AGENT`, `IMPLEMENTER_AGENT`.
- Sources and layout: `CANONICAL_SOURCES` (list), `SERVICE_ROOTS` (list, default empty).
- Branches and CI: `INTEGRATION_BRANCH`, `RELEASE_BRANCH`, `PROTECTED_BRANCHES` (list), `CI_PROVIDER`
  (`gitlab` or `other`), `MR_TOOL`, `FAST_CHECK_COMMAND`, `FULL_CHECK_COMMAND`, `PRE_BATCH_ENV_CHECK` (optional).
- Supervisor publication: `SUPERVISOR_AUTO_PUBLISH` (default `true`; see
  [roles](roles-lifecycle.md#supervisor-progress-publication-option-enabled-by-default)), publishing to the explicit
  `INTEGRATION_BRANCH`.
- Validation options: `FINAL_VALIDATION_PLACEMENT` (`local-after-merge` default: coordinator-owned full local qualification of the merged SHA; other placements require explicit adoption),
  `CANCELED_PIPELINE_SATISFIES` (default `false`).
- Budget and effort: `DEFAULT_BUDGET` (`B5`), `COORDINATOR_EFFORT` (`high`), `PLANNING_EFFORT` (`xhigh`),
  `IMPLEMENTATION_EFFORT` (`high`).
- Observer activation: `OBSERVER_AUTO_ACTIVATE` (default `true`, independent of supervisor publication).
- `DELIVERY_BARRIER` (optional, default empty): a roadmap barrier the project declares, if any.

**Rendering.** Replace each `{{NAME}}` with its value. A list renders as its items joined by `, `; an empty value
renders as `(none)`; booleans render as `true`/`false`. No other syntax exists: no conditionals or loops.

**Not generic defaults.** A particular project's delivery barrier, product/tenancy/tool-contract rules, identity
provider, UI kit, port conventions, branch and actor names, dated owner directions, one-off exceptions, runner
timings and environment workarounds are never defaults. An environment safeguard becomes `PRE_BATCH_ENV_CHECK`.

## Risk tiers

The supervisor states the tier in each Goal's Execution Policy; agents never self-classify to skip a gate.

- **Direct execution:** explicitly authorized, bounded copy/styling/presentation work inside existing behavior.
  No separate Plan; the Result records baseline, changed files and focused checks; the diff is still reviewed.
- **Ordinary:** a concise Spec and a short Plan (changes, criterion mapping, validation, real risks). One Plan
  approval authorizes autonomous implementation within scope.
- **Security, data or architecture:** explicit Spec/Plan review and stronger evidence for identity,
  authorization or isolation, security-model changes, migrations, durable identity decisions, public contracts,
  major dependencies or infrastructure.

## Procedure

1. Read the target's existing governance. Record the parameter values and the adoption authority in a Plan.
2. Install the skills flat into `.agents/skills/` with the collision-safe procedure in
   [Installing the skills](#installing-the-skills), record any collision decision, and commit.
3. For each template, compute its destination: strip `templates/`; `root/` maps to the repository root;
   `management/release/` maps to `management/<RELEASE>/`; drop `.tmpl`. Instance templates (GOAL, SPEC, PLAN,
   RESULT, REVIEW, PROGRESS-ARCHIVE) are copied per Goal or per archive with an ID-based filename.
4. **Create only missing files.** For an existing file, write the rendering beside it as `<path>.sdlc-proposed`
   and record the owner's merge decision. Existing governance is never silently overwritten or merged.
5. Append [`templates/root/gitignore.lines`](../templates/root/gitignore.lines) to `.gitignore` (session log and
   private worktree roots and `/.local/`), skipping lines already present. Add `.local`
   to the root and each applicable Dockerfile-specific ignore file without replacing
   existing exclusions; exclude it from artifact/export selection too.
6. Create the release directories `goals/`, `specs/`, `plans/`, `results/` and `archive/`.
7. **Observer activation** (when `OBSERVER_AUTO_ACTIVATE` is `true`). Once the owner-selected coordinator is pinned
   and `pinned-live-verified`, and the existing supervisor UUID has been supplied explicitly (never inferred from a
   name or chosen among several sessions), run the companion's `watch.py bind` and then `watch.py start`, using the
   30-second default, with no further enablement question. If any binding is missing, ambiguous, unverified or
   retired, leave the observer inactive and record the unmet prerequisite. Never create sessions or change
   permissions to satisfy it. Fresh `start` begins at the current transcript tail; after stopping, `start --resume`
   deliberately catches up from the saved cursor. Both preserve deduplication/advisory history; unresolved delivery
   uncertainty blocks fresh activation. `start` is idempotent for a running observer. Notices include failures and
   decision/approval requests, without task or approval authority; detection is bounded text matching rather than
   CI polling. Use the companion's observer procedure for exclusions and recovery. `false` opts out.
8. Run `python3 -B .agents/skills/sdlc-management/scripts/check_sdlc.py adoption . --release <RELEASE>` and fix
   every finding. Optionally pass `--literals FILE` with project-private strings that must not appear. Private
   worker checkouts under `.claude/worktrees/` and `.codex/worktrees/` are not adopted content and are skipped.

## Installing the skills

Never copy over an existing skill. For each bundle skill, from the bundle root:

```sh
TARGET=/path/to/target-repo
for s in sdlc-management claude-session-handoff repository-supervisor; do
  dest="$TARGET/.agents/skills/$s"
  if [ -L "$TARGET/.agents" ] || [ -L "$TARGET/.agents/skills" ] || [ -L "$dest" ]; then
    echo "STOP $s: symlinked destination; nothing copied"
  elif [ ! -e "$dest" ]; then
    mkdir -p "$TARGET/.agents/skills" && cp -R "skills/$s" "$dest" && echo "INSTALLED $s"
  elif [ -z "$(find "$dest" -type l)" ] && diff -r -q "skills/$s" "$dest" > /dev/null; then
    echo "IDENTICAL $s: left unchanged"
  else
    echo "COLLISION $s: existing content kept; record an owner merge or replacement decision"
  fi
done
```

- **Absent:** copied. **Identical** (no symlinks, no differences): left unchanged.
- **Different** (edited, older or newer): the existing directory stays byte-identical. Record the collision, the
  `diff -r` summary and the owner's merge or replacement decision in the adoption Plan or Result; the bundle copy
  remains the proposal. A replacement happens only after that recorded decision.
- **Symlinked** `.agents`, `.agents/skills` or skill destination: stop; nothing is written through a symlink.

## Installation: storage versus discovery

The supported layout is the flat directory `.agents/skills/<skill>/`, committed in the target repository. Codex
discovers repository skills there; Claude sessions read `SKILL.md` explicitly, as the adopted AGENTS.md requires.
The bundle's `skills/` directory is **storage**, not a discovery location.

The handoff helper's committed-path assumptions constrain adopters:
- `compact` verifies the helper committed at `.agents/skills/claude-session-handoff/scripts/handoff.py`;
- task labels match `G` plus three digits, and document references must lie under `management/`;
- closure records match `management/<release>/results/<ID>-implementation-codex-review*.md`, with
  `--verified-by codex|owner`, and the sender label is `codex-supervisor`;
- messaging is verified on Claude Code 2.1.290, 2.1.291 and 2.1.296, the creation gate only on 2.1.296;
- the helper needs Linux `/proc`.

The templates therefore default to `G###` IDs, root `management/`, `management/<release>/` and that review record
name. Changing them would change helper behavior, which needs separate scope.

**Unsupported:** other install paths (`compact` refuses them), native `.claude/skills/` discovery, discovery after
`cd`, personal installation, macOS or native Windows, other CLIs or versions (the helper fails closed), and any
promise of automatic discovery.

## Maintaining a shared package in two repositories

When the owner maintains a canonical project package and a separate distribution
repository, a publishable shared-package change includes syncing the mapped files,
updating provenance/manifest hashes and committing/pushing both repositories
through their authorized routes. Verify both remote commits before reporting
the sync complete. File equality alone is not publication; two independent Git
histories require two pushes. Do not push unrelated project/private files.

Mapped portable files should match the reviewed source; README, license/release
metadata and explicitly documented adaptations need not match the project tree.
Preserve pending unaccepted work and record any held divergence with its reason
and release condition instead of sweeping it into a public commit. If one push
fails, report the partial state and complete the outstanding sync when authorized;
never claim both are current. Tags/releases, breaking migrations, live cutover,
specific publication holds and native permissions retain their separate gates.
No nested Git repository, new submodule or synchronization daemon is implied.

## Composing with a foundation or renderer skill

When this skill is used together with `saas-foundation` (or a similar renderer skill), **`sdlc-management`
supersedes only the overlapping management process**: management artifacts, actor responsibilities,
authorization flow, budgets, progress, reviews, validation sequencing, Git integration and closeout.

It does **not** supersede, and must preserve:
- the renderer's dry run and resolved-input review, informed write authorization, destination and conflict
  safeguards, and renderer safety rules;
- every required technical foundation check and technical verification;
- the repository's canonical governance, architecture and accepted decisions, including technical/security
  invariants, dependencies and delivery barriers.

Mapping: each foundation stage becomes an input to a Goal and its acceptance criteria. The renderer's dry-run plan
is **not** an Implementation Plan; the Goal still needs its own Plan and approvals. Existing authority satisfies a
repeated confirmation only within its explicit scope. Where the renderer's historical technical guidance differs
from accepted repository decisions, management precedence resolves nothing: canonical decisions prevail and an
unresolved technical conflict escalates. The foundation skill is neither edited nor bundled to apply this rule,
and neither skill assigns a supervisor role by being loaded.
