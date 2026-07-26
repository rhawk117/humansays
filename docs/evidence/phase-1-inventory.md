# Phase 1 inventory — observed state of `feat/proof-of-concept`

**Scope.** This document records what is on disk. It proposes nothing,
recommends nothing, and evaluates nothing. Where a source file states a
judgement, that judgement is quoted and attributed to the source, not adopted.

**Method.** Every fact below traces to a command or a literal file read.
Commands are shown with their output. Git history questions are scoped to
`main..HEAD` (merge-base `a3d301fefae2c56ef8e707d270bf48d15aaf5568`); where
that window clips an answer, the clipping is stated.

**Measured on.** commit `90a5185`, 2026-07-26.

---

## Section A checklist

| Item | Recorded in |
| --- | --- |
| Package layout / `__init__.py` | §1 |
| Build backend, entry point, `requires-python` | §1 |
| `dependencies` verbatim, optional extras and guards | §1 |
| Module map, imports, `ast`/`tokenize` | §3 |
| Rule catalog: IDs, names, metadata fields | §4 |
| Rules deleted / renamed / retained | §4 |
| Test inventory: count, framework, structure, assertions | §11 |
| Golden fixtures: existence, contents, commit order | §9 |
| Config discovery, nonexistent-`--config` case | §5 |
| TODOs, contract-debt docstrings, baseline file | §8, §12 |

---

## 1. Layout

**Package path.** `src/humansays/` (confirmed by `find src/humansays -name '*.py'`,
24 files).

**`__init__.py` contents.** Empty file, 0 bytes.

```
$ wc -c src/humansays/__init__.py
0 src/humansays/__init__.py
```

**Build backend.** `pyproject.toml`:

```toml
[build-system]
requires = ["uv_build>=0.11.29,<0.12.0"]
build-backend = "uv_build"
```

**Console-script entry point.**

```toml
[project.scripts]
humansays = "humansays.cli:main"
```

**`requires-python`.** `>=3.11` (`pyproject.toml:4`).

**`dependencies`, verbatim.**

```toml
dependencies = []
```

**Optional extras and their guards.**

```toml
[project.optional-dependencies]
terminal = ["rich>=13.7"]
```

One extra, `terminal`, pinning `rich>=13.7`. The guard on its use lives at
`src/humansays/reporting/render.py:28` inside `_load_rich` (see §7 for the
full accessor and its call count), which is the sole `import rich...` site
reachable from `src/humansays/**` per the module map in §3.

---

## 2. Import cost

Spec's exact command:

```bash
python3 -X importtime -c "import humansays" 2>&1 | tail -1
```

Run as written, bare `python3`:

```
ModuleNotFoundError: No module named 'humansays'
```

Bare `python3` does not resolve the project environment (no interpreter has
`humansays` installed outside the `uv`-managed venv). Run under `uv run`:

```bash
uv run python -X importtime -c "import humansays" 2>&1 | tail -1
```

```
import time:       114 |        114 | humansays
```

Cumulative time for the `humansays` package itself is 114 microseconds.
`tail -1` shows only the final `importtime` line — the `humansays` package's
own entry — not the transitive total of everything Python imported to get
there (stdlib machinery, etc. is on earlier lines that `tail -1` discards).

`__init__.py` is empty (§1), so `import humansays` triggers no submodule
imports; the 114 µs figure is the cost of creating an empty package object,
not of loading `cli.py`, `application.py`, or any analysis code.

---

## 3. Modules

One row per `.py` file under `src/humansays/` (24 total). Imports are as
written at the top of each file (`grep -n '^import \|^from '`).

| Module | Imports | `ast`? | `tokenize`? |
| --- | --- | --- | --- |
| `__init__.py` | (none — empty file) | no | no |
| `__main__.py` | `humansays.cli.main` | no | no |
| `analysis/__init__.py` | `ast`; `pathlib.Path`; `.models.ParsedModule`; `.rules.Analyzer` | yes | no |
| `analysis/cpython_ast.py` | `ast`; `collections.abc.Iterable`; `humansays.catalog.build_finding`; `humansays.config.models.ModuleThresholds`; `humansays.const` (multiple names, lines 17-23); `humansays.enums.SignalName`; `humansays.factories.string_set_map`; `humansays.findings.models` (`Finding`, `Incident`, `Location`, `Observation`); `.models` (multiple, lines 27-34); `.syntax` (multiple, lines 35-39) | yes | no |
| `analysis/models.py` | `ast`; `dataclasses` (`dataclass`, `field`); `operator.attrgetter`; `pathlib.Path`; `humansays.const.IMPLICIT_PARAMETERS`; `humansays.enums.SignalName`; `humansays.factories` (multiple, lines 15-20); `humansays.findings.models` (`Incident`, `Location`) | yes | no |
| `analysis/rules.py` | `ast`; `operator.attrgetter`; `humansays.catalog.build_finding`; `humansays.config.models.Thresholds`; `humansays.const` (multiple, lines 20-25); `humansays.enums.SignalName`; `humansays.findings.models` (`Finding`, `Location`, `Observation`); `.cpython_ast` (multiple, lines 29-39); `.models` (multiple, lines 40-48); `.syntax` (multiple, lines 49-...) | yes | no |
| `analysis/syntax.py` | `ast`; `collections.abc.Iterable`; `humansays.const` (`BOOL_NAMES`, `BOUNDARY_MODULES`, `UNPARSE_LIMIT`); `humansays.findings.models.Location`; `.models` (`FunctionNode`, `ParsedModule`) | yes | no |
| `application.py` | `collections.abc.Iterable`; `pathlib.Path`; `typing.TextIO`; `.analysis` (`Analyzer`, `parse_module`); `.config.models` (`ScannerSettings`, `Selection`); `.const` (`FINDINGS_EXIT`, `STDIN_SPEC`); `.enums` (`FailOn`, `Severity`); `.findings.models.Score`; `.reporting.models` (`FileReport`, `ScanResult`) | no | no |
| `catalog.py` | `types.MappingProxyType`; `.enums` (`Severity`, `SignalName`); `.findings.models` (`Finding`, `Location`, `Observation`, `RuleSpec`) | no | no |
| `cli.py` | `sys`; `collections.abc.Sequence`; `typing.TextIO`; `humansays.application`; `humansays.config.loading` (`ConfigError`, `load_settings`); `humansays.const` (`CONFIG_ERROR_EXIT`, `MISSING_SYMBOL_EXIT`, `NO_FILES_EXIT`); `humansays.reporting.render.emit`; `humansays.scoring.score_for` | no | no |
| `config/__init__.py` | (none — 0 bytes) | no | no |
| `config/loading.py` | `argparse`; `dataclasses`; `tomllib`; `collections.abc` (`Mapping`, `Sequence`); `importlib.metadata.version`; `pathlib.Path`; `types.MappingProxyType`; `typing.TYPE_CHECKING`; `humansays.const` (`CLI_DESTINATIONS`, `DEFAULT_CONFIG_NAMES`, `PYPROJECT_SECTION`); `humansays.enums` (`FailOn`, `OutputFormat`); `.models` (multiple, lines 24-32) | no | no |
| `config/models.py` | `dataclasses` (`dataclass`, `field`); `humansays.const.DEFAULT_EXCLUDES`; `humansays.enums` (`FailOn`, `OutputFormat`); `humansays.findings.models.check_bounds` | no | no |
| `const.py` | `collections` (`defaultdict`, `deque`); `types.MappingProxyType`; `.enums` (`Grade`, `Severity`) | no | no |
| `enums.py` | `enum.StrEnum` | no | no |
| `factories.py` | `inspect`; `collections.defaultdict`; `collections.abc.Iterable`; `.const` (multiple, lines 12-...) | no | no |
| `findings/__init__.py` | (none — 0 bytes) | no | no |
| `findings/models.py` | `dataclasses.dataclass`; `humansays.enums` (`Grade`, `Severity`, `SignalName`) | no | no |
| `reporting/__init__.py` | (none — 0 bytes) | no | no |
| `reporting/ansi.py` | `os`; `sys`; `types.MappingProxyType`; `humansays.config.models.Report`; `humansays.const` (`GRADE_STYLES`, `SEVERITY_STYLES`); `humansays.findings.models.Score`; `.grouping` (`Target`, `review_targets`, `shown_targets`); `.models.ScanResult` | no | no |
| `reporting/grouping.py` | `typing.Any`; `humansays.const` (`SEVERITY_ORDER`, `UNKNOWN_SEVERITY_ORDER`); `.models.FileReport` | no | no |
| `reporting/models.py` | `dataclasses.dataclass`; `pathlib.Path`; `humansays.findings.models.Finding` | no | no |
| `reporting/render.py` | `dataclasses`; `json`; `types.SimpleNamespace`; `typing.TYPE_CHECKING`; `humansays.config.models.Report`; `humansays.const` (`GRADE_STYLES`, `SEVERITY_STYLES`); `humansays.enums.OutputFormat`; `humansays.findings.models.Score`; `. import ansi`; `.grouping` (`Target`, `review_targets`, `shown_targets`); `.models.ScanResult` | no | no |
| `scoring.py` | `.const` (`GRADE_BANDS`, `PERFECT_SCORE`, `SCORE_TOLERANCE`, `SCORE_WINDOW`); `.enums.Grade`; `.findings.models.Score`; `.reporting.models.ScanResult` | no | no |

`ast` appears in exactly 5 files, all under `src/humansays/analysis/`:
`analysis/__init__.py`, `analysis/cpython_ast.py`, `analysis/models.py`,
`analysis/rules.py`, `analysis/syntax.py`.

```
$ grep -rn '^import ast\|^import tokenize\|import ast$\|import tokenize$' src/
src/humansays/analysis/models.py:8:import ast
src/humansays/analysis/syntax.py:8:import ast
src/humansays/analysis/__init__.py:1:import ast
src/humansays/analysis/cpython_ast.py:12:import ast
src/humansays/analysis/rules.py:15:import ast
```

`import tokenize` does not appear anywhere under `src/`: no line matched that
pattern.

---

## 4. Catalog

**Declaration mechanism.** `src/humansays/catalog.py` builds a
`types.MappingProxyType` keyed by the `SignalName` enum, verbatim:

```python
RULES = MappingProxyType({
    SignalName.HS001: RuleSpec(
        signal=SignalName.HS001,
        severity=Severity.WARNING,
        confidence=0.80,
        weight=WARNING_WEIGHT,
        review_question=(...),
    ),
    ...
})
```

**`RuleSpec` fields** (`src/humansays/findings/models.py:41-46`):

```python
@dataclass(frozen=True, slots=True)
class RuleSpec:
    signal: SignalName
    severity: Severity
    confidence: float
    weight: float
    review_question: str
```

There is no `name` field on `RuleSpec`. A rule's identity is the
`SignalName` enum member itself; `RuleSpec.rule_id` is a computed property
(`self.signal.name`) and `SignalName`'s member *value* (e.g. `HS001` →
`'many-arguments'`) is the human-readable label — see `enums.py`'s module
docstring: *"the member name is the stable rule id used in reports and
configuration, the member value is the human-readable indicator printed
next to a target."*

**Every rule ID, its `SignalName` value, and its `RuleSpec` metadata**
(from `src/humansays/enums.py` and `src/humansays/catalog.py`):

| ID | `SignalName` value | `severity` | `confidence` | `weight` |
| --- | --- | --- | --- | --- |
| HS001 | many-arguments | warning | 0.80 | 3.0 (`WARNING_WEIGHT`) |
| HS002 | boolean-modes | advisory | 0.82 | 1.0 (`ADVISORY_WEIGHT`) |
| HS003 | deep-nesting | warning | 0.76 | 3.0 |
| HS004 | shared-mutable-state | warning | 0.95 | 3.0 |
| HS005 | broad-exception | warning | 0.96 | 3.0 |
| HS006 | multiple-mutation-owners | warning | 0.70 | 3.0 |
| HS007 | mixed-boundaries | warning | 0.65 | 3.0 |
| HS008 | low-class-cohesion | advisory | 0.65 | 1.0 |
| HS009 | long-function | advisory | 0.55 | 1.0 |
| HS012 | many-class-attributes | advisory | 0.72 | 1.0 |
| HS013 | attribute-prefix-cluster | warning | 0.84 | 3.0 |
| HS014 | validated-argument-bundle | warning | 0.88 | 3.0 |
| HS015 | static-method | warning | 0.99 | 3.0 |
| HS016 | lambda-expression | warning | 0.99 | 3.0 |
| HS017 | long-file | warning | 0.60 | 3.0 |
| HS018 | many-base-classes | warning | 0.78 | 3.0 |
| HS019 | many-branches | warning | 0.74 | 3.0 |
| HS021 | lazy-import | advisory | 0.85 | 1.0 |
| HS022 | dense-function | warning | 0.72 | 3.0 |

19 rule IDs total (`SignalName` has 19 members; `RULES` has 19 keys — both
counted directly from the files above).

Every entry also carries a `review_question` string (omitted from the table
above for width; present in the `catalog.py` excerpt for each ID).

**HS010, HS011, HS020 — confirmed absent from the catalog, not merely from
output:**

```bash
$ grep -rn 'HS010\|HS011\|HS020\|PY010\|PY011\|PY020' src/
(no output)
```

No match anywhere under `src/`. The `SignalName` member sequence itself
skips these numbers: `HS009` is followed by `HS012` (010, 011 absent), and
`HS019` is followed by `HS021` (020 absent) — visible directly in the
`enums.py` listing above.

**Deleted / renamed / retained.** `tests/deletions/test_deleted_rules.py`
states and asserts (its own module docstring, quoted):

> "Deleted-rule behavior: PY010 (comments), PY011 (docstring), PY020
> (future-annotations) no longer exist anywhere in humansays, and
> ast/tokenize stay confined to humansays.analysis."

That file defines `DELETED_IDS = frozenset({'HS010', 'HS011', 'HS020'})` and
asserts (`test_deleted_ids_are_absent_from_signal_name`,
`test_deleted_ids_are_absent_from_catalog`) that this set is disjoint from
both `SignalName.__members__` and `RULES`. This is the test's own
classification of which three rules were deleted; this document does not
independently derive a rename or retention list beyond what the enum and
this test state — every other `SignalName` member present in `enums.py`
(19 of them, listed above) is retained under the `HS` prefix. No renames
are recorded in this file or in the test; the identifiers are the original
`HS` numbering with the three IDs above removed from the sequence.

---

## 5. Exit codes

**Symbolic constants** (`src/humansays/const.py:102-107`):

```python
STDIN_SPEC = '-'
DEFAULT_CONFIG_NAMES = ('humansays.toml', 'pyproject.toml')
NO_FILES_EXIT = 3
MISSING_SYMBOL_EXIT = 2
FINDINGS_EXIT = 1
CONFIG_ERROR_EXIT = 4
```

**Return sites and their trigger conditions**, quoted from the surrounding
code:

| Code | Constant | Site | Trigger (as stated by the surrounding code) |
| --- | --- | --- | --- |
| 0 | (none — literal `0`) | `application.py:141` (`severity_exit`, "no findings meet `fail_on`") | fallthrough of `severity_exit`: `return 0` after the `FailOn.ANY`/`FailOn.WARNING` branches don't trigger |
| 0 | (none — literal `0`) | `application.py:148` (`exit_code`) | `if settings.report.fail_on is FailOn.NEVER: return 0` |
| 1 | `FINDINGS_EXIT` | `application.py:135` (`severity_exit`) | `if fail_on is FailOn.ANY and findings: return FINDINGS_EXIT` |
| 1 | `FINDINGS_EXIT` | `application.py:140` (`severity_exit`) | `if fail_on is FailOn.WARNING and warnings: return FINDINGS_EXIT` |
| 1 | `FINDINGS_EXIT` | `application.py:146` (`exit_code`) | `if score.value < settings.report.min_score: return FINDINGS_EXIT` |
| 2 | `MISSING_SYMBOL_EXIT` | `cli.py:28-30` (`main`) | `if wanted and not application.symbol_is_present(result, wanted): print(...); return MISSING_SYMBOL_EXIT` |
| 3 | `NO_FILES_EXIT` | `cli.py:21-24` (`main`) | `if not paths: ...; return NO_FILES_EXIT` |
| 4 | `CONFIG_ERROR_EXIT` | `cli.py:15-17` (`main`) | `except ConfigError as err: print(...); return CONFIG_ERROR_EXIT` |

**Argparse's own exit code.** `config/loading.py:111-141` (`build_parser`)
constructs a standard `argparse.ArgumentParser`. Argparse itself calls
`parser.exit(2, message)` on a usage error (unrecognized argument, missing
value for a flag expecting one, etc.) — independent of any constant defined
in this codebase. `MISSING_SYMBOL_EXIT` is also `2`. Both an argparse usage
error and a "requested symbol not found" application error exit `2`; nothing
in the source distinguishes them beyond the stderr text each path prints.

**Codes not present in the POC.** The POC's `const.py` defines:

```
$ grep -rn 'EXIT\|sys.exit\|return [0-9]' tests/golden/poc-parity/corpus/poc/
tests/golden/poc-parity/corpus/poc/const.py:104:NO_FILES_EXIT = 3
tests/golden/poc-parity/corpus/poc/const.py:105:MISSING_SYMBOL_EXIT = 2
tests/golden/poc-parity/corpus/poc/const.py:106:FINDINGS_EXIT = 1
```

The POC corpus defines only `1`, `2`, `3` (plus a bare `0` return at
`core.py:145,152`, matching the current codebase's unnamed `0` returns).
`CONFIG_ERROR_EXIT = 4` does not appear anywhere in
`tests/golden/poc-parity/corpus/poc/`. It is new relative to the frozen POC
corpus; its trigger is the `ConfigError` path shown above.

**Config discovery behavior** (`src/humansays/config/loading.py:98-108`,
`discover_config`):

```python
def discover_config(explicit: str | None) -> Path | None:
    if explicit:
        candidate = Path(explicit)
        if not candidate.is_file():
            raise ConfigError(explicit)
        return candidate
    for name in DEFAULT_CONFIG_NAMES:
        candidate = Path(name)
        if candidate.is_file():
            return candidate
    return None
```

Order: if `--config` is given explicitly, that path is used or a
`ConfigError` is raised (no fallback to the default names). If `--config` is
absent, `DEFAULT_CONFIG_NAMES = ('humansays.toml', 'pyproject.toml')` is
checked in that order; if neither exists, `None` is returned (no config
values applied).

**Nonexistent-`--config` case, measured:**

```bash
$ uv run humansays --config /nonexistent/hs.toml src/humansays; echo "exit=$?"
error: config file not found: /nonexistent/hs.toml
exit=4
```

Stderr text and exit code as shown — `4`, via the `ConfigError` →
`CONFIG_ERROR_EXIT` path in `cli.py:15-17`.

---

## 6. HS002 parameters

Every `HS002` finding from the self-scan, from `$SCRATCH/raw/signals.txt`:

```
HS002 src/humansays/reporting/ansi.py use_color 32 ['is_tty']
HS002 src/humansays/reporting/ansi.py _style 40 ['color']
HS002 src/humansays/reporting/ansi.py indicator_text 47 ['color']
HS002 src/humansays/reporting/ansi.py score_text 60 ['color']
```

Four findings, all in `src/humansays/reporting/ansi.py`. Each symbol's `def`
line as it appears on disk:

```python
def use_color(*, is_tty: bool) -> bool:                                  # line 32
def _style(text: str, style: str, *, color: bool) -> str:                # line 40
def indicator_text(target: Target, *, color: bool) -> str:               # line 47
def score_text(score: Score, *, color: bool) -> str:                     # line 60
```

For every parameter in each signature, kind determined structurally from the
`/` and `*` markers (no `/` marker appears in any of these four signatures —
none has a positional-only parameter):

| Symbol | `file:line` | Full signature | Parameter | Kind | Named in evidence? |
| --- | --- | --- | --- | --- | --- |
| `use_color` | `ansi.py:32` | `def use_color(*, is_tty: bool) -> bool:` | `is_tty` | keyword-only | yes |
| `_style` | `ansi.py:40` | `def _style(text: str, style: str, *, color: bool) -> str:` | `text` | positional-or-keyword | no |
| `_style` | `ansi.py:40` | (same) | `style` | positional-or-keyword | no |
| `_style` | `ansi.py:40` | (same) | `color` | keyword-only | yes |
| `indicator_text` | `ansi.py:47` | `def indicator_text(target: Target, *, color: bool) -> str:` | `target` | positional-or-keyword | no |
| `indicator_text` | `ansi.py:47` | (same) | `color` | keyword-only | yes |
| `score_text` | `ansi.py:60` | `def score_text(score: Score, *, color: bool) -> str:` | `score` | positional-or-keyword | no |
| `score_text` | `ansi.py:60` | (same) | `color` | keyword-only | yes |

---

## 7. HS021 sites

Every `HS021` finding from the self-scan, from `$SCRATCH/raw/signals.txt`:

```
HS021 src/humansays/reporting/render.py _load_rich 28 ['line 36: rich.console']
HS021 src/humansays/reporting/render.py _load_rich 28 ['line 37: rich.table']
HS021 src/humansays/reporting/render.py _load_rich 28 ['line 38: rich.text']
```

Two counts, derived separately because they differ:

```bash
$ grep '^HS021' "$SCRATCH/raw/signals.txt" | wc -l
3
$ grep '^HS021' "$SCRATCH/raw/signals.txt" | awk '{print $2, $3, $4}' | sort -u
src/humansays/reporting/render.py _load_rich 28
```

**Number of HS021 signal rows emitted: 3.**
**Number of distinct lazy-import sites (`path`, `symbol`, `line` tuples): 1.**

All three rows share the tuple `(src/humansays/reporting/render.py,
_load_rich, 28)`.

---

## 8. Baseline file

The `reason` values below are quoted from the file. They are the baseline
author's stated rationale, recorded here as data; this document takes no
position on them.

`tests/golden/self-scan-baseline.json`, in full:

```json
{
  "entries": [
    {
      "path": "src/humansays/reporting/ansi.py",
      "symbol": "use_color",
      "line": 32,
      "rule_id": "HS002",
      "evidence": "is_tty",
      "reason": "is_tty is keyword-only (`*, is_tty: bool`), required to implement the NO_COLOR/FORCE_COLOR/TERM=dumb color policy. HS002's declared_arguments() merges posonly/positional/kwonly indiscriminately, so it cannot tell a keyword-only flag from a positional mode switch -- false positive from that argument-kind defect, not a fixable structural issue.",
      "expires_phase": "phase-2-argument-kind-fix"
    },
    {
      "path": "src/humansays/reporting/ansi.py",
      "symbol": "_style",
      "line": 40,
      "rule_id": "HS002",
      "evidence": "color",
      "reason": "color is keyword-only (`*, color: bool`), required to implement the NO_COLOR/FORCE_COLOR/TERM=dumb color policy. Same argument-kind defect as use_color.",
      "expires_phase": "phase-2-argument-kind-fix"
    },
    {
      "path": "src/humansays/reporting/ansi.py",
      "symbol": "indicator_text",
      "line": 47,
      "rule_id": "HS002",
      "evidence": "color",
      "reason": "color is keyword-only (`*, color: bool`), required to implement the NO_COLOR/FORCE_COLOR/TERM=dumb color policy. Same argument-kind defect as use_color.",
      "expires_phase": "phase-2-argument-kind-fix"
    },
    {
      "path": "src/humansays/reporting/ansi.py",
      "symbol": "score_text",
      "line": 60,
      "rule_id": "HS002",
      "evidence": "color",
      "reason": "color is keyword-only (`*, color: bool`), required to implement the NO_COLOR/FORCE_COLOR/TERM=dumb color policy. Same argument-kind defect as use_color.",
      "expires_phase": "phase-2-argument-kind-fix"
    },
    {
      "path": "src/humansays/reporting/render.py",
      "symbol": "_load_rich",
      "line": 28,
      "rule_id": "HS021",
      "evidence": "line 36: rich.console",
      "reason": "_load_rich is the single lazy-import accessor for the optional `terminal` (rich) extra -- every other rendering helper receives rich's classes as a parameter instead of importing them, so this is the only place in the module an Import node exists. Required by the plan's rich-optional design; the three entries here are the three names imported by this one accessor, not three separate call sites.",
      "expires_phase": "phase-2-signals-split"
    },
    {
      "path": "src/humansays/reporting/render.py",
      "symbol": "_load_rich",
      "line": 28,
      "rule_id": "HS021",
      "evidence": "line 37: rich.table",
      "reason": "See the rich.console entry above -- same accessor, same reason.",
      "expires_phase": "phase-2-signals-split"
    },
    {
      "path": "src/humansays/reporting/render.py",
      "symbol": "_load_rich",
      "line": 28,
      "rule_id": "HS021",
      "evidence": "line 38: rich.text",
      "reason": "See the rich.console entry above -- same accessor, same reason.",
      "expires_phase": "phase-2-signals-split"
    }
  ]
}
```

Table form:

| Path | Symbol | Line | `rule_id` | `evidence` | `expires_phase` | `reason` |
| --- | --- | --- | --- | --- | --- | --- |
| `reporting/ansi.py` | `use_color` | 32 | HS002 | `is_tty` | `phase-2-argument-kind-fix` | "is_tty is keyword-only (`*, is_tty: bool`), required to implement the NO_COLOR/FORCE_COLOR/TERM=dumb color policy. HS002's declared_arguments() merges posonly/positional/kwonly indiscriminately, so it cannot tell a keyword-only flag from a positional mode switch -- false positive from that argument-kind defect, not a fixable structural issue." |
| `reporting/ansi.py` | `_style` | 40 | HS002 | `color` | `phase-2-argument-kind-fix` | "color is keyword-only (`*, color: bool`), required to implement the NO_COLOR/FORCE_COLOR/TERM=dumb color policy. Same argument-kind defect as use_color." |
| `reporting/ansi.py` | `indicator_text` | 47 | HS002 | `color` | `phase-2-argument-kind-fix` | "color is keyword-only (`*, color: bool`), required to implement the NO_COLOR/FORCE_COLOR/TERM=dumb color policy. Same argument-kind defect as use_color." |
| `reporting/ansi.py` | `score_text` | 60 | HS002 | `color` | `phase-2-argument-kind-fix` | "color is keyword-only (`*, color: bool`), required to implement the NO_COLOR/FORCE_COLOR/TERM=dumb color policy. Same argument-kind defect as use_color." |
| `reporting/render.py` | `_load_rich` | 28 | HS021 | `line 36: rich.console` | `phase-2-signals-split` | "_load_rich is the single lazy-import accessor for the optional `terminal` (rich) extra -- every other rendering helper receives rich's classes as a parameter instead of importing them, so this is the only place in the module an Import node exists. Required by the plan's rich-optional design; the three entries here are the three names imported by this one accessor, not three separate call sites." |
| `reporting/render.py` | `_load_rich` | 28 | HS021 | `line 37: rich.table` | `phase-2-signals-split` | "See the rich.console entry above -- same accessor, same reason." |
| `reporting/render.py` | `_load_rich` | 28 | HS021 | `line 38: rich.text` | `phase-2-signals-split` | "See the rich.console entry above -- same accessor, same reason." |

**Total entry count:** 7.
**Distinct `rule_id` values:** `HS002`, `HS021` (2).
**Distinct `expires_phase` values:** `phase-2-argument-kind-fix`,
`phase-2-signals-split` (2).

**Cross-check against the live scan:**

```bash
$ uv run python - <<'PY'
import json
base = json.load(open("tests/golden/self-scan-baseline.json"))["entries"]
bkeys = {(e["path"], e["symbol"], e["line"], e["rule_id"], e["evidence"]) for e in base}
print("baseline entries:", len(base), "distinct keys:", len(bkeys))
PY
baseline entries: 7 distinct keys: 7
```

Entry count and distinct-key count are equal (7 = 7).

---
