# Externalized and omitted rules

This page records rules deliberately excluded from the catalog. Externalized checks cover ground already owned by mature linters or type checkers; omitted rules failed to establish their structural claims with sufficient rigor. Externalized checks may still surface as correlated evidence in higher-order findings.

## 7. Explicit externalizations, replacements, and omissions

Externalized checks may remain as raw facts when they strengthen a humansays finding, but humansays does not emit their standalone diagnostic.

| Source rule | Original name | Decision | Replacement | Explicit reason |
|---|---|---|---|---|
| HS-ARGS-05 | dependency-as-argument | omitted | — | Passing a dependency explicitly is normally healthier than hiding it in ambient state, so the original rule would push design in the wrong direction. |
| HS-ARGS-08 | untyped-varkwargs | external | — | Untyped `**kwargs` is directly covered by Ruff ANN003 and type checkers without a meaningful structural extension. |
| HS-CLASS-09 | lsp-signature-drift | external | — | Override signature compatibility is already checked precisely by type checkers, while behavioral substitutability cannot be established from signatures alone. |
| HS-EFFECT-12 | dynamic-python-execution | external | — | Standalone `eval`/`exec` detection is already owned by Bandit/Ruff security rules; humansays may retain the effect fact for higher-order findings. |
| HS-EFFECT-13 | process-image-replacement | external | — | Standalone `os.exec*` detection is security and process-policy linting; humansays only needs it as an effect and lifecycle fact. |
| HS-EFFECT-14 | shell-command-execution | external | — | Shell execution and `shell=True` are already covered by Bandit's shell-injection checks, leaving no unique standalone humansays claim. |
| HS-FAIL-04 | bare-except | external | — | Bare `except` is a conventional lint diagnostic already owned by Ruff/Pylint. |
| HS-FAIL-06 | absence-not-modeled | external | — | A return annotation that omits `None` is type-checker territory; humansays only retains correlated evidence when distinct failure paths collapse into absence. |
| HS-FAIL-10 | finally-suppresses | external | — | Control flow in `finally` is already reported by Ruff B012 with no structural inference needed. |
| HS-FAIL-11 | handler-never-fires | omitted | — | A handler not firing during one observation window does not establish that it is unreachable or unnecessary. |
| HS-FIND-15 | dead defensive structure | omitted | — | Runtime non-execution cannot justify the finding's claim that defensive structure is dead. |
| HS-INIT-05 | missing-transition-method | replaced | STATE transition-without-explicit-model | The absence of a named transition method proves nothing, so it is replaced by a rule that requires repeated ad hoc state writes and transition guards. |
| HS-INIT-09 | equality-without-invariant | omitted | — | Defining equality does not imply that construction validation or a stronger invariant is required. |
| HS-NARRATION-05 | commented-out-code | external | — | Commented-out code is directly covered by Ruff ERA001/eradicate-style checks and does not require correlated structural analysis. |
| HS-NARRATION-08 | defensive-redundancy | replaced | IDIOM008 | The broad defensive-redundancy claim trusted annotations and observed call sites too much; it is replaced by the narrow numeric truthiness rule IDIOM008. |
| HS-NARRATION-12 | branch-never-taken | omitted | — | An untaken branch in one runtime sample is coverage evidence, not proof that the branch is dead. |
| HS-PURPOSE-07 | missing-return-annotation | external | — | Missing return annotations are owned by annotation linters and type checkers; humansays gains no structural inference by repeating the standalone diagnostic. |
| HS-STATE-02 | mutable-default-argument | external | — | Mutable argument defaults are a mature correctness check in Ruff B006 and need no higher-order humansays rule unless used as evidence of shared-state ownership. |

Official overlap references used for these decisions: [Ruff rule index](https://docs.astral.sh/ruff/rules/), [Ruff ANN003](https://docs.astral.sh/ruff/rules/missing-type-kwargs/), [Bandit shell-injection checks](https://bandit.readthedocs.io/en/latest/plugins/index.html), and [mypy override checks](https://mypy.readthedocs.io/en/stable/error_code_list.html#check-validity-of-overrides-override).
