# Contributing

Contributions are welcome when they are focused, tested, and understandable to
someone other than the person who wrote them at 2:00 AM.

## before starting

- Search existing issues and pull requests before creating another.
- Open an issue before substantial or breaking work.
- Keep pull requests limited to one logical change.
- Do not include unrelated formatting or generated-file churn.
- Never report a vulnerability in a public issue. Follow `SECURITY.md`.

Small typo and documentation fixes do not require an issue first.

## setup

```bash
git clone <repository-url>
cd <repository-name>
uv sync --all-groups
make ci
```

## development rules

- Add or update tests for behavior changes.
- Keep public APIs typed.
- Prefer clear code over explanatory comments.
- Add comments only when they preserve non-obvious constraints, risks, or
  reasoning that the code cannot communicate.
- Do not weaken lint, type, test, or coverage rules merely to make CI pass.
- Update documentation when behavior or contributor workflows change.

## commits

Use concise imperative subjects:

```text
feat(app): add packet validation
fix(app): fix empty input handling
docs: document release process
```

A pull request may contain multiple commits during review. Maintainers may
squash the branch when merging.

## quality gate

All commands except `make format` are check-only:

```bash
make ci
```

The `format` target modifies files and is intended for local use:

```bash
make format
```

## pull requests

A useful pull request explains:

- what changed,
- why the change is needed,
- how it was tested,
- any compatibility or security implications.

By contributing, you agree that your contribution is distributed under the
repository's license.
