# Test-suite standardization implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan
> task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the test suite a single `conftest.py`, real fixtures, and three
scope-named directories whose markers are applied by a collection hook, so a
failure's blast radius is readable from its location.

**Architecture:** `tests/conftest.py` registers fixture modules through
`pytest_plugins` and assigns exactly one marker per test from its top-level
directory. Tests move into `unit/`, `integration/` and `tooling/` by what they
exercise. `tests/poc_fixtures.py` and `tests/fixture_module.py` are replaced by
`tests/fixtures/`, which supplies the paths and temporary files the tests
actually need and keeps source snippets as plain module constants.

**Tech Stack:** Python 3.11–3.14, pytest 9.1.1 (config in `.pytest.toml`,
`[pytest]` table), pytest-cov / pytest-mock / pytest-randomly / pytest-xdist,
`uv` for every invocation.

## Global Constraints

- **The operator owns git.** Ask before creating a branch and before each
  commit. Never `git add -A`, never `git commit -a`, never `git add .`. Commit
  with the pathspec form: `git commit -m '...' -- path/one path/two`.
- **`scripts/release_info.py` is staged for deletion and is not ours.** Run
  `git status --short` after every commit and confirm `D  scripts/release_info.py`
  is still there. If it disappears, stop.
- **Commit messages** are validated by `scripts/check_commit_msg.py` (a
  `commit-msg` pre-commit hook): `prefix(scope): summary`, prefix one of
  `feat|chore|ops|fix|release|docs`, summary starts lowercase, no trailing
  period. Use `chore(tests): ...`.
- **Bare `python` is not on PATH.** Every invocation is `uv run python`.
- **`--no-cov` is mandatory when running a subset.** `fail_under = 85` in
  `.coveragerc.ini` applies to whatever ran, so a partial run fails on coverage
  even when every test passes.
- **Run `bash scripts/format.sh` before `bash scripts/lint.sh`.** `format.sh` is
  the only quality script that writes to the repository.
- **Absolute imports only** inside `src/humansays`. `ban-relative-imports = "all"`
  in `.ruff.toml` makes TID252 the enforcer. Test files are not covered by that
  rule, but follow it anyway.
- **This branch touches no `src/` and no `docs/`.** If a step seems to require
  either, stop and report.
- **Every enforcement claim names its enforcer.** If you write that something is
  blocked or guaranteed, name the test, hook or CI job. Otherwise write it as
  convention.

**Branch:** `chore/standardize-testing`, already created from `origin/develop`
at `e255c0b`. Commit `f098546` (`chore(pytest): drop the blank-line separators
in .pytest.toml`) is already on it.

---

## Verified baseline — do not re-derive

Every fact below was measured on this branch on 2026-07-27. Re-measure only what
a step tells you to.

**Suite baseline:** `124 passed, 36 subtests passed in 0.73s`, total coverage
`92.63%`. Slowest single test is `0.06s`
(`tests/tooling/test_version_metadata.py::test_cli_version_flag_matches_installed_metadata`).
Command: `uv run pytest -q`.

**pytest discovery:** `rootdir: /home/rhawk/dev/humansays`, `configfile: .pytest.toml`.
`.pytest.toml` is auto-discovered; no `-c` flag is needed anywhere.

**`pytest_plugins` in `tests/conftest.py` is accepted.** Verified by probe on
this branch: a `tests/conftest.py` containing
`pytest_plugins = ["tests.fixtures.paths"]` loaded correctly and the fixture
resolved. `tests/conftest.py` counts as the initial conftest because `rootdir`
is the repository root. **This settles the question the old plan's step 10.1
existed to answer — do not re-probe it.**

**`tests/` works as an implicit namespace package.** With `pythonpath = ["."]`
and no `tests/__init__.py`, `pytest_plugins = ["tests.fixtures.paths"]` resolves
and `from tests.fixtures.sources import X` works under
`--import-mode=importlib`. Verified by probe.

**Three files import `poc_fixtures`, not one.** Dropping `pythonpath = ["tests"]`
without rewiring them produces
`ModuleNotFoundError: No module named 'poc_fixtures'` at collection in:
`tests/ansi/test_text_snapshot.py`, `tests/deletions/test_deleted_rules.py`,
`tests/parity/test_signals.py`. Verified by running the suite with
`pythonpath = ["."]`.

**`required_plugins` blocks isolated pytest runs.** From the repository root,
`uv run --isolated --no-project --with pytest pytest tests/smoke -q` fails with
`ERROR: Missing required plugins: pytest-cov, pytest-mock, pytest-randomly, pytest-xdist`.
It passes only with `-o required_plugins= -o addopts=`, which also discards
`strict`, `filterwarnings = ["error"]` and `--import-mode=importlib`. Verified by
probe. This is why Task 8 of the old plan is cut (see Decisions).

**`vulture` scans `tests/` too** — `[tool.vulture] paths = ["src", "tests"]`,
`min_confidence = 100`. Fixture functions have not been checked against it;
Task 7 verifies.

**Existing ruff exemptions for test material** (`.ruff.toml`, `[lint.per-file-ignores]`):

```toml
"tests/**/*.py" = ["ARG001", "ARG002", "INP001", "PLR2004", "S101", "PLC0415"]
"tests/fixture_module.py" = ["ANN001", "ANN201", "ANN205", "E731", "FBT002", "PLR0911", "RET505", "SIM116"]
"tests/parity/*.py" = ["PT009", "SIM115"]
```

The second and third blocks are deleted by this plan. The first stays.

**`scripts/ci.sh run_test`** currently runs `uv run python -m compileall -q src tests`
then `uv run python -m pytest`. **There is no `scripts/test.sh` and no `make test`.**

**Empty `__init__.py` in six directories:** `ansi`, `cli`, `deletions`, `golden`,
`parity`, `tooling`. All are 0 bytes. `tests/golden/poc-parity/corpus/poc/__init__.py`
is **not** one of them — it is vendored fixture source and must survive.

## Decisions taken with the operator

These were settled by direct question on 2026-07-27. Do not reopen them.

**The split is by scope, not by cost.** The whole suite runs in 0.73s, so there
is no slow loop to escape; the old plan's stated motivation was measured and
found false. The payoff is that a reader knows what a failure implicates.
Definitions, applied strictly:

- **`unit/`** — exercises one module's public surface in-process. Constructing
  inputs under `tmp_path` is still unit.
- **`integration/`** — drives `humansays.cli.main` or `humansays.application`,
  spawns a subprocess, or asserts over the real `src/humansays` tree.
- **`tooling/`** — verifies the repository's own scripts, packaging and
  documentation rather than the analyzer.

**The clone-at-commit fixture is cut entirely.** No test in the suite consumes a
cloned repository; it was the riskiest step and would have added the project's
first network dependency to serve nothing. The vendored `poc-parity` corpus
already covers real-world source, offline and sha256-pinned. The `network`
marker is removed with it.

**`tooling/` survives as a third bucket.** `test_planned_catalog.py`,
`test_commit_msg.py` and `test_version_metadata.py` verify docs and scripts,
contribute zero analyzer coverage, and are misfiled under either of the other
two names.

**The parity corpus stays exactly as it is.** Pinned by sha256, offline by
design, and its oracle cannot be regenerated without an untainted pysignals
0.3.0 install. `tests/golden/` is not reorganized; it is mapped to the
`integration` marker in place.

## Decisions taken during planning

**Task 8 of the old plan — porting `scripts/smoke_test_package.py` to
`tests/smoke/` — is cut.** Evidence above: it only runs under
`-o required_plugins= -o addopts=`, at which point the smoke run stops sharing
the configuration it exists to share, and a future edit to `.pytest.toml` would
silently not reach it. The script works today and is correctly isolated. Leave
`scripts/smoke_test_package.py` and `scripts/smoke-package.sh` untouched.
`test_poc_group_grouped_json_smoke` stays in `tests/golden/test_parity.py`,
which is already mapped to `integration`.

**Source snippets stay module constants; they do not become fixtures.** The old
plan's step 10.4 would have wrapped fourteen string constants in
`@pytest.fixture`. That is indirection with no payoff — the strings are not
expensive, not stateful, and not parameterized. Fixtures are introduced only
where there is a reason: filesystem paths, temporary files, and environment
variables.

**`tests/fixture_module.py` is deleted, and the one test that guards it goes
with it.** `FixtureScanTests.test_disk_fixture_matches_the_fixture_module`
asserts that the committed duplicate matches `SMELLY_MODULE`. Deleting the
duplicate removes the thing that test guards, so it has no subject. This is the
only test this plan deletes. Every other test is moved or converted, never
dropped.

## Two `__file__` walks survive on purpose

The research input listed four hand-rolled repository-root computations and
proposed replacing all of them. This plan replaces two and leaves two, because
leaving them costs nothing and moving their files would cost a regeneration:

- `tests/tooling/test_planned_catalog.py` resolves `parents[2]` to reach
  `docs/site/planned/`, which is correct only at its current depth. **This plan
  does not move it** — `tooling/` keeps its files and only gains a marker — so
  the constant stays valid and needs no edit. The research input flagged this as
  an open risk; not moving the file is what closes it.
- `tests/golden/test_parity.py:25` does the same. `tests/golden/` is untouched
  for the reasons in the Decisions section.

The two that go are `test_signals.py:21-23` (replaced by the `src_root` and
`baseline_path` fixtures in Task 4) and `poc_fixtures.py:11` (deleted with the
file in Task 6).

## Not investigated

- Whether `tests/golden/self-scan-baseline.json` needs regenerating. It should
  not: `tests/golden/` does not move, and Task 5 replaces
  `test_signals.py`'s hand-rolled path with a fixture pointing at the same file.
  Task 5 verifies by running the test.
- Whether `vulture` flags the new fixture functions. Task 7 runs it.
- Whether `pytest-xdist` (`-n auto`) still passes after the move. Nothing in
  this plan adds shared state, but no step exercises xdist.

---

## File structure

```
tests/
  conftest.py                        NEW  pytest_plugins + the marker hook
  fixtures/
    __init__.py                      NEW  empty
    paths.py                         NEW  repo_root, src_root, baseline_path fixtures
    sources.py                       NEW  snippet constants + factories (from poc_fixtures.py)
    environment.py                   NEW  no_color, forced_color, dumb_terminal fixtures
    modules.py                       NEW  smelly_module_path, config_toml_path fixtures
  unit/                              NEW  marker: unit
    test_color_policy.py             from tests/ansi/test_color_policy.py
    test_text_snapshot.py            from tests/ansi/test_text_snapshot.py
    test_config_models.py            from tests/deletions/test_config_models.py
    test_findings_models.py          from tests/deletions/test_findings_models.py
    test_config_decoding.py          from tests/tooling/test_config_decoding.py
    test_deleted_rules.py            from tests/deletions/test_deleted_rules.py (4 of 5 tests)
    test_rules.py                    from tests/parity/test_signals.py (rule classes)
  integration/                       NEW  marker: integration
    test_exit_contract.py            from tests/cli/test_exit_contract.py
    test_config_loading.py           from tests/deletions/test_config_loading.py
    test_analysis_confinement.py     from tests/deletions/test_deleted_rules.py (1 of 5 tests)
    test_cli_contract.py             from tests/parity/test_signals.py (CLI + self-scan classes)
  tooling/                           marker: tooling; files unchanged, __init__.py deleted
    test_commit_msg.py
    test_planned_catalog.py
    test_version_metadata.py
  golden/                            marker: integration; UNTOUCHED except __init__.py
    poc-parity/                      never touched
    self-scan-baseline.json
    test_parity.py
    test_self_scan.py

DELETED: tests/poc_fixtures.py, tests/fixture_module.py,
         tests/ansi/, tests/cli/, tests/deletions/, tests/parity/,
         and the six empty __init__.py files.
```

---

### Task 1: conftest, marker hook, and the fixtures package

**Files:**

- Create: `tests/conftest.py`
- Create: `tests/fixtures/__init__.py`
- Create: `tests/fixtures/paths.py`
- Modify: `.pytest.toml` (markers list)

**Interfaces:**

- Produces: fixtures `repo_root: Path`, `src_root: Path`, `baseline_path: Path`,
  all session-scoped. Produces the `pytest_collection_modifyitems` hook that
  adds exactly one of `unit` / `integration` / `tooling` to every collected
  test and raises `pytest.UsageError` for a test in an unmapped directory.

- [ ] **Step 1: Create the fixtures package**

`tests/fixtures/__init__.py` — empty file, zero bytes.

`tests/fixtures/paths.py`:

```python
"""Filesystem anchors, resolved once instead of by hand in each test module."""

from __future__ import annotations

from pathlib import Path

import pytest

_TESTS_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope='session')
def repo_root() -> Path:
    """The repository checkout root."""
    return _TESTS_ROOT.parent


@pytest.fixture(scope='session')
def src_root() -> Path:
    """The installed package's source directory, `src/humansays`."""
    return _TESTS_ROOT.parent / 'src' / 'humansays'


@pytest.fixture(scope='session')
def baseline_path() -> Path:
    """The frozen self-scan baseline the golden tests assert against."""
    return _TESTS_ROOT / 'golden' / 'self-scan-baseline.json'
```

`_TESTS_ROOT` is computed once at module import, so the depth-sensitive
`Path(__file__)` walk exists in exactly one place. Every consumer asks for a
fixture instead.

- [ ] **Step 2: Create `tests/conftest.py`**

```python
"""Suite-wide configuration.

Every test carries exactly one scope marker, applied from its top-level
directory rather than by decorator, so a test cannot be filed in a directory
and silently miss its marker.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest_plugins = [
    'tests.fixtures.paths',
]

_TESTS_ROOT = Path(__file__).resolve().parent

_MARKER_BY_DIRECTORY = {
    'unit': 'unit',
    'integration': 'integration',
    'tooling': 'tooling',
    'golden': 'integration',
}


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Mark every collected test according to the directory holding it."""
    del config
    for item in items:
        relative = Path(item.path).resolve().relative_to(_TESTS_ROOT)
        directory = relative.parts[0]
        marker = _MARKER_BY_DIRECTORY.get(directory)
        if marker is None:
            raise pytest.UsageError(
                f'{relative} is not under a directory with a scope marker; '
                f'expected one of {sorted(_MARKER_BY_DIRECTORY)}'
            )
        item.add_marker(marker)
```

The `UsageError` is the enforcer for "every test carries exactly one marker".
Name it as such wherever that claim is made.

- [ ] **Step 3: Put the repository root on `pythonpath` alongside `tests`**

In `.pytest.toml`, change:

```toml
pythonpath = ["tests"]
```

to:

```toml
pythonpath = [".", "tests"]
```

Both entries are needed **during the transition and only during it**. `.` is
what makes `tests.fixtures.paths` importable from this task onward; `tests` is
what keeps the three files still doing `import poc_fixtures` working until
Task 6 rewires them. Task 6 drops `"tests"`, leaving `pythonpath = ["."]`.

Verified 2026-07-27: `pythonpath = ["."]` resolves `tests.fixtures.*` as an
implicit namespace package with **no** `tests/__init__.py`, under
`--import-mode=importlib`. Do not add one.

- [ ] **Step 4: Replace the marker list in `.pytest.toml`**

Replace the existing `markers = [...]` block with:

```toml
markers = [
    "unit: exercises one module's public surface in-process",
    "integration: drives the CLI, the application, or the real source tree",
    "tooling: verifies the repository's own scripts, packaging and documentation",
]
```

`slow` and `network` are removed. Neither was ever applied, and `network`'s only
planned consumer was cut.

- [ ] **Step 5: Run the suite and confirm the hook rejects the current layout**

Run: `uv run pytest -q --no-cov`

Expected: a `UsageError` naming `ansi/test_color_policy.py` (or whichever file
`pytest-randomly` orders first) as not being under a marked directory. **This
failure is the goal of this step** — it proves the hook fires before any test
runs. Tasks 2 and 3 clear it by moving the files.

- [ ] **Step 6: Confirm the fixtures load in isolation**

Create a throwaway `tests/unit/test_probe.py`:

```python
from pathlib import Path


def test_repo_root_holds_pyproject(repo_root: Path) -> None:
    assert (repo_root / 'pyproject.toml').is_file()


def test_src_root_holds_the_package(src_root: Path) -> None:
    assert (src_root / '__init__.py').is_file()
```

Run: `uv run pytest tests/unit -q --no-cov`

Expected: `2 passed`. If it errors with `ModuleNotFoundError: No module named
'tests'`, Step 3 was skipped — `.` must be on `pythonpath` for
`tests.fixtures.paths` to resolve. If it errors with
`Defining 'pytest_plugins' in a non-top-level conftest is no longer supported`,
stop and report: that contradicts the probe recorded in the baseline section and
means something about `rootdir` resolution has changed.

Then delete `tests/unit/test_probe.py`. It is scaffolding for this step only and
must not reach a commit.

- [ ] **Step 7: Commit**

```bash
git add tests/conftest.py tests/fixtures/__init__.py tests/fixtures/paths.py
git commit -m 'chore(tests): add a conftest that marks tests by directory' -- \
  tests/conftest.py tests/fixtures/__init__.py tests/fixtures/paths.py .pytest.toml
git status --short
```

Confirm `D  scripts/release_info.py` is still listed. The suite does not pass at
this commit; that is expected and is stated in the message body if you add one.

---

### Task 2: move the unit tests

**Files:**

- Create: `tests/fixtures/sources.py`
- Move: `tests/ansi/test_color_policy.py` → `tests/unit/test_color_policy.py`
- Move: `tests/ansi/test_text_snapshot.py` → `tests/unit/test_text_snapshot.py`
- Move: `tests/deletions/test_config_models.py` → `tests/unit/test_config_models.py`
- Move: `tests/deletions/test_findings_models.py` → `tests/unit/test_findings_models.py`
- Move: `tests/tooling/test_config_decoding.py` → `tests/unit/test_config_decoding.py`
- Move: `tests/deletions/test_deleted_rules.py` → `tests/unit/test_deleted_rules.py` (4 of 5 tests)
- Create: `tests/integration/test_analysis_confinement.py` (the 5th test)

**Interfaces:**

- Consumes: `src_root` from `tests.fixtures.paths` (Task 1).
- Produces: `tests/fixtures/sources.py` exporting the snippet constants
  `STATIC_METHOD`, `CLASSMETHOD_AND_FUNCTION`, `LAMBDAS_IN_THREE_SCOPES`,
  `NAMED_FUNCTION`, `MULTIPLE_INHERITANCE`, `SINGLE_INHERITANCE`,
  `FUTURE_ANNOTATIONS`, `FUTURE_OTHER_FEATURE`, `LAZY_IMPORT`,
  `MODULE_LEVEL_IMPORT`, `NESTED_LOOPS`, `NESTED_LOOPS_IN_METHOD`,
  `NESTED_LOOPS_IN_METHOD_DEEPER`, `SMELLY_MODULE`, `CONFIG_TOML`, and the
  factories `branch_chain(count: int) -> str`, `line_padding(count: int) -> str`,
  `padded_function(statements: int, blanks: int) -> str`.

- [ ] **Step 1: Create `tests/fixtures/sources.py`**

Copy `tests/poc_fixtures.py` verbatim into `tests/fixtures/sources.py`, then
make exactly two changes:

1. Delete the `from pathlib import Path` import and the `FIXTURE_MODULE_PATH`
   constant (lines 9 and 11). That path is replaced by the `smelly_module_path`
   fixture in Task 4.
2. Replace the module docstring with:

```python
"""Source snippets the analyzer tests run against.

Each is named for the rule it exercises, so a test reads as "analyze this
snippet, expect this signal". These stay plain module constants rather than
fixtures: they are immutable strings with no setup cost and no per-test state.
"""
```

Everything else — all fourteen remaining constants and all three factory
functions — is copied byte-for-byte.

- [ ] **Step 2: Move the four files that need no source-fixture rewiring**

```bash
mkdir -p tests/unit
git mv tests/ansi/test_color_policy.py tests/unit/test_color_policy.py
git mv tests/deletions/test_config_models.py tests/unit/test_config_models.py
git mv tests/deletions/test_findings_models.py tests/unit/test_findings_models.py
git mv tests/tooling/test_config_decoding.py tests/unit/test_config_decoding.py
```

No content edits. None of these four imports `poc_fixtures`, and none contains a
`Path(__file__)` walk.

- [ ] **Step 3: Move and rewire `test_text_snapshot.py`**

```bash
git mv tests/ansi/test_text_snapshot.py tests/unit/test_text_snapshot.py
```

Then change its import line (currently line 4):

```python
import poc_fixtures as fixtures
```

to:

```python
from tests.fixtures import sources
```

and change the one use site, `fixtures.MULTIPLE_INHERITANCE` (line 24), to
`sources.MULTIPLE_INHERITANCE`. Nothing else in the file changes; the three
`monkeypatch.setenv('NO_COLOR', '1')` calls are replaced in Task 5, not here.

- [ ] **Step 4: Split `test_deleted_rules.py`**

```bash
git mv tests/deletions/test_deleted_rules.py tests/unit/test_deleted_rules.py
```

In `tests/unit/test_deleted_rules.py`:

- Change `import poc_fixtures as fixtures` to `from tests.fixtures import sources`,
  and change `fixtures.FUTURE_ANNOTATIONS` → `sources.FUTURE_ANNOTATIONS` and
  `fixtures.FUTURE_OTHER_FEATURE` → `sources.FUTURE_OTHER_FEATURE`.
- Delete the `SRC_ROOT = Path(__file__).resolve().parent.parent.parent / 'src' / 'humansays'`
  constant (line 17) and the `from pathlib import Path` import, which becomes
  unused.
- Delete the whole `test_ast_and_tokenize_are_confined_to_analysis` function.

The four tests that remain are
`test_deleted_ids_are_absent_from_signal_name`,
`test_deleted_ids_are_absent_from_catalog`,
`test_future_annotations_import_yields_no_finding`, and
`test_other_future_features_still_yield_no_finding`.

Then create `tests/integration/test_analysis_confinement.py` holding the deleted
test, rewritten to take the `src_root` fixture instead of walking `__file__`:

```python
"""The `ast` and `tokenize` ban is a package-layout constraint, so it is
asserted against the real source tree rather than a snippet."""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

_CONFINED_MODULES = frozenset({'ast', 'tokenize'})
_ALLOWED_PACKAGE = 'analysis'


def _imported_modules(source: str) -> set[str]:
    tree = ast.parse(source)
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split('.')[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split('.')[0])
    return modules


def test_ast_and_tokenize_are_confined_to_analysis(src_root: Path) -> None:
    offenders = []
    for path in sorted(src_root.rglob('*.py')):
        if _ALLOWED_PACKAGE in path.relative_to(src_root).parts:
            continue
        confined = _CONFINED_MODULES & _imported_modules(
            path.read_text(encoding='utf-8')
        )
        if confined:
            offenders.append((str(path.relative_to(src_root)), sorted(confined)))

    assert offenders == []
```

**Before writing this, open the original `test_ast_and_tokenize_are_confined_to_analysis`
in git history** (`git show HEAD:tests/deletions/test_deleted_rules.py`) and make
the new version assert the same thing the old one did. If the original used a
different confinement rule — for example checking `humansays.analysis` by module
path rather than by directory part — match the original exactly and adjust the
code above. Do not widen or narrow the assertion. `lint-imports` is the primary
enforcer of this constraint (`.importlinter.ini`); this test is the second one.

- [ ] **Step 5: Run the unit tests**

Run: `uv run pytest tests/unit tests/integration -q --no-cov`

Expected: all tests in those two directories pass and every one is marked. The
rest of the suite still fails the `UsageError` from Task 1 — that is expected
until Task 3.

To check just these directories without the unmoved files tripping the hook, run
them by path as shown. Do not run bare `uv run pytest` yet.

- [ ] **Step 6: Commit**

```bash
git add tests/fixtures/sources.py tests/unit tests/integration
git commit -m 'chore(tests): move the unit tests into tests/unit' -- \
  tests/fixtures/sources.py tests/unit tests/integration \
  tests/ansi tests/deletions tests/tooling
git status --short
```

Confirm `D  scripts/release_info.py` survives.

---

### Task 3: move the integration tests and clear the hook

**Files:**

- Move: `tests/cli/test_exit_contract.py` → `tests/integration/test_exit_contract.py`
- Move: `tests/deletions/test_config_loading.py` → `tests/integration/test_config_loading.py`
- Delete: the six empty `__init__.py` files
- Delete: `tests/ansi/`, `tests/cli/`, `tests/deletions/` (now empty)

**Interfaces:**

- Consumes: nothing new.
- Produces: a `tests/` tree where every directory holding tests is in
  `_MARKER_BY_DIRECTORY`, except `tests/parity/`, which Task 4 empties.

- [ ] **Step 1: Move the two remaining integration files**

```bash
git mv tests/cli/test_exit_contract.py tests/integration/test_exit_contract.py
git mv tests/deletions/test_config_loading.py tests/integration/test_config_loading.py
```

No content edits in this step. `test_exit_contract.py` imports nothing from
`poc_fixtures` and contains no `Path(__file__)` walk; its
`monkeypatch.setattr` is replaced in Task 5.

- [ ] **Step 2: Delete the six empty `__init__.py` files**

```bash
git rm tests/ansi/__init__.py tests/cli/__init__.py tests/deletions/__init__.py \
       tests/golden/__init__.py tests/parity/__init__.py tests/tooling/__init__.py
```

They are all zero bytes and unnecessary under `--import-mode=importlib`.
**Do not touch `tests/golden/poc-parity/corpus/poc/__init__.py`** — it is
vendored fixture source that the parity oracle analyzes.

- [ ] **Step 3: Remove the emptied directories**

```bash
rmdir tests/ansi tests/cli tests/deletions
```

`rmdir` rather than `rm -rf`: it refuses if anything is left, which is the check
you want. If it refuses, something was missed — list the directory and report
rather than forcing it.

- [ ] **Step 4: Confirm collection**

Run: `uv run pytest --collect-only -q 2>&1 | tail -5`

Expected: the `UsageError` now names only `parity/test_signals.py`. Every other
file is under a mapped directory. If it names anything else, a file was missed.

- [ ] **Step 5: Commit**

```bash
git commit -m 'chore(tests): move the cli tests into tests/integration' -- \
  tests/integration tests/cli tests/deletions tests/ansi tests/golden tests/parity tests/tooling
git status --short
```

---

### Task 4: convert `test_signals.py` off unittest and split it

**Files:**

- Create: `tests/unit/test_rules.py`
- Create: `tests/integration/test_cli_contract.py`
- Create: `tests/fixtures/modules.py`
- Delete: `tests/parity/test_signals.py`, `tests/parity/`
- Modify: `.ruff.toml` (drop the `tests/parity/*.py` ignore block)

**Interfaces:**

- Consumes: `sources` constants and factories (Task 2), `src_root` and
  `baseline_path` (Task 1).
- Produces: fixtures `smelly_module_path: Path` and `config_toml_path: Path`
  from `tests.fixtures.modules`, both function-scoped and both writing into
  `tmp_path`.

**Read this before starting the task.** The two code blocks below give the
target structure — class names, split, fixture use, helper placement — and were
written from a reading of `tests/parity/test_signals.py`. They are not a
transcription. **Keep the original open in a second buffer**
(`git show HEAD:tests/parity/test_signals.py`) and port each test body across
individually, preserving its assertion exactly. Where an assertion below
disagrees with the original, **the original wins** — this is a conversion of
scaffolding, not a rewrite of what is asserted. Two specific things to carry
over verbatim rather than trusting the blocks below: the `BANNED_SIGNALS` and
`NOTICE_SIGNALS` constants at the top of the original, and the exact expected
substrings in the `observation.message` assertions. A converted test that
passes while asserting something weaker than the original is the failure mode
this warning exists to prevent.

- [ ] **Step 1: Create `tests/fixtures/modules.py`**

```python
"""Fixture material that has to exist as a real file on disk.

The CLI accepts paths, not strings, so the snippets it scans have to be
written somewhere. Writing them into `tmp_path` per test replaces the
committed duplicate that used to live at `tests/fixture_module.py`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.fixtures import sources

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def smelly_module_path(tmp_path: Path) -> Path:
    """`sources.SMELLY_MODULE` written to disk so the CLI can be pointed at it."""
    path = tmp_path / 'smelly_module.py'
    path.write_text(sources.SMELLY_MODULE, encoding='utf-8')
    return path


@pytest.fixture
def config_toml_path(tmp_path: Path) -> Path:
    """`sources.CONFIG_TOML` written to disk for `--config` to load."""
    path = tmp_path / 'humansays.toml'
    path.write_text(sources.CONFIG_TOML, encoding='utf-8')
    return path
```

Register it by adding `'tests.fixtures.modules'` to the `pytest_plugins` list in
`tests/conftest.py`:

```python
pytest_plugins = [
    'tests.fixtures.paths',
    'tests.fixtures.modules',
]
```

- [ ] **Step 2: Write `tests/unit/test_rules.py`**

The rule classes convert mechanically: drop `(unittest.TestCase)`, turn
`self.assertEqual(a, b)` into `assert a == b`, `self.assertIs(a, b)` into
`assert a is b`, `self.assertIn(a, b)` into `assert a in b`,
`self.assertNotIn(a, b)` into `assert a not in b`, `self.assertTrue(x)` into
`assert x`, and `self.assertLessEqual(a, b)` into `assert a <= b`. Add
`-> None` return annotations, which the originals already carry.

```python
"""Per-rule detection tests: one class per rule, positive case then negative."""

from __future__ import annotations

import ast
from pathlib import Path

from humansays.analysis.models import ParsedModule
from humansays.analysis.rules import RulesetEvaluator
from humansays.config.models import Thresholds
from humansays.enums import Severity, SignalName
from humansays.findings.models import Finding
from tests.fixtures import sources


def analyze(source: str, thresholds: Thresholds | None = None) -> list[Finding]:
    module = ParsedModule(Path('<snippet>'), source, ast.parse(source))
    return RulesetEvaluator(module, thresholds or Thresholds()).run()


def signals(findings: list[Finding]) -> list[SignalName]:
    return [finding.rule.signal for finding in findings]


def findings_for(findings: list[Finding], signal: SignalName) -> list[Finding]:
    return [finding for finding in findings if finding.rule.signal is signal]


class TestStaticMethodRule:
    def test_staticmethod_is_reported(self) -> None:
        found = findings_for(analyze(sources.STATIC_METHOD), SignalName.HS015)
        assert len(found) == 1
        assert found[0].location.symbol == 'Router.classify'
        assert found[0].rule.severity is Severity.WARNING

    def test_classmethod_and_module_function_are_not_reported(self) -> None:
        found = analyze(sources.CLASSMETHOD_AND_FUNCTION)
        assert SignalName.HS015 not in signals(found)


class TestLambdaRule:
    def test_lambda_is_reported_in_every_scope(self) -> None:
        found = findings_for(analyze(sources.LAMBDAS_IN_THREE_SCOPES), SignalName.HS016)
        symbols = sorted(finding.location.symbol for finding in found)
        assert symbols == ['<module>', 'Holder.pick', 'sort_items']

    def test_named_function_is_not_reported(self) -> None:
        assert SignalName.HS016 not in signals(analyze(sources.NAMED_FUNCTION))


class TestLazyImportRule:
    def test_imports_inside_a_function_are_reported(self) -> None:
        found = findings_for(analyze(sources.LAZY_IMPORT), SignalName.HS021)
        assert len(found) == 2
        assert all(item.location.symbol == 'render' for item in found)

    def test_module_level_imports_are_not_reported(self) -> None:
        found = analyze(sources.MODULE_LEVEL_IMPORT)
        assert SignalName.HS021 not in signals(found)


class TestModuleLengthRule:
    def test_long_file_is_reported(self) -> None:
        found = findings_for(analyze(sources.line_padding(600)), SignalName.HS017)
        assert len(found) == 1
        assert '600 source lines' in found[0].observation.message

    def test_file_at_threshold_is_not_reported(self) -> None:
        found = analyze(sources.line_padding(500))
        assert SignalName.HS017 not in signals(found)


class TestFunctionSizeRule:
    def test_blank_lines_count_toward_span_but_not_code(self) -> None:
        found = signals(analyze(sources.padded_function(30, 30)))
        assert SignalName.HS009 in found
        assert SignalName.HS022 not in found

    def test_dense_function_trips_the_code_line_rule(self) -> None:
        found = findings_for(analyze(sources.padded_function(70, 0)), SignalName.HS022)
        assert len(found) == 1
        assert '72 lines of code' in found[0].observation.message


class TestBaseClassRule:
    def test_multiple_inheritance_is_reported(self) -> None:
        found = findings_for(analyze(sources.MULTIPLE_INHERITANCE), SignalName.HS018)
        assert len(found) == 1
        assert found[0].observation.evidence == ('Reader', 'Writer')

    def test_single_inheritance_is_not_reported(self) -> None:
        found = analyze(sources.SINGLE_INHERITANCE)
        assert SignalName.HS018 not in signals(found)


class TestBranchRule:
    def test_branch_count_includes_elif(self) -> None:
        found = findings_for(analyze(sources.branch_chain(6)), SignalName.HS019)
        assert len(found) == 1
        assert '6 if/elif statements' in found[0].observation.message

    def test_branches_at_threshold_are_not_reported(self) -> None:
        found = analyze(sources.branch_chain(5))
        assert SignalName.HS019 not in signals(found)


class TestNestingRule:
    def test_module_function_uses_base_limit(self) -> None:
        found = findings_for(analyze(sources.NESTED_LOOPS), SignalName.HS003)
        assert len(found) == 1

    def test_method_receives_the_class_bonus(self) -> None:
        found = analyze(sources.NESTED_LOOPS_IN_METHOD)
        assert SignalName.HS003 not in signals(found)

    def test_method_one_level_deeper_still_fires(self) -> None:
        found = analyze(sources.NESTED_LOOPS_IN_METHOD_DEEPER)
        assert SignalName.HS003 in signals(found)


class TestScoringWeights:
    def test_documentation_notices_do_not_cost_points(self) -> None:
        findings = analyze(sources.NAMED_FUNCTION)
        assert all(finding.rule.weight == 0.0 for finding in findings)


class TestSmellyFixture:
    def test_fixture_reports_every_new_rule(self) -> None:
        reported = set(signals(analyze(sources.SMELLY_MODULE)))
        expected = {
            SignalName.HS015,
            SignalName.HS016,
            SignalName.HS018,
            SignalName.HS019,
            SignalName.HS021,
        }
        assert expected <= reported
```

`test_documentation_notices_do_not_cost_points` came from `ScoringTests`, whose
other three tests drive the CLI and go to `integration/` in the next step.
`test_fixture_reports_every_new_rule` came from `FixtureScanTests`; its sibling
`test_disk_fixture_matches_the_fixture_module` is deleted, per the Decisions
section.

- [ ] **Step 3: Write `tests/integration/test_cli_contract.py`**

```python
"""End-to-end CLI behavior: scoring, configuration, input resolution, self-scan."""

from __future__ import annotations

import ast
import contextlib
import io
import json
from pathlib import Path

from humansays.analysis.models import ParsedModule
from humansays.analysis.rules import RulesetEvaluator
from humansays.cli import main
from humansays.config.models import Thresholds
from humansays.enums import Grade, SignalName
from humansays.findings.models import Finding

BANNED_SIGNALS = frozenset({SignalName.HS015, SignalName.HS016})
NOTICE_SIGNALS: frozenset[SignalName] = frozenset()


def analyze(source: str, thresholds: Thresholds | None = None) -> list[Finding]:
    module = ParsedModule(Path('<snippet>'), source, ast.parse(source))
    return RulesetEvaluator(module, thresholds or Thresholds()).run()


def signals(findings: list[Finding]) -> list[SignalName]:
    return [finding.rule.signal for finding in findings]


def run_cli(argv: list[str], piped: str = '') -> tuple[int, str]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(io.StringIO()):
        code = main(argv, io.StringIO(piped))
    return code, buffer.getvalue()


def rule_ids(payload: dict) -> set[str]:
    return {
        signal['rule_id']
        for target in payload['targets']
        for signal in target['signals']
    }


class TestScoring:
    def test_clean_source_scores_an_a(self, src_root: Path) -> None:
        _, output = run_cli([str(src_root), '--format', 'json'])
        assert json.loads(output)['score']['grade'] == Grade.A

    def test_smelly_source_scores_badly(self, smelly_module_path: Path) -> None:
        _, output = run_cli(['--format', 'json'], str(smelly_module_path))
        score = json.loads(output)['score']
        assert score['value'] < 60.0
        assert score['penalty'] > 0.0

    def test_min_score_gates_the_exit_code(self, smelly_module_path: Path) -> None:
        code, _ = run_cli(['--min-score', '90'], str(smelly_module_path))
        assert code == 1


class TestConfiguration:
    def test_toml_thresholds_are_applied(
        self,
        config_toml_path: Path,
        smelly_module_path: Path,
    ) -> None:
        code, output = run_cli(
            ['--config', str(config_toml_path), '--format', 'json', '--min-score', '0'],
            str(smelly_module_path),
        )
        assert code == 0
        assert 'HS017' in rule_ids(json.loads(output))

    def test_command_line_overrides_the_file(
        self,
        config_toml_path: Path,
        smelly_module_path: Path,
    ) -> None:
        code, output = run_cli(
            [
                '--config',
                str(config_toml_path),
                '--format',
                'json',
                '--max-file-lines',
                '5000',
                '--min-score',
                '0',
            ],
            str(smelly_module_path),
        )
        assert code == 0
        assert 'HS017' not in rule_ids(json.loads(output))

    def test_file_min_score_can_fail_the_run(
        self,
        config_toml_path: Path,
        smelly_module_path: Path,
    ) -> None:
        code, _ = run_cli(['--config', str(config_toml_path)], str(smelly_module_path))
        assert code == 1


class TestInputResolution:
    def test_paths_can_be_piped_on_stdin(self, smelly_module_path: Path) -> None:
        code, output = run_cli(['--format', 'json'], f'{smelly_module_path}\n')
        payload = json.loads(output)
        assert code == 0
        assert payload['summary']['files'] == 1
        assert payload['root'] == '<stdin>'

    def test_nul_separated_paths_are_accepted(self, smelly_module_path: Path) -> None:
        code, output = run_cli(['-', '--format', 'json'], f'{smelly_module_path}\0')
        assert code == 0
        assert json.loads(output)['summary']['files'] == 1

    def test_fail_on_warning_sets_exit_code(self, smelly_module_path: Path) -> None:
        code, _ = run_cli(['-', '--fail-on', 'warning'], f'{smelly_module_path}\n')
        assert code == 1

    def test_fail_on_never_is_the_default(self, smelly_module_path: Path) -> None:
        code, _ = run_cli(['-'], f'{smelly_module_path}\n')
        assert code == 0

    def test_missing_paths_exit_three(self) -> None:
        code, _ = run_cli(['-'], '/nonexistent/path.py\n')
        assert code == 3

    def test_unknown_symbol_exits_two(self, smelly_module_path: Path) -> None:
        code, _ = run_cli(['-', '--symbol', 'nope'], f'{smelly_module_path}\n')
        assert code == 2

    def test_symbol_filter_narrows_targets(self, smelly_module_path: Path) -> None:
        code, output = run_cli(
            ['-', '--symbol', 'dispatch', '--format', 'json'],
            f'{smelly_module_path}\n',
        )
        symbols = {target['symbol'] for target in json.loads(output)['targets']}
        assert code == 0
        assert symbols
        assert all('dispatch' in symbol for symbol in symbols)


class TestSelfScan:
    @staticmethod
    def package_findings(src_root: Path) -> dict[str, list[Finding]]:
        return {
            path.name: analyze(path.read_text(encoding='utf-8'))
            for path in sorted(src_root.rglob('*.py'))
        }

    def test_no_banned_constructs_in_own_source(self, src_root: Path) -> None:
        offenders = {
            name: sorted(BANNED_SIGNALS.intersection(signals(findings)))
            for name, findings in self.package_findings(src_root).items()
            if BANNED_SIGNALS.intersection(signals(findings))
        }
        assert offenders == {}

    def test_no_module_exceeds_the_file_threshold(self, src_root: Path) -> None:
        offenders = [
            name
            for name, findings in self.package_findings(src_root).items()
            if SignalName.HS017 in signals(findings)
        ]
        assert offenders == []

    def test_only_notices_and_baselined_signals_remain(
        self,
        src_root: Path,
        baseline_path: Path,
    ) -> None:
        entries = json.loads(baseline_path.read_text(encoding='utf-8'))['entries']
        allowed = NOTICE_SIGNALS | frozenset(
            SignalName[entry['rule_id']] for entry in entries
        )
        remaining = {
            signal
            for findings in self.package_findings(src_root).values()
            for signal in signals(findings)
        }
        assert remaining <= allowed

    def test_json_report_is_serializable(self, src_root: Path) -> None:
        code, output = run_cli([str(src_root), '--format', 'json'])
        payload = json.loads(output)
        assert code == 0
        assert payload['summary']['files'] >= 10
        assert payload['errors'] == []
```

Two behavior notes to carry into the commit message:

- The original `SelfScanTests` used `self.subTest(module=name)` to report every
  failing module. Plain pytest has no `subTest`, so the two loop-based tests
  collect offenders into a container and assert the container is empty, which
  reports the same information on failure. **This is why the subtest count drops
  from 36 to 0** — account for it in the Task 7 baseline comparison rather than
  treating it as lost coverage.
- `ConfigurationTests.setUp` used `tempfile.NamedTemporaryFile(delete=False)`
  plus `addCleanup`. The `config_toml_path` fixture replaces it, which is what
  lets the `SIM115` ruff ignore go.

- [ ] **Step 4: Delete the old file and its ruff exemption**

```bash
git rm tests/parity/test_signals.py
rmdir tests/parity
```

In `.ruff.toml`, delete these three lines from `[lint.per-file-ignores]`:

```toml
# Ported verbatim from the POC's unittest.TestCase suite; assertions are kept
# as unittest-style (not rewritten to plain assert) per the migration plan.
"tests/parity/*.py" = ["PT009", "SIM115"]
```

- [ ] **Step 5: Run the full suite**

Run: `uv run pytest -q`

Expected: no `UsageError`, every test marked, coverage at or above the 92.63%
baseline. Test count should be `124 - 1 = 123` (the deleted
`test_disk_fixture_matches_the_fixture_module`), with 0 subtests.

If `test_only_notices_and_baselined_signals_remain` fails, the baseline path is
wrong — check that `baseline_path` resolves to
`tests/golden/self-scan-baseline.json` and that the file exists. Do **not**
regenerate the baseline.

- [ ] **Step 6: Commit**

```bash
git add tests/unit/test_rules.py tests/integration/test_cli_contract.py tests/fixtures/modules.py
git commit -m 'chore(tests): convert the signal tests off unittest and split by scope' -- \
  tests/unit tests/integration tests/fixtures tests/conftest.py tests/parity .ruff.toml
git status --short
```

---

### Task 5: environment and mocking fixtures

**Files:**

- Create: `tests/fixtures/environment.py`
- Modify: `tests/conftest.py` (add to `pytest_plugins`)
- Modify: `tests/unit/test_color_policy.py`
- Modify: `tests/unit/test_text_snapshot.py`
- Modify: `tests/integration/test_exit_contract.py`

**Interfaces:**

- Produces: fixtures `no_color`, `forced_color`, `dumb_terminal`, each
  function-scoped, each returning `None` and used for its side effect.

- [ ] **Step 1: Create `tests/fixtures/environment.py`**

```python
"""Colour-policy environment states, named instead of re-spelled per test.

`monkeypatch` stays the right tool for environment variables — it restores
them automatically. What these fixtures remove is the repetition of the same
three-variable dance in eight test bodies.
"""

from __future__ import annotations

import pytest


@pytest.fixture
def no_color(monkeypatch: pytest.MonkeyPatch) -> None:
    """`NO_COLOR` set, `FORCE_COLOR` cleared."""
    monkeypatch.setenv('NO_COLOR', '1')
    monkeypatch.delenv('FORCE_COLOR', raising=False)


@pytest.fixture
def forced_color(monkeypatch: pytest.MonkeyPatch) -> None:
    """`FORCE_COLOR` set, `NO_COLOR` cleared."""
    monkeypatch.setenv('FORCE_COLOR', '1')
    monkeypatch.delenv('NO_COLOR', raising=False)


@pytest.fixture
def dumb_terminal(monkeypatch: pytest.MonkeyPatch) -> None:
    """`TERM=dumb`, with both colour overrides cleared."""
    monkeypatch.setenv('TERM', 'dumb')
    monkeypatch.delenv('NO_COLOR', raising=False)
    monkeypatch.delenv('FORCE_COLOR', raising=False)
```

Add `'tests.fixtures.environment'` to `pytest_plugins` in `tests/conftest.py`:

```python
pytest_plugins = [
    'tests.fixtures.paths',
    'tests.fixtures.modules',
    'tests.fixtures.environment',
]
```

- [ ] **Step 2: Rewire `tests/unit/test_color_policy.py`**

The file holds exactly three tests, each opening with two or three `monkeypatch`
calls. Replace the `monkeypatch: pytest.MonkeyPatch` parameter with the matching
fixture and delete the setup lines. The assertions are unchanged — note that
`use_color` takes an explicit `is_tty` argument and the tests assert identity
against `True`/`False`, not truthiness. Verified against the file on
2026-07-27; the result is the whole module:

```python
"""Colour policy: the environment decides, and the caller says only whether
the stream is a terminal."""

from __future__ import annotations

from humansays.reporting import ansi


def test_no_color_disables_color(no_color: None) -> None:
    assert ansi.use_color(is_tty=True) is False


def test_force_color_overrides_non_tty(forced_color: None) -> None:
    assert ansi.use_color(is_tty=False) is True


def test_term_dumb_disables(dumb_terminal: None) -> None:
    assert ansi.use_color(is_tty=True) is False
```

The `import pytest` at line 1 becomes unused once the `monkeypatch` annotations
go — delete it. The `no_color: None` parameter is unused by name, which is why
`ARG001` is already ignored for `tests/**/*.py`.

- [ ] **Step 3: Rewire `tests/unit/test_text_snapshot.py`**

Its three tests each call `monkeypatch.setenv('NO_COLOR', '1')` — lines 35, 45
and 55 before the move, verified 2026-07-27. Replace the `monkeypatch` parameter
with `no_color: None` and delete the `setenv` line from each body.

Unlike `test_color_policy.py`, **keep `import pytest` here**: two of the three
tests also take `capsys: pytest.CaptureFixture[str]`, which still needs the
name. Nothing else changes.

- [ ] **Step 4: Replace the one real patch in `tests/integration/test_exit_contract.py`**

The file contains exactly one `monkeypatch.setattr`, in
`test_unexpected_errors_exit_seventy` (line 68 before the move). Verified
against the file on 2026-07-27, the whole test currently reads:

```python
def test_unexpected_errors_exit_seventy(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def explode(*args: object, **kwargs: object) -> None:
        raise RuntimeError('boom')

    monkeypatch.setattr('humansays.cli.application.collect_files', explode)
```

`explode` is a callable that raises, so `side_effect=` is the right `mocker`
argument — not `return_value=`. Replace the whole thing with:

```python
def test_unexpected_errors_exit_seventy(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    mocker: MockerFixture,
) -> None:
    mocker.patch(
        'humansays.cli.application.collect_files',
        side_effect=RuntimeError('boom'),
    )
```

The nested `explode` function goes with it: `side_effect` accepts an exception
instance directly, so the wrapper has nothing left to do. The rest of the test
body — writing `good.py`, calling `main`, asserting `code == 70` and
`'internal error' in capsys.readouterr().err` — is unchanged.

Add the import at the top of the file:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytest_mock import MockerFixture
```

`import pytest` stays — the file uses `pytest.mark.parametrize`,
`pytest.CaptureFixture` and `pytest.raises` elsewhere.

This is the only use of `pytest-mock` in the suite. It is a declared
`required_plugin` that nothing currently exercises, which is part of why this
plan exists.

- [ ] **Step 5: Verify no blind monkeypatch remains**

```bash
grep -rn 'monkeypatch.setattr' tests/ --include='*.py'   # must print nothing
grep -rn 'monkeypatch' tests/ --include='*.py' | grep -v 'tests/fixtures/environment.py'
```

The second command should print nothing: every remaining `monkeypatch` use is
inside the fixtures module.

Run: `uv run pytest -q`
Expected: 123 passed, coverage at or above baseline.

- [ ] **Step 6: Commit**

```bash
git add tests/fixtures/environment.py
git commit -m 'chore(tests): name the colour-policy environments as fixtures' -- \
  tests/fixtures tests/conftest.py tests/unit tests/integration
git status --short
```

---

### Task 6: retire `poc_fixtures.py` and `fixture_module.py`

**Files:**

- Delete: `tests/poc_fixtures.py`
- Delete: `tests/fixture_module.py`
- Modify: `.pytest.toml` (`pythonpath`)
- Modify: `.ruff.toml` (drop the `tests/fixture_module.py` ignore block)

- [ ] **Step 1: Confirm nothing imports them**

```bash
grep -rn 'poc_fixtures\|fixture_module\|FIXTURE_MODULE_PATH' tests/ scripts/ --include='*.py'
```

Expected: no output. If anything prints, a rewiring step was missed — fix it
before deleting.

**Note:** `scripts/smoke_test_package.py` references
`tests/golden/poc-parity/corpus/poc`, which is a different path and must not be
touched.

- [ ] **Step 2: Delete both files**

```bash
git rm tests/poc_fixtures.py tests/fixture_module.py
```

- [ ] **Step 3: Point `pythonpath` at the repository root**

Task 1 Step 3 set this to `[".", "tests"]`. Now that nothing imports
`poc_fixtures`, drop the second entry:

```toml
pythonpath = ["."]
```

Do **not** remove the key entirely. The research input proposed "drop
`pythonpath = ["tests"]` once nothing imports off it", which reads as deleting
the line; deleting it breaks every `from tests.fixtures ...` import in the
suite. `.` stays.

- [ ] **Step 4: Drop the fixture-module ruff exemption**

In `.ruff.toml`, delete this block from `[lint.per-file-ignores]`:

```toml
# Deliberately smelly fixture, byte-for-byte ported from the POC: its
# lint violations are the point (each one is what a specific rule detects).
"tests/fixture_module.py" = [
    "ANN001",
    "ANN201",
    "ANN205",
    "E731",
    "FBT002",
    "PLR0911",
    "RET505",
    "SIM116",
]
```

The smelly source now exists only as a string constant in
`tests/fixtures/sources.py`, which ruff does not parse as code.

- [ ] **Step 5: Verify**

Run: `uv run pytest -q`
Expected: 123 passed. Report the coverage number.

Deleting `tests/fixture_module.py` should not move coverage at all —
`.coveragerc.ini` has `source = humansays`, so test material was never measured.
**Confirm this rather than assuming it**: if coverage moved, say by how much and
stop.

Run: `bash scripts/format.sh && bash scripts/lint.sh ruff`
Expected: clean. If ruff now flags something in `tests/fixtures/sources.py`,
the string constants are being parsed as code — report rather than adding a
new ignore.

- [ ] **Step 6: Commit**

```bash
git commit -m 'chore(tests): retire poc_fixtures and the on-disk fixture module' -- \
  tests/poc_fixtures.py tests/fixture_module.py .pytest.toml .ruff.toml
git status --short
```

---

### Task 7: `scripts/test.sh`, the Makefile target, and the final gate

**Files:**

- Create: `scripts/test.sh`
- Modify: `scripts/ci.sh` (`run_test`)
- Modify: `Makefile`

**Interfaces:**

- Produces: `bash scripts/test.sh [unit|integration|tooling|all]`, matching
  `scripts/lint.sh`'s structure exactly.

- [ ] **Step 1: Write `scripts/test.sh`**

```bash
#!/usr/bin/env bash

# Test runner, split by scope. `unit`, `integration` and `tooling` run a
# single marker with coverage off, because `fail_under` applies to whatever
# ran and a partial run cannot reach it. `all` (default) runs everything and
# is the only subcommand that measures coverage.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# shellcheck disable=SC1091 source=scripts/log.sh
source "$SCRIPT_DIR/log.sh"

run_marker() {
    local marker="$1"
    local failed=0

    log_step "pytest -m $marker"
    if ! uv run python -m pytest -m "$marker" --no-cov; then
        log_error "The $marker tests failed"
        failed=1
    fi
    log_step_end

    return "$failed"
}

run_unit() {
    run_marker unit
}

run_integration() {
    run_marker integration
}

run_tooling() {
    run_marker tooling
}

run_all() {
    local failed=0

    log_step "py-compile"
    if ! uv run python -m compileall -q src tests; then
        log_error "Compile check failed"
        failed=1
    fi
    log_step_end

    log_step "pytest"
    if ! uv run python -m pytest; then
        log_error "Tests failed"
        failed=1
    fi
    log_step_end

    return "$failed"
}

main() {
    case "${1:-all}" in
    unit) run_unit ;;
    integration) run_integration ;;
    tooling) run_tooling ;;
    all)
        if ! run_all; then
            log_error "One or more test checks failed"
            exit 1
        fi
        log_success "All tests passed"
        ;;
    *)
        echo "Usage: $(basename "$0") [unit|integration|tooling|all]" >&2
        exit 1
        ;;
    esac
}

main "$@"
```

Make it executable: `chmod +x scripts/test.sh`

`run_all` reproduces `ci.sh`'s existing `run_test` body verbatim so behavior
under `make ci` does not change.

- [ ] **Step 2: Point `scripts/ci.sh` at it**

Replace the whole `run_test()` function in `scripts/ci.sh` with:

```bash
run_test() {
    bash "$SCRIPT_DIR/test.sh" all
}
```

This mirrors the existing `run_lint()`, which is already a one-line delegation
to `lint.sh`.

- [ ] **Step 3: Add the Makefile target**

```makefile
.PHONY: format lint test ci

format:
	@bash scripts/format.sh

lint:
	@bash scripts/lint.sh

test:
	@bash scripts/test.sh

ci:
	@bash scripts/ci.sh

.DEFAULT_GOAL := ci
```

Only the `.PHONY` line and the new `test` target change. Makefile recipes use
tab indentation — confirm with `cat -A Makefile | grep test` that the recipe
line starts with `^I`.

- [ ] **Step 4: Run every subcommand**

```bash
bash scripts/test.sh unit
bash scripts/test.sh integration
bash scripts/test.sh tooling
bash scripts/test.sh all
```

Expected: each passes. Record each subcommand's test count; the three marker
counts must sum to the `all` count. If they do not, a test carries two markers
or none — the collection hook should have made that impossible, so investigate
rather than adjusting the numbers.

- [ ] **Step 5: Run the suite-level assertions**

Every one of these must print nothing:

```bash
find tests -name '__init__.py' -not -path 'tests/fixtures/*' -not -path '*/poc-parity/*'
grep -rn 'unittest' tests/ --include='*.py' | grep -v poc-parity
grep -rn 'monkeypatch.setattr' tests/ --include='*.py'
grep -rn 'poc_fixtures\|fixture_module' tests/ scripts/ --include='*.py'
```

Confirm the markers are registered:

```bash
uv run pytest --markers | grep -E '^@pytest.mark.(unit|integration|tooling)'
```

Confirm no test escaped a marker:

```bash
uv run pytest --collect-only -q --no-cov -m 'not unit and not integration and not tooling'
```

Expected: `no tests ran`. The collection hook's `UsageError` is the enforcer
that makes this structural rather than incidental; this command is the check
that it worked.

- [ ] **Step 6: Full gate**

```bash
bash scripts/format.sh
bash scripts/lint.sh all
bash scripts/ci.sh
```

`bash scripts/lint.sh deadcode` is the one to watch: `vulture` scans `tests/`
at `min_confidence = 100` and has never seen fixture functions in this repo. If
it flags them, prefer a `# noqa`-free fix — adding the fixture to a
`whitelist.py` or raising the confidence threshold both hide real dead code.
Report before changing vulture's configuration.

- [ ] **Step 7: Report the before/after numbers**

State plainly, with the commands that produced them:

| | Before | After |
| --- | --- | --- |
| Tests | 124 passed, 36 subtests | _measure_ |
| Coverage | 92.63% | _measure_ |
| Wall clock | 0.73s | _measure_ |

The test count should be `123` with `0` subtests: one test deleted
(`test_disk_fixture_matches_the_fixture_module`, whose subject was deleted) and
`subTest` replaced by collect-then-assert. **Do not adjust `fail_under` to make
coverage pass.** If coverage dropped below 92.63%, find out which lines stopped
being exercised and report it.

- [ ] **Step 8: Commit**

```bash
git add scripts/test.sh
git commit -m 'chore(tests): add a scope-split test runner' -- \
  scripts/test.sh scripts/ci.sh Makefile
git status --short
```

Confirm `D  scripts/release_info.py` is still there.

---

## Verification

The complete gate, in order:

```bash
bash scripts/format.sh
bash scripts/lint.sh all
bash scripts/test.sh unit
bash scripts/test.sh integration
bash scripts/test.sh tooling
make ci
```

Package validation is unchanged by this branch, but run it once to prove that:

```bash
bash scripts/build.sh && bash scripts/smoke-package.sh
```

## What this plan claims, and what enforces each claim

Per `CLAUDE.md` rule 13, stated explicitly:

| Claim | Enforcer |
| --- | --- |
| Every test carries exactly one scope marker | `pytest_collection_modifyitems` in `tests/conftest.py` raises `pytest.UsageError` for a test outside `_MARKER_BY_DIRECTORY` |
| No `unittest.TestCase` remains outside the vendored corpus | Convention. The Task 7 `grep` checks it at review time; nothing checks it in CI |
| No `monkeypatch.setattr` remains | Convention. Same — a Task 7 `grep`, not a CI job |
| Test material is not measured for coverage | `.coveragerc.ini` `source = humansays` |
| `ast`/`tokenize` stay inside `humansays.analysis` | `lint-imports` via `.importlinter.ini`, plus `tests/integration/test_analysis_confinement.py` |
| The suite passes on every supported Python | The `Lint+Test` matrix job in `.github/workflows/integration.yml` |

The first row is the only structural guarantee this plan adds. The two `grep`
rows are conventions; do not describe them as enforced.
