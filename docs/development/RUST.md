# Rust migration

The current package remains pure Python and uses `uv_build`. Rust should be
introduced only when profiling identifies analysis work that benefits from a
native implementation.

## Stable boundary established now

Keep the public interface independent of Python AST objects:

```python
def analyze_source(
    source: str,
    *,
    path: str,
) -> list[Finding]:
    ...
```

The CLI, reporters, JSON schema, scoring model, and tests should consume stable
finding models. Raw `ast.AST` nodes should remain internal implementation
details.

## Phase 1: private Python engine

Route analysis through a private implementation boundary such as:

```text
src/humansays/_engine.py
```

All callers use this boundary rather than importing individual AST visitors.

## Phase 2: private Rust extension

Add a mixed project layout:

```text
src/humansays_core/
├── Cargo.lock
├── Cargo.toml
└── src/
    └── lib.rs

src/humansays/
├── _core.pyi
├── cli.py
├── engine.py
└── models.py
```

Expose the native module as `humansays._core`. Keep the Python package as the
public API and treat the extension as replaceable implementation detail.

## Phase 3: switch the build backend

Replace only the build backend configuration:

```toml
[build-system]
requires = ["maturin>=1,<2"]
build-backend = "maturin"

[tool.maturin]
bindings = "pyo3"
python-source = "src"
manifest-path = "src/humansays_core/Cargo.toml"
module-name = "humansays._core"
```

Keep `[project].version` in `pyproject.toml` as the release source of truth.
The internal crate should not own the public package version:

```toml
[package]
name = "humansays-core"
version = "0.0.0"
publish = false
```

## Phase 4: expand package building

The top-level `ci.yml`, `release.yml`, PyPI publication job, GitHub Release
workflow, version-change detection, and documentation workflow remain
unchanged.

Replace the implementation inside `_package.yml` with a native wheel matrix
that builds platform wheels and a source distribution. Each produced wheel is
then smoke-tested on its matching platform before the same artifacts are
published.

This is intentionally deferred until Rust exists. Designing native wheel
matrices for code that does not exist would create maintenance without value.
