# Documentation Realignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decompose the 158-rule catalog in `NEW_RULES.md` into per-domain MkDocs pages without losing or altering a single rule, document the shipped `0.1.0a1` release, reconcile it against the new catalog, and retire the nine-phase roadmap into an unordered backlog.

**Architecture:** A grep-generated fidelity baseline is frozen first, then bounded `sed` ranges are handed to one subagent per destination file so no agent ever reads the source catalog whole. MkDocs `validation:` under `--strict` becomes the structural gate, so every task ends with a green build. A final diff of the source slug set against the destination slug set proves nothing was lost.

**Tech Stack:** MkDocs 1.6.1 + Material, `uv` for all Python invocation, grep/sed/awk for all inventory generation, pre-commit with an enforced conventional-commit hook.

## Context

The project's direction changed. `NEW_RULES.md` (untracked, 690 lines, repo root) is the new canonical rule catalog and design document. The published site still describes the previous catalog, and `.agent-specs/phases/` still defines a nine-phase roadmap that predates the shift.

This branch (`docs/realign-specs`) realigns documentation and agent workflow. **No `src/` or `tests/` changes happen here.** It is not a phase and appears in no roadmap, because planning several phases ahead is the practice being retired — going forward only the next piece of work gets planned, and this branch is the first instance of that discipline rather than an exception to it.

## Global Constraints

Every task's requirements implicitly include this section.

- **Never read `NEW_RULES.md` end to end, at any tier — including the coordinator.** Access it only via `grep -n '^#'` for a heading index, bounded `sed -n 'START,ENDp'`, or a subagent given one range and nothing else.
- **Do not reference or invoke `scope_guard.py`**, in this plan or during execution.
- **Do not modify `src/` or `tests/`.** Task 10 verifies this with an empty diffstat.
- **Do not plan or perform an end-to-end rewrite of anything.**
- **No task may presuppose, depend on, or reserve scope for a later phase.**
- Legacy rules stay in an explicit `legacy/` subdirectory — present, viewable, marked superseded, **not deleted**.
- Agent-facing execution specs live under `.agent-specs/`, never under `docs/site/`.
- **Rule text moves verbatim.** Only page introductions and framing between sections are authored, and that is the only place the `humanizer` skill applies.
- **Generate every count and inventory from a command, never from a model's account of what it read.**
- Commit subjects must match `prefix(scope): summary` where prefix ∈ `feat|chore|ops|fix|release|docs`, summary starts lowercase, no trailing period (enforced by `scripts/check_commit_msg.py` as a `commit-msg` pre-commit hook).
- The operator owns git remotes. Commit locally; **do not push, branch, or open a PR** unless asked.
- If a task touches Python, run `scripts/format.sh` before `scripts/lint.sh`. No task here should.

---

## Established Facts

Verified by running the stated command on this branch on 2026-07-26. Do not re-derive; re-run the command if you doubt one.

### Slug pattern — the whole verification chain depends on this

```
\b(SRP|KISS|CQS|POLA|COUP|CONTRACT|STATE|LIFE|FAIL|CONC|IDIOM|NIT|DRY)[0-9]{3}\b
```

Domain prefix, three digits, **no dash**. Examples: `SRP001`, `STATE020`, `NIT024`. Source: §1 of `NEW_RULES.md` — *"ID is a stable domain-prefixed selector such as `STATE001`; severity never appears in the ID."*

- 158 unique matches in `NEW_RULES.md`, all inside §5, one markdown table row each.
  `grep -ohE '<PATTERN>' NEW_RULES.md | sort -u | wc -l` → `158`
  `grep -cE '^\| (SRP|…|DRY)[0-9]{3} \|' NEW_RULES.md` → `158`
- Currently **0** matches anywhere in `docs/` and **0** in `src/`. The destination set starts empty.
- **The explicit domain alternation is required.** A naive `[A-Z]{2,10}[0-9]{3}` yields 182 unique matches, pulling in Ruff codes (`ANN001`, `ERA001`) from §7 and `PY001`–`PY022` from §8. Do not simplify the pattern.

**Five identifier families exist in this repo. Do not confuse them:**

| Family | Form | Where | Count |
|---|---|---|---|
| New catalog rules | `SRP001` | `NEW_RULES.md` §5 | 158 |
| Source-catalog provenance slugs | `HS-PURPOSE-01` | `NEW_RULES.md` §6–§9, legacy catalog page | 209 |
| Prototype crosswalk IDs | `PY001` | `NEW_RULES.md` §8 | 22 |
| Shipped source codes | `HS001` | `src/humansays/` | 19 |
| Internal evidence IDs | `coup.data_clump` | `NEW_RULES.md` §6, §9 | 57 |

### Correction to the stated verification chain

`--exclude-dir=legacy` on the destination grep is **belt-and-braces, not load-bearing**. Legacy pages use the dashed `HS-PURPOSE-01` family, which the new pattern cannot match — confirmed: `grep -rhoE '<PATTERN>' docs/` returns 0 hits today *with the legacy catalog present*. Keep the flag anyway; it costs nothing and guards against a future legacy page quoting a new ID.

### MkDocs

- **Version 1.6.1** (`uv run mkdocs --version`). `validation.anchors` requires ≥ 1.6 — supported.
- **`uv run mkdocs build --strict -f docs/mkdocs.yml` currently exits 0.** The gate is green at the start, so any later failure is attributable to this migration. Getting it green is *not* a precondition task.
- `docs_dir: site` → the built docs root is **`docs/site/`**, not `docs/`.
- `site_dir: ../site` → output goes to repo-root `site/`, gitignored at `.gitignore:168`.
- `docs/evidence/` and `docs/README.md` sit **outside `docs_dir` and are never built** — no build gate covers them.
- Docs deps live in the `docs` dependency group (`mkdocs-material>=9.7.7`).
- **`omitted_files: warn` under `--strict` makes nav completeness a hard gate.** From Task 2 onward, any page created without a matching `nav:` entry fails the build. Every page-creating task below adds its own nav entries for this reason.

### `NEW_RULES.md` structure — line ranges (from `grep -n '^#'`)

| Section | Lines | Destination |
|---|---|---|
| Title + status block | 1–10 | folded into `rules/python/index.md` |
| §1 Rule model | 11–29 | `rules/python/index.md` |
| §2 Domains and default weights | 30–49 | `rules/python/index.md` |
| §3 Profiles and selection | 50–77 | `rules/python/index.md` |
| §4 Domain thresholds | 78–92 | `rules/python/index.md` |
| §5 preamble | 93–96 | `rules/python/index.md` |
| §5 SRP | 97–114 | `rules/python/srp.md` |
| §5 KISS | 115–130 | `rules/python/kiss.md` |
| §5 CQS | 131–140 | `rules/python/cqs.md` |
| §5 POLA | 141–156 | `rules/python/pola.md` |
| §5 COUP | 157–171 | `rules/python/coup.md` |
| §5 CONTRACT | 172–188 | `rules/python/contract.md` |
| §5 STATE | 189–215 | `rules/python/state.md` |
| §5 LIFE | 216–239 | `rules/python/life.md` |
| §5 FAIL | 240–261 | `rules/python/fail.md` |
| §5 CONC | 262–280 | `rules/python/conc.md` |
| §5 IDIOM | 281–303 | `rules/python/idiom.md` |
| §5 NIT | 304–334 | `rules/python/nit.md` |
| §5 DRY | 335–345 | `rules/python/dry.md` |
| §6 Internal evidence registry (57 facts) | 346–409 | `rules/python/evidence-registry.md` |
| §7 Externalizations/replacements/omissions (18) | 410–436 | `rules/python/externalized.md` |
| §8 Prototype `PY001`–`PY022` crosswalk | 437–463 | `rules/python/prototype-crosswalk.md` |
| §9 Source-accountability ledger (209 rows) | 464–679 | `.migration/source-accountability-ledger.md` (**not published**) |
| §10 Accounting summary | 680–690 | `rules/python/accounting.md` |

§5 table columns: `| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |`

Rules per domain: SRP 11, KISS 9, CQS 3, POLA 9, COUP 8, CONTRACT 10, STATE 20, LIFE 17, FAIL 15, CONC 12, IDIOM 16, NIT 24, DRY 4. **Sum = 158.**

### Known accounting discrepancy in the source document — not a migration risk

§10 claims 158 selectable rules and grep confirms 158 ID rows. But §10's sub-accounting does not reconcile at row level: 137 rows cite an `HS-` source, 18 cite "Later combined catalog", and 3 cite a prototype ID directly (`IDIOM016` ← PY021, `NIT022` ← PY015, `NIT023` ← PY016). 137 + 18 + 3 = 158. **Migrate the text as written; do not correct it.**

§9 is fully joinable: 209 rows, 209 unique source IDs, dispositions `on` 105, `evidence` 57, `hint` 21, `external` 11, `omitted` 5, `off` 4, `observe` 4, `replaced` 2. The 134 rows dispositioned on/hint/off/observe carry a `DOMAIN###` final ID; 57 carry an internal evidence ID; 18 (external + omitted + replaced) match §10's stated 18. 134 + 57 + 18 = 209.

### Current documentation site inventory

| Path | Lines | Fate |
|---|---|---|
| `docs/site/index.md` | 9 | links updated |
| `docs/site/rules/README.md` | 57 | → `docs/site/rules/legacy/README.md` |
| `docs/site/rules/python.md` | 337 | → `docs/site/rules/legacy/python.md` |
| `docs/site/style-guide/README.md` | 20 | unchanged |
| `docs/site/style-guide/python.md` | 636 | unchanged |
| `docs/site/style-guide/rust.md` | 935 | unchanged |
| `docs/site/roadmap/future-additions.md` | 39 | triaged in Task 9 |

**Only four markdown links exist across the entire site**, at `docs/site/index.md:6,7,8` (→ `style-guide/README.md`, `rules/README.md`, `roadmap/future-additions.md`) and `docs/site/rules/python.md:7` (→ `README.md`). There are no anchor links today, so `anchors: warn` starts from a clean slate.

### `docs/site/legacy` does not exist

Commit `f8497a1` ("split agent specs from the published docs site") already moved the agent specs to `.agent-specs/`. Zero occurrences of the word "legacy" anywhere under `docs/`. The stated constraint is largely already satisfied.

One residue remains: **`docs/README.md`** is agent-facing (`## If you are a coding agent`), describes a `docs/{process,phases,design,rules,criteria,evidence}/` layout that no longer exists, and its links `process/agent-protocol.md` and `phases/` are broken. It sits outside `docs_dir`, so MkDocs never sees it and the build gate cannot catch this. Task 3 moves it.

### The shipped release

`v0.1.0a1`, tagged, built into `dist/`. `src/humansays/` implements **19 rules**: `HS001`–`HS009`, `HS012`–`HS019`, `HS021`, `HS022` (`src/humansays/catalog.py:18-197`; names in `src/humansays/enums.py:35-54`). Gaps at `HS010`, `HS011`, `HS020`.

Key source coordinates for Task 7:

- `src/humansays/config/loading.py:111-141` — the CLI: positional `paths` (nargs `*`, `-` for stdin), plus `--version --config --format --symbol --limit --exclude --fail-on --min-score --max-arguments --max-nesting --class-nesting-bonus --max-branches --max-function-lines --max-code-lines --max-class-attributes --max-base-classes --max-file-lines`
- `src/humansays/config/models.py:14-101` — the `[tool.humansays]` surface
- `src/humansays/scoring.py:1-38` — penalty = weight × confidence; density = penalty × 100 / lines; score = `100 / (1 + density / SCORE_TOLERANCE)`
- `src/humansays/const.py:82,91` — grades A ≥ 90, B ≥ 75, C ≥ 60, D ≥ 40, F < 40; `SCORE_TOLERANCE = 7.5`
- `src/humansays/reporting/render.py:123-145` — JSON payload; `:148` — text via `rich` if installed, ANSI fallback otherwise
- `src/humansays/findings/models.py:40-60` — `RuleSpec` fields: `signal`, `severity`, `confidence`, `weight`, `review_question`

No `TODO`/`FIXME`/`XXX`/`NotImplementedError` anywhere in `src/humansays/`.

### The reconciliation join is mechanical, two hops

The shipped `HS0NN` codes correspond 1:1 **by rule name** to prototype `PY0NN`:

```
shipped HS0NN --(name match)--> PY0NN --(§8 crosswalk)--> HS-DOMAIN-NN --(§9 ledger)--> SRP001-style ID
```

Findings already established that Task 8's agent should **verify rather than rediscover**:

- The three gaps in the shipped codes (`HS010` comments, `HS011` docstrings, `HS020` future annotations) map to the three `PY` entries §8 marks **omitted**. The source already reflects those decisions.
- Three shipped rules are **demoted to unweighted reviewer hints**: `HS015` static-method (WARNING, w3.0) → `NIT022` hint; `HS016` lambda-expression (WARNING, w3.0) → `NIT023` hint; `HS021` lazy-import (ADVISORY, w1.0) → `IDIOM016` hint. This is the substantive behavioral change for a `0.1.0a1` user.
- `HS005` broad-exception splits: §8 maps `PY005` → `HS-FAIL-01/02/03`, and `HS-FAIL-02`/`HS-FAIL-03` become **internal evidence** (`fail.broad_exception_logged_only`, `fail.broad_exception_reraised`), not selectable rules.

### Phase roadmap dependencies

Nothing in `.pre-commit-config.yaml`, `.github/`, `Makefile`, or `scripts/*.sh` reads the phases tree — **deletion is safe for CI and hooks**. But four markdown links in the design specs point into it, and **no build gate covers `.agent-specs/`**, so the grep in Task 9 is the only check:

- `.agent-specs/design/02-evaluation-model.md:117` and `:228` → `../phases/05-measurement-study/PHASE.md`
- `.agent-specs/design/03-effect-architecture.md:60` → `../phases/07-effects/PHASE.md`
- `.agent-specs/design/04-execution-modes.md:47` → `../phases/08-dynamic/PHASE.md`

`docs/evidence/*.md` also mentions `docs/phases/…` — historical records of completed work. **Leave them alone.**

### Pre-commit will rewrite the extracted files — this bounds what "verbatim" can mean

`.pre-commit-config.yaml` runs `pre-commit-hooks` v6.0.0 on every commit, including on markdown: `trailing-whitespace`, `end-of-file-fixer`, `mixed-line-ending`, `check-yaml`, `check-toml`, `check-merge-conflict`, `check-added-large-files`. Also `ruff-check --fix` and `ruff-format` (Python only), `shellcheck` v0.11.0, `shfmt` v3.10.0-2, and the local `commit-msg-format` hook.

Two consequences the executor must plan around:

1. **`trailing-whitespace` is configured without `--markdown-linebreak-ext`, so it strips trailing spaces from markdown too.** A byte-for-byte diff of an extracted page against its `sed` range will therefore fail after the first commit even when the extraction was perfect. **This is why every fidelity check in this plan is slug-set and row-count based, not byte based.** Do not "upgrade" the verification to a byte diff — it will produce false failures.
2. **When a hook modifies a file, the commit aborts and leaves the file modified in the working tree.** Re-stage and re-run the same `git commit` command. Expect this on the first commit of Tasks 4, 5, and 6. It is not a failure; it is the hook doing its job.

If a rule's message template genuinely depends on trailing whitespace, the row-count checks will still pass while the text has silently changed. This was **not** investigated — see *Not Investigated*.

### Sample §5 row, so the table format is checkable without opening the file

`NEW_RULES.md:103`, verbatim:

```
| SRP001 | Role conflict | design | review | on | HS-PURPOSE-10 | Decides, performs I/O, and formats output in one body | `{symbol}` decides policy, performs `{effects}`, and formats output in one body. |
```

Eight columns, single space padding inside each pipe, message templates contain `{placeholder}` tokens inside backticks. `{` and `}` are literal — do not treat them as template syntax to be filled in.

---

## Decisions

| Decision | Chosen | Rejected, and why |
|---|---|---|
| Catalog page granularity | 13 pages, one per §5 domain | 6 themed pages and 11 folded pages both require a grouping judgment that could misplace a rule; the catalog's own headings are the safest boundary. Accepts thin `cqs.md` (3 rules) and `dry.md` (4). |
| Non-catalog sections | Publish §1–§8 and §10; §9 to `.migration/` | Publishing everything adds a 209-row provenance table no product reader will use. Withholding §8/§10 too would hide the honesty artifact that makes the rewrite auditable. |
| Retired phase directories | **Delete** them | Moving to `.agent-specs/retired/` or bannering in place both leave a nine-phase sequence in the specs tree that an agent may still read as live — the exact failure this branch corrects. The classification writeup plus git history is the record. **The operator explicitly authorized this deletion.** |
| `NEW_RULES.md` fate | Commit at root, **delete in Task 10** | Keeping it duplicates the site content permanently. Deleting it does make verification step 1 unrepeatable — mitigated by committing `.migration/slugs-source.txt` as the frozen baseline. |
| Where the backlog lives | `.agent-specs/backlog.md` | It is planning input for future agent sessions, not product documentation. Putting it on the site would give a wishlist the standing of a commitment. |
| Nav wiring | Each page-creating task adds its own nav entries | Deferring all nav to one task leaves the build red across three commits, which destroys the gate's value as a per-commit signal. |
| Page creation order | Domain pages → provenance pages → landing page | The landing page links to all 17 others; `unrecognized_links` requires its targets to exist first. |
| Inventory generation | grep/awk pipelines only | A model's account of what it read is not evidence. |

---

## File Structure

```
docs/site/
├── index.md                              links updated (Task 3, 6)
├── rules/
│   ├── python/
│   │   ├── index.md                      §1–§4 + §5 preamble + link list   (Task 6)
│   │   ├── srp.md kiss.md cqs.md pola.md coup.md contract.md
│   │   ├── state.md life.md fail.md conc.md idiom.md nit.md dry.md          (Task 4)
│   │   ├── evidence-registry.md          §6                                 (Task 5)
│   │   ├── externalized.md               §7                                 (Task 5)
│   │   ├── prototype-crosswalk.md        §8                                 (Task 5)
│   │   └── accounting.md                 §10                                (Task 5)
│   └── legacy/
│       ├── README.md                     was rules/README.md + banner       (Task 3)
│       └── python.md                     was rules/python.md + banner       (Task 3)
├── reference/                            what 0.1.0a1 actually ships
│   ├── index.md cli.md configuration.md output.md shipped-rules.md          (Task 7)
│   └── reconciliation.md                 shipped → new catalog              (Task 8)
├── style-guide/                          unchanged
└── roadmap/future-additions.md           triaged                            (Task 9)

.migration/                               committed, outside docs/ by design
├── README.md  inventory.tsv  slugs-source.txt  slugs-dest.txt               (Task 1)
└── source-accountability-ledger.md       §9, unpublished                    (Task 5)

.agent-specs/
├── README.md                             moved from docs/README.md          (Task 3)
├── roadmap-retirement.md                 per-phase classification           (Task 9)
├── backlog.md                            unordered survivors                (Task 9)
├── plans/2026-07-26-docs-realignment.md  this plan                          (Task 1)
├── design/  process/
└── phases/                               DELETED                            (Task 9)
```

---

## Subagent Protocol

**One subagent per destination file.** Each receives its line range and its destination path and **sees no other part of the catalog**. Extraction agents must never read `NEW_RULES.md` outside their range and must never read it whole.

Reusable extraction prompt — substitute the bracketed values:

> You are extracting one section of a rule catalog into its own documentation page.
>
> 1. Run exactly: `sed -n '[START],[END]p' NEW_RULES.md` from `/home/rhawk/dev/humansays`. Do not read `NEW_RULES.md` any other way. Do not read outside this range.
> 2. Write the result to `[DEST]`.
> 3. **Every table row and every rule ID moves byte-for-byte verbatim.** Do not rewrite, reword, reclassify, renumber, reorder, reformat, or "improve" any rule text, message template, or table cell. If you find yourself paraphrasing a rule, you have exceeded your brief — stop and report it.
> 4. You may author exactly two kinds of new text: a page title (`# [TITLE]`) and one short introductory paragraph before the table. Invoke the `humanizer` skill for that prose and nothing else. Demote the extracted `###` heading to fit the page, or drop it if it duplicates the page title — but change no other heading text.
> 5. Verify before returning: `grep -cE '^\| [A-Z]+[0-9]{3} \|' [DEST]` must print `[N]`, and `grep -c '^|' [DEST]` must equal `sed -n '[START],[END]p' NEW_RULES.md | grep -c '^|'`.
>
> Return only: the destination path, the two counts you measured, and anything you could not copy verbatim.

**Model tiering.** Extraction and file assembly are mechanical — route to `haiku` via the `implementer` agent type. The landing page merges four sections and needs real connective prose — `sonnet`. The three judgment tasks (source documentation, reconciliation, roadmap classification) carry the risk of silent loss — route to `general-purpose`, the latter two on `opus`. Dispatch extraction agents in waves of at most five concurrent.

---

## Tasks

### Task 1: Freeze the fidelity baseline

**Files:**
- Create: `.migration/slugs-source.txt`, `.migration/inventory.tsv`, `.migration/README.md`
- Create: `.agent-specs/plans/2026-07-26-docs-realignment.md` (copy of this plan)
- Add to git: `NEW_RULES.md` (currently untracked)

**Produces:** `.migration/slugs-source.txt`, the 158-line frozen baseline every later verification diffs against, and `.migration/inventory.tsv`, whose column 4 is the authoritative slug→destination mapping.

- [ ] **Step 1: Create the directory and generate the source slug set**

```bash
cd /home/rhawk/dev/humansays
mkdir -p .migration
PATTERN='\b(SRP|KISS|CQS|POLA|COUP|CONTRACT|STATE|LIFE|FAIL|CONC|IDIOM|NIT|DRY)[0-9]{3}\b'
grep -rhoE "$PATTERN" NEW_RULES.md | sort -u > .migration/slugs-source.txt
```

- [ ] **Step 2: Generate the inventory from grep output**

Each rule occupies exactly one table row, so `start_line` and `end_line` are equal by construction.

```bash
grep -nE '^\| (SRP|KISS|CQS|POLA|COUP|CONTRACT|STATE|LIFE|FAIL|CONC|IDIOM|NIT|DRY)[0-9]{3} \|' NEW_RULES.md \
  | sed -E 's/^([0-9]+):\| ([A-Z]+[0-9]{3}) \|.*/\2\t\1\t\1/' \
  | awk -F'\t' '{p=$1; sub(/[0-9]+$/,"",p); print $1"\t"$2"\t"$3"\tdocs/site/rules/python/"tolower(p)".md"}' \
  > .migration/inventory.tsv
```

- [ ] **Step 3: Verify the baseline**

Run:

```bash
wc -l < .migration/slugs-source.txt                   # expect: 158
wc -l < .migration/inventory.tsv                      # expect: 158
cut -f1 .migration/inventory.tsv | sort | uniq -d     # expect: no output
cut -f4 .migration/inventory.tsv | sort -u | wc -l    # expect: 13
head -1 .migration/inventory.tsv                      # expect: SRP001<TAB>103<TAB>103<TAB>docs/site/rules/python/srp.md
```

All five must match. If `wc -l` is anything other than 158, **stop** — the slug pattern or the source document has changed and every downstream count in this plan is invalid.

- [ ] **Step 4: Write `.migration/README.md`**

Explain: this directory holds migration provenance; it lives outside `docs/` deliberately because MkDocs `omitted_files` validation flags stray pages there; `inventory.tsv` is headerless with columns `slug`, `start_line`, `end_line`, `destination`; line numbers refer to `NEW_RULES.md` at repo root.

- [ ] **Step 5: Copy this plan into the specs tree**

```bash
cp /home/rhawk/.claude/plans/instructions-branch-context-this-branch-fuzzy-riddle.md \
   .agent-specs/plans/2026-07-26-docs-realignment.md
```

- [ ] **Step 6: Commit**

```bash
git add NEW_RULES.md .migration/ .agent-specs/plans/2026-07-26-docs-realignment.md
git commit -m "docs(migration): freeze the rule-catalog fidelity baseline"
```

---

### Task 2: Add MkDocs structural validation

**Files:**
- Modify: `docs/mkdocs.yml` (insert after the `plugins:` block)

**Produces:** the `--strict` gate that every subsequent task's verification relies on. From here on, a page without a `nav:` entry fails the build.

- [ ] **Step 1: Add the validation block**

```yaml
validation:
  omitted_files: warn
  unrecognized_links: warn
  absolute_links: warn
  anchors: warn
```

MkDocs 1.6.1 supports all four. Under `--strict` these warnings become build errors. `anchors: warn` matters most: splitting one file into many breaks every cross-reference whose target moved pages, and without it those fail silently while the site still builds.

- [ ] **Step 2: Verify the build is still green**

Run: `uv run mkdocs build --strict -f docs/mkdocs.yml; echo "exit=$?"`
Expected: `exit=0`, final log line `INFO - Documentation built in N.NN seconds`, **zero lines containing `WARNING`**.

If this fails, the four existing links or the current nav are already non-conforming — fix those before proceeding. The build was green before this block was added, so any failure here is attributable to the new validation, not to the migration.

- [ ] **Step 3: Commit**

```bash
git add docs/mkdocs.yml
git commit -m "docs(mkdocs): enforce link and anchor validation under strict"
```

---

### Task 3: Relocate superseded and agent-facing pages

**Files:**
- Move: `docs/site/rules/python.md` → `docs/site/rules/legacy/python.md`
- Move: `docs/site/rules/README.md` → `docs/site/rules/legacy/README.md`
- Move: `docs/README.md` → `.agent-specs/README.md`
- Modify: `docs/site/index.md:7`, `docs/mkdocs.yml` (`nav:`)

**Consumes:** the `--strict` gate from Task 2.

- [ ] **Step 1: Move the legacy catalog pages**

```bash
cd /home/rhawk/dev/humansays
mkdir -p docs/site/rules/legacy
git mv docs/site/rules/python.md docs/site/rules/legacy/python.md
git mv docs/site/rules/README.md docs/site/rules/legacy/README.md
```

The intra-page link at the old `python.md:7` (`README.md`) still resolves inside `legacy/`, so no link edit is needed.

- [ ] **Step 2: Add a superseded notice to both pages**

Prepend to each, immediately after the H1:

```markdown
!!! warning "Superseded"
    This catalog describes the previous rule model and is kept for reference
    only. The current catalog is at [Python rules](../python/index.md).
```

Do not otherwise edit these pages. They are a historical record.

- [ ] **Step 3: Move and correct the agent-facing readme**

```bash
git mv docs/README.md .agent-specs/README.md
```

Then correct it. Its layout block, reading order, and status table all describe a `docs/{process,phases,design,rules,criteria,evidence}/` tree that no longer exists — those moved to `.agent-specs/` in commit `f8497a1`. Rewrite them against the real `.agent-specs/` tree. **Remove the `phases/` reference entirely** — Task 9 deletes that directory. Keep the `## If you are a coding agent` framing, reworded against what `.agent-specs/` actually contains. Apply `humanizer` to the prose.

- [ ] **Step 4: Repoint the site index and update nav**

`docs/site/index.md:7` currently points at `rules/README.md`, which no longer exists. Point it at `rules/legacy/README.md` for now; Task 6 repoints it at the new catalog landing page.

In `docs/mkdocs.yml`, replace the `Rules:` nav section with:

```yaml
  - Rules:
      - Legacy catalog:
          - rules/legacy/README.md
          - Python: rules/legacy/python.md
```

- [ ] **Step 5: Verify**

Run:

```bash
uv run mkdocs build --strict -f docs/mkdocs.yml; echo "exit=$?"   # expect: exit=0, no WARNING lines
ls docs/site/rules/                                                # expect: legacy  (and nothing else)
grep -rn 'phases/' .agent-specs/README.md                          # expect: no output
test ! -f docs/README.md && echo moved                             # expect: moved
```

- [ ] **Step 6: Commit**

```bash
git add -A docs/ .agent-specs/README.md
git commit -m "docs(legacy): move the superseded catalog and the agent readme"
```

---

### Task 4: Extract the thirteen domain pages

**Files:**
- Create: `docs/site/rules/python/{srp,kiss,cqs,pola,coup,contract,state,life,fail,conc,idiom,nit,dry}.md`
- Modify: `docs/mkdocs.yml` (`nav:`)

**Consumes:** the line ranges below and `.migration/inventory.tsv` column 4 from Task 1.
**Produces:** 158 rule rows across 13 pages — the destination set Task 6's fidelity gate diffs against the frozen baseline.

- [ ] **Step 1: Dispatch 13 extraction subagents**

Use the reusable extraction prompt from **Subagent Protocol** above. `implementer` agent type on `haiku`, in waves of at most five concurrent.

| Agent | `[START],[END]` | `[DEST]` | `[N]` |
|---|---|---|---|
| SRP | 97,114 | `docs/site/rules/python/srp.md` | 11 |
| KISS | 115,130 | `docs/site/rules/python/kiss.md` | 9 |
| CQS | 131,140 | `docs/site/rules/python/cqs.md` | 3 |
| POLA | 141,156 | `docs/site/rules/python/pola.md` | 9 |
| COUP | 157,171 | `docs/site/rules/python/coup.md` | 8 |
| CONTRACT | 172,188 | `docs/site/rules/python/contract.md` | 10 |
| STATE | 189,215 | `docs/site/rules/python/state.md` | 20 |
| LIFE | 216,239 | `docs/site/rules/python/life.md` | 17 |
| FAIL | 240,261 | `docs/site/rules/python/fail.md` | 15 |
| CONC | 262,280 | `docs/site/rules/python/conc.md` | 12 |
| IDIOM | 281,303 | `docs/site/rules/python/idiom.md` | 16 |
| NIT | 304,334 | `docs/site/rules/python/nit.md` | 24 |
| DRY | 335,345 | `docs/site/rules/python/dry.md` | 4 |

- [ ] **Step 2: Add the nav entries**

Replace the `Rules:` section in `docs/mkdocs.yml` with:

```yaml
  - Rules:
      - Python:
          - SRP: rules/python/srp.md
          - KISS: rules/python/kiss.md
          - CQS: rules/python/cqs.md
          - POLA: rules/python/pola.md
          - COUP: rules/python/coup.md
          - CONTRACT: rules/python/contract.md
          - STATE: rules/python/state.md
          - LIFE: rules/python/life.md
          - FAIL: rules/python/fail.md
          - CONC: rules/python/conc.md
          - IDIOM: rules/python/idiom.md
          - NIT: rules/python/nit.md
          - DRY: rules/python/dry.md
      - Legacy catalog:
          - rules/legacy/README.md
          - Python: rules/legacy/python.md
```

- [ ] **Step 3: Verify — measure, do not trust the agents' self-reports**

Run:

```bash
cd /home/rhawk/dev/humansays
for f in docs/site/rules/python/*.md; do
  printf '%s\t%s\n' "$(grep -cE '^\| [A-Z]+[0-9]{3} \|' "$f")" "$f"
done
grep -hcE '^\| [A-Z]+[0-9]{3} \|' docs/site/rules/python/*.md | paste -sd+ | bc
uv run mkdocs build --strict -f docs/mkdocs.yml; echo "exit=$?"
```

Expected: per-file counts match the `[N]` column exactly; the total prints `158`; `exit=0` with no `WARNING` lines.

- [ ] **Step 4: Commit**

```bash
git add docs/site/rules/python/ docs/mkdocs.yml
git commit -m "docs(rules): split the catalog into thirteen domain pages"
```

---

### Task 5: Extract the reference and provenance sections

**Files:**
- Create: `docs/site/rules/python/{evidence-registry,externalized,prototype-crosswalk,accounting}.md`
- Create: `.migration/source-accountability-ledger.md` (committed, **not** in nav)
- Modify: `docs/mkdocs.yml` (`nav:`)

- [ ] **Step 1: Dispatch four extraction subagents plus one plain copy**

Same reusable prompt, `implementer` on `haiku`. These sections contain no `DOMAIN###` IDs, so drop the prompt's `[N]` check and keep only the row-count equality check.

| `[START],[END]` | `[DEST]` | Content |
|---|---|---|
| 346,409 | `docs/site/rules/python/evidence-registry.md` | 57 internal evidence facts |
| 410,436 | `docs/site/rules/python/externalized.md` | 18 externalized/replaced/omitted decisions |
| 437,463 | `docs/site/rules/python/prototype-crosswalk.md` | 22 `PY0NN` rows |
| 680,690 | `docs/site/rules/python/accounting.md` | §10 accounting summary |

§9 needs no authored prose — copy it directly rather than dispatching an agent:

```bash
cd /home/rhawk/dev/humansays
{ printf '# Source-accountability ledger\n\n'
  printf 'Extracted verbatim from NEW_RULES.md lines 464-679. Unpublished: this\n'
  printf 'is migration provenance, not product documentation.\n\n'
  sed -n '464,679p' NEW_RULES.md
} > .migration/source-accountability-ledger.md
```

- [ ] **Step 2: Add nav entries**

Append under the `Python:` sub-section in `docs/mkdocs.yml`, after `DRY:`:

```yaml
          - Evidence registry: rules/python/evidence-registry.md
          - Externalized and omitted: rules/python/externalized.md
          - Prototype crosswalk: rules/python/prototype-crosswalk.md
          - Accounting: rules/python/accounting.md
```

`.migration/source-accountability-ledger.md` gets **no** nav entry — it is outside `docs_dir`, so `omitted_files` does not apply to it.

- [ ] **Step 3: Verify by diffing source row counts against destination row counts**

This check is format-agnostic, so it holds regardless of how the tables are laid out:

```bash
cd /home/rhawk/dev/humansays
check() {  # $1=start $2=end $3=dest
  s=$(sed -n "$1,$2p" NEW_RULES.md | grep -c '^|')
  d=$(grep -c '^|' "$3")
  [ "$s" = "$d" ] && echo "OK   $3 ($s rows)" || echo "FAIL $3 src=$s dest=$d"
}
check 346 409 docs/site/rules/python/evidence-registry.md
check 410 436 docs/site/rules/python/externalized.md
check 437 463 docs/site/rules/python/prototype-crosswalk.md
check 680 690 docs/site/rules/python/accounting.md
check 464 679 .migration/source-accountability-ledger.md
uv run mkdocs build --strict -f docs/mkdocs.yml; echo "exit=$?"
```

Expected: five `OK` lines, no `FAIL`; `exit=0` with no `WARNING` lines. Rough expected row counts are 59 (57 facts + header + separator), 20, 24, and 211 (209 + header + separator); `accounting.md` may be 0 if §10 is prose rather than a table, which is fine as long as source and destination agree.

- [ ] **Step 4: Commit**

```bash
git add docs/site/rules/python/ .migration/ docs/mkdocs.yml
git commit -m "docs(rules): extract the evidence registry and provenance sections"
```

---

### Task 6: Build the catalog landing page and run the fidelity gate

**Files:**
- Create: `docs/site/rules/python/index.md`
- Modify: `docs/site/index.md:7`, `docs/mkdocs.yml` (`nav:`)
- Create: `.migration/slugs-dest.txt`

**Consumes:** all 17 pages from Tasks 4 and 5 — they must exist first, because `unrecognized_links` rejects links to files that are not there.

- [ ] **Step 1: Dispatch the landing-page subagent**

`implementer` on `sonnet` — this one merges four sections and needs real connective prose. Range `1,96`: title block, §1 rule model, §2 domain weights, §3 profiles, §4 thresholds, §5 preamble.

Same verbatim rule for the four tables and the TOML block. Beyond the extraction prompt, this agent additionally:

- authors a page introduction and one line of framing between each of the four sections;
- appends a link list to all 17 sibling pages as relative `.md` links (13 domain pages + `evidence-registry.md` + `externalized.md` + `prototype-crosswalk.md` + `accounting.md`);
- applies `humanizer` to the authored prose **only**.

- [ ] **Step 2: Repoint the site index and add the nav entry**

`docs/site/index.md:7` → `rules/python/index.md`.

In `docs/mkdocs.yml`, add as the first entry under `Python:`:

```yaml
          - Overview: rules/python/index.md
```

- [ ] **Step 3: Run the full five-step fidelity chain**

```bash
cd /home/rhawk/dev/humansays
PATTERN='\b(SRP|KISS|CQS|POLA|COUP|CONTRACT|STATE|LIFE|FAIL|CONC|IDIOM|NIT|DRY)[0-9]{3}\b'

grep -rhoE "$PATTERN" docs/ --exclude-dir=legacy | sort -u > .migration/slugs-dest.txt
wc -l < .migration/slugs-dest.txt
diff .migration/slugs-source.txt .migration/slugs-dest.txt; echo "diff=$?"
cut -f1 .migration/inventory.tsv | sort | uniq -d
uv run mkdocs build --strict -f docs/mkdocs.yml; echo "build=$?"
grep -oE '\]\([a-z-]+\.md\)' docs/site/rules/python/index.md | sort -u | wc -l
```

Expected, in order: `158`; **no diff output** followed by `diff=0`; no `uniq -d` output; `build=0` with no `WARNING` lines; `17` distinct link targets.

`diff=0` alone proves every rule landed **somewhere**. The `uniq -d` check is what proves each landed **once** — do not skip it.

- [ ] **Step 4: Commit**

```bash
git add docs/site/ docs/mkdocs.yml .migration/slugs-dest.txt
git commit -m "docs(rules): add the catalog landing page and verify fidelity"
```

---

### Task 7: Document what `0.1.0a1` ships

**Files:**
- Create: `docs/site/reference/{index,cli,configuration,output,shipped-rules}.md`
- Modify: `docs/mkdocs.yml` (`nav:`)
- Read only: `src/humansays/**` — **this task must not modify `src/` or `tests/`**

- [ ] **Step 1: Dispatch the documentation subagent**

One `general-purpose` agent on `sonnet`. Hand it the source coordinates from **Established Facts → The shipped release** so it verifies rather than rediscovers. Pages:

- `index.md` — what the tool does today, how to install it, one worked example
- `cli.md` — the `humansays` command: positional `paths` and every flag in `src/humansays/config/loading.py:111-141`
- `configuration.md` — the `[tool.humansays]` surface from `src/humansays/config/models.py:14-101`, with defaults
- `output.md` — text and JSON formats (`src/humansays/reporting/render.py`), the scoring model (`src/humansays/scoring.py:1-38`), and the A–F grade bands (`src/humansays/const.py:82,91`)
- `shipped-rules.md` — a table of all 19 codes with name, severity, confidence, weight, and review question, from `src/humansays/catalog.py:18-197`

Binding instructions for the agent: documentation describes behavior read from source. **It must not claim behavior it did not read**, and must not state a performance characteristic without a measurement. Apply `humanizer` to the prose. This is a `0.1.0a1` alpha — say so.

- [ ] **Step 2: Add nav entries**

```yaml
  - Reference:
      - reference/index.md
      - CLI: reference/cli.md
      - Configuration: reference/configuration.md
      - Output and scoring: reference/output.md
      - Shipped rules: reference/shipped-rules.md
```

- [ ] **Step 3: Verify**

```bash
cd /home/rhawk/dev/humansays
for c in $(grep -rhoE '\bHS[0-9]{3}\b' src/ | sort -u); do
  grep -q "$c" docs/site/reference/shipped-rules.md || echo "MISSING $c"
done
git status --porcelain src/ tests/
uv run mkdocs build --strict -f docs/mkdocs.yml; echo "exit=$?"
```

Expected: no `MISSING` lines — all 19 shipped codes documented; `git status --porcelain` on `src/` and `tests/` prints **nothing** (`tests/` is currently untracked and must stay untouched); `exit=0` with no `WARNING` lines.

- [ ] **Step 4: Commit**

```bash
git add docs/site/reference/ docs/mkdocs.yml
git commit -m "docs(reference): document the shipped 0.1.0a1 surface"
```

---

### Task 8: Reconcile shipped rules against the new catalog

**Files:**
- Create: `docs/site/reference/reconciliation.md`
- Modify: `docs/mkdocs.yml` (`nav:`)

**Judgment task — do not route to the extraction tier.** One `general-purpose` agent on `opus`.

- [ ] **Step 1: Dispatch the reconciliation subagent**

The agent reads `src/humansays/catalog.py` and **only** §8 (`sed -n '437,463p'`) and §9 (`sed -n '464,679p'`) of `NEW_RULES.md` — never the whole file, never §5. §5's content is already on the 13 domain pages if it needs to check a destination.

Hand it the two-hop join chain and the three pre-established findings from **Established Facts → The reconciliation join**, instructing it to **verify each rather than assume**.

Output structure:

1. A table, one row per shipped `HS0NN` code: prototype `PY0NN`, `HS-DOMAIN-NN` source slug, new-catalog ID or internal-evidence ID, new disposition, and a plain statement of what changes for a user.
2. A section on rules dropped in the rewrite: for each, whether it is worth keeping, and if so which of the 13 domains it belongs to.
3. An explicit callout wherever the ledger's disposition contradicts shipped behavior — the three demotions to unweighted hints being the clearest case.

Binding instruction: if the agent cannot establish a mapping from the ledger, it **records the unresolved question** rather than inventing a plausible one.

- [ ] **Step 2: Add the nav entry**

```yaml
      - Reconciliation: reference/reconciliation.md
```

- [ ] **Step 3: Verify**

```bash
cd /home/rhawk/dev/humansays
for c in $(grep -rhoE '\bHS[0-9]{3}\b' src/ | sort -u); do
  grep -q "$c" docs/site/reference/reconciliation.md || echo "MISSING $c"
done
grep -cE 'NIT022|NIT023|IDIOM016' docs/site/reference/reconciliation.md
git status --porcelain src/ tests/
uv run mkdocs build --strict -f docs/mkdocs.yml; echo "exit=$?"
```

Expected: no `MISSING` lines — all 19 shipped codes accounted for; the demotion grep prints **3 or more**; `git status --porcelain` prints nothing; `exit=0` with no `WARNING` lines.

- [ ] **Step 4: Commit**

```bash
git add docs/site/reference/reconciliation.md docs/mkdocs.yml
git commit -m "docs(reference): reconcile shipped rules against the new catalog"
```

---

### Task 9: Retire the phase roadmap

**Files:**
- Create: `.agent-specs/roadmap-retirement.md`, `.agent-specs/backlog.md`
- Delete: `.agent-specs/phases/` (nine phase directories + `README.md`), `.agent-specs/plans/2026-07-26-phase-2-fact-model.md`
- Modify: `.agent-specs/design/02-evaluation-model.md:117,228`, `.agent-specs/design/03-effect-architecture.md:60`, `.agent-specs/design/04-execution-modes.md:47`
- Modify or delete: `docs/site/roadmap/future-additions.md`, `docs/mkdocs.yml` (`nav:`)

**Judgment task.** One `general-purpose` agent on `opus`.

- [ ] **Step 1: Write the classification record**

The agent reads all nine `.agent-specs/phases/*/PHASE.md` plus `.agent-specs/phases/README.md` and writes `.agent-specs/roadmap-retirement.md`: one entry per phase (`01-review` through `09-performance`), classifying each as **misaligned with the current direction** or **still worth doing**, with the reasoning. Each entry cites the phase's own stated goal against the new catalog. This document is the record that replaces the deleted files, so it must stand alone once they are gone.

- [ ] **Step 2: Write the unordered backlog**

`.agent-specs/backlog.md` holds the survivors as an **unordered** list. No numbers, no dates, no sequencing, no phase grouping, no "first/then/next", no dependency ordering. **Sort alphabetically**, so the absence of sequence is structural rather than merely asserted.

Open the file with one line noting that a future planning session draws from it and that only the next piece of work gets planned at a time.

Also add one backlog entry that is not derived from a phase: **the new catalog's rules cite `HS-` source slugs rather than criteria-document sections, which the project's rule 9 requires.** See **Not Investigated** below.

**An ordered list of survivors is the specific failure this branch exists to correct.** If the agent produces one, reject and re-dispatch.

- [ ] **Step 3: Triage the future-additions wishlist**

`docs/site/roadmap/future-additions.md` holds 39 unnumbered bullets, largely absorbed into the new catalog (spot-checked examples: "A class with more than 2 generics", "A class with more than 6 private methods", "A try except block with more than 6 different exception blocks", "The use of `object` over `typing.Any`").

Bullets the 158-rule catalog covers are removed. Bullets it does not cover move to `.agent-specs/backlog.md`. If the page empties, delete it and its nav entry, and remove the link at `docs/site/index.md:8`; otherwise leave the remainder with a pointer to `../rules/python/index.md`.

- [ ] **Step 4: Delete the phase tree and repair the dangling links**

```bash
cd /home/rhawk/dev/humansays
git rm -r .agent-specs/phases/
git rm .agent-specs/plans/2026-07-26-phase-2-fact-model.md
```

The second file is an implementation plan for a phase being retired. Nothing in `.pre-commit-config.yaml`, `.github/`, `Makefile`, or `scripts/*.sh` reads this tree — verified — so deletion is safe for CI and hooks.

Then repoint the four dangling links listed in **Established Facts → Phase roadmap dependencies** at `.agent-specs/roadmap-retirement.md`. **No build gate covers `.agent-specs/`**, so the grep in Step 5 is the only thing that catches a missed one.

- [ ] **Step 5: Verify**

```bash
cd /home/rhawk/dev/humansays
test ! -d .agent-specs/phases && echo "phases removed"
grep -rn 'phases/' .agent-specs/ ; echo "dangling_exit=$?"
grep -nE '^\s*([0-9]+[.)]|Phase [0-9]|Step [0-9]|First,|Then,|Next,)' .agent-specs/backlog.md
grep '^- ' .agent-specs/backlog.md | sort -c && echo "unordered (alphabetical)"
uv run mkdocs build --strict -f docs/mkdocs.yml; echo "exit=$?"
```

Expected: `phases removed`; **no grep output** followed by `dangling_exit=1`; **no output** from the sequencing-word grep; `unordered (alphabetical)`; `exit=0` with no `WARNING` lines.

- [ ] **Step 6: Commit**

```bash
git add -A .agent-specs/ docs/
git commit -m "docs(roadmap): retire the phase sequence for an unordered backlog"
```

---

### Task 10: Final gate and source removal

**Files:**
- Delete: `NEW_RULES.md`
- Modify: `.migration/README.md`, `.migration/slugs-dest.txt`

`.migration/slugs-source.txt` becomes the permanent frozen baseline once `NEW_RULES.md` is gone. Confirm it is still correct **before** deleting, then delete, then re-run the chain against the frozen file.

- [ ] **Step 1: Confirm the frozen baseline still matches the source document**

```bash
cd /home/rhawk/dev/humansays
PATTERN='\b(SRP|KISS|CQS|POLA|COUP|CONTRACT|STATE|LIFE|FAIL|CONC|IDIOM|NIT|DRY)[0-9]{3}\b'
diff <(grep -rhoE "$PATTERN" NEW_RULES.md | sort -u) .migration/slugs-source.txt; echo "baseline=$?"
```

Expected: no output, `baseline=0`. **If this fails, stop** — do not delete the source document.

- [ ] **Step 2: Remove the source document**

```bash
git rm NEW_RULES.md
```

- [ ] **Step 3: Re-run the full chain against the frozen baseline**

```bash
cd /home/rhawk/dev/humansays
PATTERN='\b(SRP|KISS|CQS|POLA|COUP|CONTRACT|STATE|LIFE|FAIL|CONC|IDIOM|NIT|DRY)[0-9]{3}\b'
grep -rhoE "$PATTERN" docs/ --exclude-dir=legacy | sort -u > .migration/slugs-dest.txt
diff .migration/slugs-source.txt .migration/slugs-dest.txt; echo "fidelity=$?"
cut -f1 .migration/inventory.tsv | sort | uniq -d
uv run mkdocs build --strict -f docs/mkdocs.yml; echo "build=$?"
scripts/lint.sh; echo "lint=$?"
git diff --stat "$(git merge-base HEAD main)"..HEAD -- src/ tests/
```

Expected: no diff output then `fidelity=0`; no `uniq -d` output; `build=0` with no `WARNING` lines; `lint=0`; and the `src/`/`tests/` diffstat is **empty** — this branch changed no code.

- [ ] **Step 4: Record the baseline's new status**

Append to `.migration/README.md`: `slugs-source.txt` is now the frozen baseline; `NEW_RULES.md` was deleted in this commit; `inventory.tsv`'s `start_line`/`end_line` columns refer to that deleted file's line numbers and are historical, not resolvable against the working tree.

- [ ] **Step 5: Commit**

```bash
git add -A .migration/
git commit -m "docs(migration): retire the source document after fidelity verification"
```

- [ ] **Step 6: Report to the operator**

The operator owns git remotes. Report the commit range and the verification output; **do not push or open a PR** unless asked.

---

## Handoff Notes — Environment State at Planning Time

Everything below was read on 2026-07-26 on this branch. It is reproduced here so the executor does not have to re-read the files to get started, and so the facts survive compaction.

### Git state

Branch `docs/realign-specs`. Staged 0, modified 0, **untracked 5** (one of which is `NEW_RULES.md`; Task 1 adds it). Run `git status --porcelain` before Task 1 and confirm the untracked set — do not assume it is unchanged, and do not `git add -A` at the repo root, which would sweep in the untracked `tests/` trees that this branch must not touch. Every `git add` in this plan names its paths for that reason.

`main` exists and is the merge-base target for Task 10's diffstat. HEAD at planning time was `1b77597`.

### `docs/mkdocs.yml` in full, before any task touches it

```yaml
site_name: humansays
docs_dir: site
site_dir: ../site
theme:
  name: material
plugins:
  - search
nav:
  - Overview: index.md
  - Style guide:
      - style-guide/README.md
      - Python: style-guide/python.md
      - Rust: style-guide/rust.md
  - Rules:
      - rules/README.md
      - Python: rules/python.md
  - Roadmap:
      - Future additions: roadmap/future-additions.md
```

There is no `validation:` block today — Task 2 adds one. Nav entries written as a bare path (`style-guide/README.md`) take their title from the page's H1; entries written as `Title: path` override it. Both forms are in use; keep whichever the surrounding block uses.

**`mkdocs.yml` lives at `docs/`, not the repo root.** Every build command in this plan therefore carries `-f docs/mkdocs.yml`. A bare `uv run mkdocs build` from the repo root fails with "config file not found" — that is a wrong invocation, not a migration failure.

If `mkdocs` is not found, the `docs` dependency group is not synced: `uv sync --group docs`.

### `docs/site/index.md` in full — 9 lines, three of the site's four links

```markdown
# humansays

Documentation for the humansays code review tool.

- [Style guide](style-guide/README.md)
- [Rules](rules/README.md)
- [Roadmap](roadmap/future-additions.md)
```

Task 3 repoints line 7 at `rules/legacy/README.md`; Task 6 repoints it at `rules/python/index.md`; Task 9 may remove line 8. Line 6 never changes.

### The 19 shipped rules, for Task 7's `shipped-rules.md`

From `src/humansays/catalog.py:18-197`. Confidence and weight as shown; where weight is omitted below the agent must read it rather than guess.

| Code | Signal name | Severity | Confidence | Weight |
|---|---|---|---|---|
| HS001 | many-arguments | WARNING | 0.80 | 3.0 |
| HS002 | boolean-modes | ADVISORY | 0.82 | 1.0 |
| HS003 | deep-nesting | WARNING | 0.76 | 3.0 |
| HS004 | shared-mutable-state | WARNING | 0.95 | 3.0 |
| HS005 | broad-exception | WARNING | 0.96 | 3.0 |
| HS006 | multiple-mutation-owners | WARNING | 0.95 | 3.0 |
| HS007 | mixed-boundaries | WARNING | 0.65 | 3.0 |
| HS008 | low-class-cohesion | ADVISORY | 0.65 | 1.0 |
| HS009 | long-function | ADVISORY | 0.55 | 1.0 |
| HS012 | many-class-attributes | ADVISORY | 0.72 | 1.0 |
| HS013 | attribute-prefix-cluster | WARNING | 0.84 | read from source |
| HS014 | validated-argument-bundle | WARNING | 0.88 | read from source |
| HS015 | static-method | WARNING | 0.99 | 3.0 |
| HS016 | lambda-expression | WARNING | 0.99 | 3.0 |
| HS017 | long-file | WARNING | 0.60 | 3.0 |
| HS018 | many-base-classes | WARNING | 0.99 | 3.0 |
| HS019 | many-branches | WARNING | 0.74 | 3.0 |
| HS021 | lazy-import | ADVISORY | 0.85 | 1.0 |
| HS022 | dense-function | WARNING | 0.72 | 3.0 |

**This table is a cross-check, not the source.** Task 7's agent reads `catalog.py` and reports any disagreement with the above rather than copying it.

Packaging facts for `reference/index.md`: `name = "humansays"`, `version = "0.1.0a1"`, `requires-python = ">=3.11"`, console script `humansays = "humansays.cli:main"`, optional extra `terminal = ["rich>=13.7"]`. `rich` is optional with an ANSI fallback — **do not document it as required.**

### Commit message format, verbatim from `scripts/check_commit_msg.py`

```python
PREFIXES = ('feat', 'chore', 'ops', 'fix', 'release', 'docs')
SUBJECT = re.compile(r'^(?P<prefix>[a-z]+)\((?P<scope>[^()\s]+)\): (?P<summary>\S.*)')
MERGES  = re.compile(r' \[merges #\d+\]')
```

Summary must start lowercase and must not end with a period. The scope may not contain spaces or parentheses. Every commit subject in this plan already conforms — use them as written. This runs as a `commit-msg` stage pre-commit hook.

### Things you will encounter that are not bugs

- **`src/humansays/analysis/rules.py:6-12` documents contract debt in a module docstring**: the module fuses AST extraction with rule evaluation, and splitting it into a `humansays.signals` layer is explicitly noted as out of scope. Task 7's agent will read this. It is a known, recorded design compromise — document the behavior, do not file it as a defect and do not fix it.
- **`docs/site/rules/python.md` mentions `.agent-specs/phases/...` at lines 32, 142, 191, 213 and 335.** These are backtick-quoted plain text, not markdown links, so MkDocs will not flag them and `unrecognized_links` will not catch them. After Task 9 deletes the phases tree they become stale references — on a page already banner-marked superseded. **Leave them.** The superseded banner from Task 3 Step 2 covers it; rewriting a historical page's body contradicts keeping it as a record.
- **Gaps at `HS010`, `HS011`, `HS020` in the shipped codes are intentional**, matching the three prototype checks §8 marks omitted. Not missing implementations.

### Notes on dispatching the subagents

- Extraction agents need `Bash` to run `sed`, and `Skill` for `humanizer`. The `implementer` agent type has both. **Instruct them explicitly to use `sed`, not `Read`** — an agent that reaches for `Read` on `NEW_RULES.md` will pull the whole 690-line file into its context and violate the standing constraint.
- Subagent working directory is `/home/rhawk/dev/humansays`. The `sed` commands in the extraction prompt use the repo-relative path `NEW_RULES.md`.
- Do not run the verification shell snippets under `set -e`. `grep -c` exits 1 on a zero count, which is a legitimate result for several checks (notably `accounting.md`, which may contain no table rows at all) and would abort the script.
- Take the agents' reported counts as a claim, not a result. Every task's verification step re-measures from the coordinator for that reason.

---

## Deliberately Out of Scope

- **`src/` and `tests/` are not touched.** Tasks 7, 8, and 10 verify this.
- `tests/criteria/` and `tests/unit/` are currently **untracked**, and one file under `tests/criteria/` references a phase directory Task 9 deletes. Leave both alone; raise the untracked state with the operator separately.
- One script under `scripts/` consumes the retired phase directories and will stop working once they are deleted. Nothing in CI or pre-commit invokes it. Flagged for the operator; no task here touches it.
- `docs/evidence/*.md` mentions `docs/phases/…`. Those are historical records of completed work and stay as written.
- `docs/site/style-guide/{python,rust}.md` are unchanged.
- No `src` implementation work, no rule implementation, no phase planning. This branch is preliminary realignment only.

## Not Investigated — Assumption, Not Verified Fact

- **Whether the new catalog satisfies the standing constraint that every rule cite a criteria-document section** (project `CLAUDE.md` rule 9). The new IDs cite `HS-` source slugs, not `style-guide/python.md` sections. This looks like a real gap. It belongs in `.agent-specs/backlog.md`, not in this branch — Task 9 Step 2 adds it there.
- **Whether any rule row in `NEW_RULES.md` carries meaningful trailing whitespace.** If one does, the `trailing-whitespace` pre-commit hook will alter it during Task 4 or 5 and every check in this plan will still pass, because they count slugs and rows rather than bytes. Judged low risk for markdown table cells; not checked. Cheap to rule out before Task 4 with `grep -nE ' +$' NEW_RULES.md`, which should print nothing.
- Whether §5's message templates are consistent with `src/`'s reporting layer. Nothing here changes either.
- Whether the 209-row ledger is internally consistent beyond the row counts and disposition tallies stated above. Individual mappings were **not** audited; Task 8's agent is the first to check any of them.
- Whether the site renders correctly in a browser. `--strict` proves structural validity, not visual correctness.
- The exact table-cell formatting of §6, §7, §8, and §10. Task 5's verification is therefore a source-to-destination row-count diff rather than a format-specific regex.
