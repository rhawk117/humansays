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

## 9. Golden fixtures

**What exists**, `find tests/golden -type f | sort`:

```
tests/golden/__init__.py
tests/golden/poc-parity/_generate.py
tests/golden/poc-parity/corpus/django/NOTICE.md
tests/golden/poc-parity/corpus/django/django/core/exceptions.py
tests/golden/poc-parity/corpus/django/django/utils/dateparse.py
tests/golden/poc-parity/corpus/django/django/utils/text.py
tests/golden/poc-parity/corpus/poc/__init__.py
tests/golden/poc-parity/corpus/poc/__main__.py
tests/golden/poc-parity/corpus/poc/catalog.py
tests/golden/poc-parity/corpus/poc/const.py
tests/golden/poc-parity/corpus/poc/core.py
tests/golden/poc-parity/corpus/poc/enums.py
tests/golden/poc-parity/corpus/poc/factories.py
tests/golden/poc-parity/corpus/poc/models.py
tests/golden/poc-parity/corpus/poc/options.py
tests/golden/poc-parity/corpus/poc/py_ast.py
tests/golden/poc-parity/corpus/poc/report.py
tests/golden/poc-parity/corpus/poc/rules.py
tests/golden/poc-parity/corpus/poc/scoring.py
tests/golden/poc-parity/corpus/poc/syntax.py
tests/golden/poc-parity/django.pysignals.json
tests/golden/poc-parity/django.pysignals.txt
tests/golden/poc-parity/django.raw.json
tests/golden/poc-parity/manifest.toml
tests/golden/poc-parity/mapping.toml
tests/golden/poc-parity/poc.pysignals.json
tests/golden/poc-parity/poc.pysignals.txt
tests/golden/poc-parity/poc.raw.json
tests/golden/self-scan-baseline.json
tests/golden/test_parity.py
tests/golden/test_self_scan.py
```

**Contents, one line per non-corpus fixture:**

| File | Contents (first lines / stated purpose) |
| --- | --- |
| `manifest.toml` | Corpus pin: `pysignals_version = "0.3.0"`, per-group `root`/`files` lists, the Django sdist URL and `sha256`. Header comment: "Corpus pinned for the humansays parity oracle... .raw.json outputs alongside this file are the frozen pysignals 0.3.0 oracle to compare against." |
| `mapping.toml` | `deleted = ["PY010", "PY011", "PY020"]` plus a `[rename]` table mapping every surviving `PY###` id to its `HS###` counterpart. Header comment: "PY-id -> HS-id rename table used to transform the raw poc-parity oracle. Every surviving rule keeps its original number; only its two-letter prefix changes." |
| `poc.raw.json` | Authoritative per-finding oracle for the `poc` corpus group — a `{"findings": [...]}` array of raw pysignals 0.3.0 output (e.g. first entry: `path: __init__.py, rule_id: PY011, symbol: <module>, line 1`). |
| `django.raw.json` | Same shape as `poc.raw.json`, for the `django` corpus group. |
| `poc.pysignals.json` | Reference-only CLI JSON output (`schema_version: 4`) for the `poc` group, `root` listing absolute paths under `.poc-reference/pysignals-0.3.0/pysignals/...`. |
| `django.pysignals.json` | Same shape, for the `django` group, `root` listing absolute paths under a scratchpad `django-src/` checkout. |
| `poc.pysignals.txt` | Reference-only plain-text CLI rendering of the `poc` group scan (`Python investigation targets ...`). |
| `django.pysignals.txt` | Same, for the `django` group. |
| `_generate.py` | One-time generator script, explicitly marked "NOT a test" in its own docstring. Docstring states it "Writes, for every group in manifest.toml: `<group>.raw.json` (the authoritative per-finding oracle used by `tests/golden/test_parity.py`) plus `<group>.pysignals.json` and `<group>.pysignals.txt` (reference-only CLI output, NOT asserted against for groups whose CLI JSON aggregates multiple findings per symbol)." |
| `corpus/poc/*.py` (14 files) | Vendored proof-of-concept source, matching `manifest.toml`'s `[groups.poc].files` list. |
| `corpus/django/*.py` (3 files) + `NOTICE.md` | Vendored Django 5.1.4 subset (`django/core/exceptions.py`, `django/utils/dateparse.py`, `django/utils/text.py`), matching `manifest.toml`'s `[groups.django].files` list. |
| `self-scan-baseline.json` | Quoted in full in §8. |
| `test_parity.py`, `test_self_scan.py` | Test files; assertions recorded in §11. |

**Ordering, branch-scoped (`main..HEAD`).** Earliest commit touching
`tests/golden/**` vs. earliest touching `src/humansays/**`:

| Path | Earliest commit | Timestamp | Subject |
| --- | --- | --- | --- |
| `tests/golden/**` | `1aeeaec` | 2026-07-25T22:27:10-04:00 | test(golden): pin poc-parity corpus (poc source + Django 5.1.4 subset) |
| `src/humansays/**` (branch-scoped) | `2342d6e` | 2026-07-25T22:29:48-04:00 | refactor: scaffold humansays package, drop placeholder entrypoint |

Within the `main..HEAD` window, `tests/golden/**` is touched first — `1aeeaec`
precedes `2342d6e` by 2 minutes 38 seconds.

**Boundary condition.** `src/humansays/**` is not created on this branch;
it already exists at the merge-base:

```
$ git log --reverse --diff-filter=A --format='%h %ad %s' --date=short -- src/humansays | head -5
a3d301f 2026-07-25 feat(setup): setup CI pipeline gates, wire dependency audit, add pre-commit (#1)
2342d6e 2026-07-25 refactor: scaffold humansays package, drop placeholder entrypoint
ade4094 2026-07-25 feat(enums,const): HS ids, humansays config names, config-error exit
34093d4 2026-07-25 feat(findings): dataclass finding models with data-driven validation
3b2f222 2026-07-25 feat(config): frozen-dataclass settings models
```

`a3d301f` **is** the merge-base for this branch (`git merge-base HEAD main`
→ `a3d301fefae2c56ef8e707d270bf48d15aaf5568`). So the unscoped first-add of
`src/humansays/**` sits at or before the branch's starting point. The
`2342d6e` figure above is the first *modification* to `src/humansays/**`
within `main..HEAD`, not the tree's first appearance. Both numbers are
recorded, labelled distinctly, so as not to be mistaken for each other.

**The parity oracle specifically.** Narrower than the module-level
comparison above: does the `poc-parity` fixture set predate the analysis
source it validates?

```
$ git log --reverse --format='%h %cI %s' main..HEAD -- tests/golden/poc-parity
1aeeaec 2026-07-25T22:27:10-04:00 test(golden): pin poc-parity corpus (poc source + Django 5.1.4 subset)
048e303 2026-07-25T22:29:09-04:00 test(golden): freeze raw pysignals 0.3.0 output as parity oracle
fabeb88 2026-07-25T23:10:51-04:00 test(golden): vendor poc/django corpus, JSON parity harness (transform + score recompute)

$ git log --reverse --format='%h %cI %s' main..HEAD -- src/humansays/analysis
2342d6e 2026-07-25T22:29:48-04:00 refactor: scaffold humansays package, drop placeholder entrypoint
d32f138 2026-07-25T22:34:31-04:00 feat(analysis): per-node fact models (only ast-bearing model module)
d6777dc 2026-07-25T22:40:33-04:00 feat(analysis): move syntax/cpython_ast, add parse_module, delete PY020, drop type_comments
af93c29 2026-07-25T23:45:33-04:00 fix(ci): rename .ty.toml -> ty.toml so config is actually discovered, tighten ast node types, fix pre-existing ruff gaps
```

`git show --stat` on each `poc-parity` commit shows what each one actually
added:

- `1aeeaec` (22:27:10) — `manifest.toml` only (35 lines; the corpus pin
  metadata, no oracle data and no corpus source yet).
- `048e303` (22:29:09) — `poc.raw.json`, `django.raw.json` (the authoritative
  per-finding oracle data itself), plus `mapping.toml` and `_generate.py`.
- `fabeb88` (23:10:51) — the vendored corpus source files themselves
  (`corpus/poc/*.py`, `corpus/django/*.py`, `NOTICE.md`) plus an update to
  `manifest.toml`.

Ordering by timestamp: the oracle data (`048e303`, 22:29:09) precedes the
first `src/humansays/analysis` commit on this branch (`2342d6e`, 22:29:48)
by 39 seconds. The vendored corpus *source* files being scanned
(`fabeb88`, 23:10:51) land after three of the four `src/humansays/analysis`
commits on this branch, and before the fourth (`af93c29`, 23:45:33).

---

## 10. Refactors made to satisfy the analyzer

**Candidate search:**

```bash
$ git log --oneline main..HEAD --grep='self-scan' --grep='split' --grep='HS0' --grep='baseline' -i
5699e66 docs(evidence): phase-1 inventory sections 6-8 (HS002 kinds, HS021 sites, baseline)
9a70ce1 fix(self-scan): consolidate rich lazy-import, wrap module dicts, split _render_rich; add self-scan-baseline gate
```

**Considered and excluded:** `5699e66` — this document's own §6-8 commit,
written during this task. It matched the `-i --grep='baseline'` term
because it mentions the baseline file, not because it changes source. `git
show --stat` confirms it touches only `docs/evidence/phase-1-inventory.md`.
Excluded: no source diff.

**Qualifying commit:** `9a70ce1` ("fix(self-scan): consolidate rich
lazy-import, wrap module dicts, split `_render_rich`; add
self-scan-baseline gate"). `git show --stat` for this commit:

```
src/humansays/config/loading.py      |  9 ++--
src/humansays/reporting/ansi.py      |  5 ++-
src/humansays/reporting/render.py    | 87 ++++++++++++++++++++++--------------
tests/golden/self-scan-baseline.json | 67 +++++++++++++++++++++++++++
tests/golden/test_self_scan.py       | 64 ++++++++++++++++++++++++++
5 files changed, 193 insertions(+), 39 deletions(-)
```

Its diff on `src/humansays/reporting/render.py` shows a source function
being restructured, and its own commit message ties the restructuring to
"consolidate rich lazy-import" and "split `_render_rich`" directly — this
document records it under §10 on that basis (the message's own words,
corroborated by the diff).

**Original function.** `_render_rich(result, score, settings)`, before this
commit, contained (per the diff) three inline `from rich.X import Y`
statements at its top, an inline score-line construction block, and an
inline table-construction block; `_rich_indicator_text` separately contained
its own inline `from rich.text import Text`. The baseline file's own
`reason` field for the resulting `HS021` findings (quoted in §8) attributes
this to "the plan's rich-optional design."

**Extracted units**, each with its current `name` and `file:line`:

| Unit | `file:line` |
| --- | --- |
| `_load_rich` | `render.py:28` |
| `_rich_score_line` | `render.py:44` |
| `_rich_targets_table` | `render.py:56` |
| `_rich_indicator_text` | `render.py:109` (signature changed to accept `rich`; not a new function) |

**Call sites**, from `grep -rn '<name>' src/ tests/`:

| Unit | Definition site | Call sites | Other references |
| --- | --- | --- | --- |
| `_load_rich` | `render.py:28` | `render.py:73` (inside `_render_rich`), `render.py:147` (inside `emit`) | `tests/ansi/test_text_snapshot.py:49` — `monkeypatch.setattr(render, '_load_rich', lambda: None)`; also named (not called) in three `tests/golden/self-scan-baseline.json` entries as the flagged symbol |
| `_rich_score_line` | `render.py:44` | `render.py:91` (inside `_render_rich`) | none |
| `_rich_targets_table` | `render.py:56` | `render.py:93` (inside `_render_rich`) | none |
| `_rich_indicator_text` | `render.py:109` | `render.py:67` (inside `_rich_targets_table`) | none |

**State shared with siblings.** Parameters and non-parameter state read by
each extracted unit, determined by reading each signature and body:

| Unit | Parameters | Shared with | Non-parameter (module-level) state read |
| --- | --- | --- | --- |
| `_load_rich` | (none) | — | none |
| `_rich_score_line` | `score`, `rich` | `rich` — also received by `_rich_targets_table`, `_rich_indicator_text` | `GRADE_STYLES` (imported from `humansays.const`) |
| `_rich_targets_table` | `shown`, `rich` | `rich` — also received by `_rich_score_line`, `_rich_indicator_text`; calls `_rich_indicator_text` directly | none read directly (delegates styling to `_rich_indicator_text`) |
| `_rich_indicator_text` | `target`, `rich` | `rich` — also received by `_rich_score_line`, `_rich_targets_table` | `SEVERITY_STYLES` (imported from `humansays.const`) |

All three helper functions (`_rich_score_line`, `_rich_targets_table`,
`_rich_indicator_text`) receive the `SimpleNamespace` returned by
`_load_rich()` as a `rich` parameter rather than importing rich's classes
themselves. `_load_rich` itself takes no parameters and reads no
module-level state beyond the stdlib `try`/`except ImportError` around the
three `from rich.X import Y` statements.

---

## 11. CI

**Workflow files** (`ls .github/workflows/`, 7 files; none deleted in
`main..HEAD` — `git log --diff-filter=D --oneline main..HEAD --
.github/workflows/` produced no output):

| File | Jobs | Triggers | Enabled/disabled | Mechanism / reason (quoted) |
| --- | --- | --- | --- | --- |
| `integration.yml` (name: "Continuous Integration (CI)") | `ci-runbook`, `package`, `ci-gate` | `pull_request`, `workflow_call`, `push` to `main`/`develop` | enabled | — |
| `ci-playbook.yml` (name: "Reusable Python tests") | `linter`, `run-tests` (matrix `["3.11","3.12","3.13","3.14"]`) | `workflow_call` only | enabled (reusable; invoked by `integration.yml` and `release.yml`) | — |
| `build-package.yml` (name: "Reusable package validation") | `build`, `smoke` | `workflow_call` only | enabled (reusable; invoked by `integration.yml` and `release.yml`) | — |
| `release.yml` (name: "Release") | `detect`, `continuous-integration`, `package`, `github-release`; a `publish-pypi` job block is present but fully commented out | `workflow_dispatch`, `push` to `main` on `paths: [pyproject.toml]` | `detect`/`continuous-integration`/`package`/`github-release` enabled; `publish-pypi` disabled | Commented-out job body at `release.yml:75-103`, headed by `# ::NOTE::fix-later` (`release.yml:75`). The `github-release` job's `needs` list carries a stale reference in a trailing comment: `needs: [detect, package] # ::NOTE::publish-pypi` (`release.yml:107`) |
| `security-audit.yml` (name: "Dependency Audit") | `audit` | `pull_request` on `paths: [uv.lock, pyproject.toml]`, weekly `schedule` (`cron: "0 6 * * 1"`), `workflow_dispatch` | enabled | — |
| `github-pages.yml` (name: "Documentation") | `build-docs` (calls `upload-mkdocs.yml`), `deploy` | `workflow_dispatch` only | disabled from automatic triggers | Comment at `github-pages.yml:3-5`, quoted in full: "Disabled in CI: docs/ is being restructured and mkdocs currently fails to build. Kept as a repository artifact, runnable manually until the docs restructuring lands." |
| `upload-mkdocs.yml` (name: "Build Doc Site") | `build` (runs `mkdocs build --strict --clean`) | `workflow_call` only | enabled (reusable; invoked only by `github-pages.yml`) | — |

**mkdocs job: disabled-vs-deleted, measured.**

```bash
$ ls .github/workflows/
build-package.yml  ci-playbook.yml  github-pages.yml  integration.yml
release.yml  security-audit.yml  upload-mkdocs.yml

$ git log --diff-filter=D --oneline main..HEAD -- .github/workflows/
(no output)

$ grep -rn 'mkdocs\|pages\|docs' .github/workflows/
.github/workflows/upload-mkdocs.yml:34:          groups: docs
.github/workflows/upload-mkdocs.yml:36:      - name: Build Mkdocs Site
.github/workflows/upload-mkdocs.yml:39:        run: uv run --locked --group docs mkdocs build --strict --clean
.github/workflows/upload-mkdocs.yml:43:        uses: actions/upload-pages-artifact@v5
.github/workflows/github-pages.yml:3:# Disabled in CI: docs/ is being restructured and mkdocs currently fails to
.github/workflows/github-pages.yml:4:# build. Kept as a repository artifact, runnable manually until the docs
.github/workflows/github-pages.yml:13:  group: pages-${{ github.ref }}
.github/workflows/github-pages.yml:17:  build-docs:
.github/workflows/github-pages.yml:18:    uses: ./.github/workflows/upload-mkdocs.yml
.github/workflows/github-pages.yml:25:    needs: build-docs
.github/workflows/github-pages.yml:29:      pages: write
.github/workflows/github-pages.yml:33:      name: github-pages
.github/workflows/github-pages.yml:39:        uses: actions/deploy-pages@v4
```

Both `github-pages.yml` and `upload-mkdocs.yml` still exist as files; neither
was deleted on this branch (the deleted-file log is empty). The mechanism is
a narrowed trigger set: `github-pages.yml`'s `on:` block was reduced to
`workflow_dispatch` only (no `pull_request`/`push` entry), with the
disabling reason stated in the comment quoted above. `upload-mkdocs.yml`
itself has no trigger of its own (`workflow_call` only, as a reusable
workflow) and is unreachable automatically because its only caller,
`github-pages.yml`, is manual-only.

**Test inventory** (Section A checklist item). From `$SCRATCH/raw/pytest.txt`:

- Framework: `pytest` (config file `.pytest.toml` — pytest 9's TOML config
  format — sets `testpaths = ["tests"]`, `--import-mode=importlib`,
  `--cov`/`--cov-config=.coveragerc.ini`/`--cov-report=term-missing` in
  `addopts`, and `required_plugins = ["pytest-cov", "pytest-mock",
  "pytest-randomly", "pytest-xdist"]`).
- Summary line, verbatim: `57 passed, 34 subtests passed in 0.67s`.
- No failures, errors, skips, or xfails appear in the summary line — the
  line contains no `failed`, `error`, `skipped`, or `xfailed` segment.
- Coverage: `TOTAL 1210 85 348 44 90.56%`, "Required test coverage of 85.0%
  reached. Total coverage: 90.56%".
- Exit code: `0`.

**Directory structure and what each suite asserts** (module docstring or,
where absent, test/class names read directly):

| Directory | File | What it asserts |
| --- | --- | --- |
| `tests/ansi/` | `test_color_policy.py` | `NO_COLOR`/`FORCE_COLOR`/`TERM=dumb` color-policy behavior of `ansi.use_color` (test names: `test_no_color_disables_color`, `test_force_color_overrides_non_tty`, `test_term_dumb_disables`) |
| `tests/ansi/` | `test_text_snapshot.py` | Plain-ANSI text output stability and the rich-absent fallback path (test names: `test_plain_text_snapshot_is_stable`, `test_emit_falls_back_to_ansi_when_rich_is_absent`) |
| `tests/deletions/` | `test_config_loading.py` | A nonexistent `--config` path exits with code 4 (`test_missing_config_exits_four`) |
| `tests/deletions/` | `test_config_models.py` | Threshold/report dataclass validation bounds (test names: `test_max_lines_must_be_at_least_one`, `test_min_score_bounds`, `test_defaults_match_poc`) |
| `tests/deletions/` | `test_deleted_rules.py` | Module docstring, quoted: "Deleted-rule behavior: PY010 (comments), PY011 (docstring), PY020 (future-annotations) no longer exist anywhere in humansays, and ast/tokenize stay confined to humansays.analysis." (already quoted in full in §4) |
| `tests/deletions/` | `test_findings_models.py` | `RuleSpec` bounds validation on `confidence`/`weight`, and the `penalty` computed property (test names: `test_rulespec_rejects_confidence_above_one`, `test_rulespec_penalty_is_weight_times_confidence`) |
| `tests/golden/` | `test_parity.py` | Module docstring, quoted: "Transforms the raw pysignals 0.3.0 oracle (PY ids, three now-deleted rules) into the shape humansays should produce (HS ids, deleted rules dropped, score recomputed from the survivors) and asserts it against what humansays actually finds when it analyzes the same vendored corpus. This is the migration's acceptance criterion..." (test names: `test_every_group_has_a_frozen_oracle`, `test_humansays_matches_transformed_oracle_for_every_group`, `test_poc_group_grouped_json_smoke`) |
| `tests/golden/` | `test_self_scan.py` | Module docstring, quoted: "Self-scan gate: humansays scanning its own source. The gate is exact-match, not a ceiling: every weighted finding humansays reports against its own source must be listed in `self-scan-baseline.json` with a reason, and every baseline entry must still be reproduced. A finding that stops showing up means the baseline has gone stale and must be pruned, not silently carried forward." (test name: `test_self_scan_matches_baseline_exactly`) |
| `tests/parity/` | `test_signals.py` | Module docstring, quoted: "Tests for the structural signal scanner, including a scan of its own source." 12 `unittest.TestCase` classes, one per rule/behavior area: `StaticMethodRuleTests`, `LambdaRuleTests`, `LazyImportRuleTests`, `ModuleLengthRuleTests`, `FunctionSizeRuleTests`, `BaseClassRuleTests`, `BranchRuleTests`, `NestingRuleTests`, `ScoringTests`, `ConfigurationTests`, `InputResolutionTests` (largest test file, 323 lines) |
| `tests/` (top level) | `fixture_module.py` | Not a test file — no `test_` functions (0 matches). Module docstring, quoted: "Deliberately smelly fixture module. Every construct here exists to trip a specific rule. Do not clean it up." Support fixture, imported by other test files. |
| `tests/` (top level) | `poc_fixtures.py` | Not a test file — no `test_` functions (0 matches). Module docstring, quoted: "Source fixtures. Every snippet the tests analyze lives here, named for the rule it exercises..." Support fixture, imported by other test files. |

**Skipped/xfailed tests.**

```bash
$ grep -rn 'skip\|xfail\|skipif' tests/ --include='*.py'
tests/golden/poc-parity/corpus/poc/syntax.py:133:    skipped = docstring_span(node)
tests/golden/poc-parity/corpus/poc/syntax.py:138:        if text and not text.startswith("#") and number not in skipped: import number not in skipped
```

Both matches are the local variable name `skipped` inside the vendored POC
corpus source (`corpus/poc/syntax.py`, analysis target data, not a test),
not a `pytest.mark.skip`/`skipif`/`xfail` marker. None found in `tests/`
outside the vendored corpus. This absence claim is established by the grep
above, per the actual `grep` output shown, not asserted without a command.

---

## 12. Existing debt markers

From `$SCRATCH/raw/grep-todo.txt`
(`grep -rn 'TODO\|FIXME\|XXX\|HACK\|contract debt\|::NOTE::' src/ tests/ scripts/ .github/`):

```
src/humansays/analysis/rules.py:6:Known contract debt: this module still fuses ast-extraction (walking
src/humansays/analysis/rules.py:10:for this migration -- see the plan's "Known contract debt" section -- so it
.github/workflows/release.yml:75:  # ::NOTE::fix-later
.github/workflows/release.yml:107:    needs: [detect, package] # ::NOTE::publish-pypi
```

Four matching lines, all attributable to two markers:

| `file:line` | Marker type | Text (verbatim) |
| --- | --- | --- |
| `src/humansays/analysis/rules.py:6-10` | Contract-debt docstring | quoted in full below |
| `.github/workflows/release.yml:75` | `::NOTE::` comment | `# ::NOTE::fix-later` |
| `.github/workflows/release.yml:107` | `::NOTE::` inline comment | `needs: [detect, package] # ::NOTE::publish-pypi` |

**`src/humansays/analysis/rules.py:6-12`, contract-debt docstring, quoted in
full:**

```python
"""Known contract debt: this module still fuses ast-extraction (walking
the tree, reading raw node shape) with rule evaluation (thresholds,
scoring, message construction) in one file. Splitting those is a Phase 2
task; there is no dedicated `humansays.signals` package to move the
extraction half into yet, and the import-linter contract can't be written
for this migration -- see the plan's "Known contract debt" section -- so it
predates the refactor it would otherwise enforce.
"""
```

No `TODO`, `FIXME`, `XXX`, or `HACK` marker was found anywhere under `src/`,
`tests/`, `scripts/`, or `.github/` — the only hits from the grep pattern
above are the contract-debt docstring and the two `::NOTE::` comments listed
in the table.

---

## Stated exceptions

**The scope guard was not run against this PR's diff.** `01-review`'s allowlist
is review-shaped and postdates the migration commits, so running the guard
against `main..HEAD` would report violations for work that predates the
allowlist. No allowlist was widened to accommodate that history. Scope
enforcement applies from the review commits forward. Recorded per
`docs/phases/01-review/PHASE.md` §C.
