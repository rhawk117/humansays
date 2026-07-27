# Reconciliation: shipped rules against the new catalog

This document maps each of the 19 shipped rule codes in
`src/humansays/catalog.py` to its fate in the new 175-rule catalog published
under `docs/site/planned/`. The mapping follows a two-hop join: a shipped
`HS0NN` code matches a prototype `PY0NN` check by name and behavior, §8 of
`NEW_RULES.md` crosswalks that prototype to one or more `HS-DOMAIN-NN`
provenance slugs, and §9 of `NEW_RULES.md` resolves each slug to a final
`DOMAIN###` rule or an internal evidence ID.

Two disposition facts from `docs/site/planned/index.md` govern the last
column. A `hint` is "emitted by the review profile; intentionally unweighted"
and does not count toward a score. `evidence` is "hidden unless cited by a
finding or requested with `--show-evidence`" and also does not count toward a
score. Both are demotions from the shipped model, where every rule was scored:
each shipped `warning` carried weight 3.0 and each `advisory` carried weight
1.0.

## Full mapping

| Shipped | Signal                    | Prototype | Source slug                 | New ID                             | Disposition | What changes for a user                                                                                                                                                                               |
| ------- | ------------------------- | --------- | --------------------------- | ---------------------------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| HS001   | many-arguments            | PY001     | HS-ARGS-01                  | CONTRACT003                        | on          | No change. Stays a scored, selectable rule.                                                                                                                                                           |
| HS002   | boolean-modes             | PY002     | HS-ARGS-03                  | SOLID012                           | on          | No change. Stays a scored, selectable rule.                                                                                                                                                           |
| HS003   | deep-nesting              | PY003     | HS-SHAPE-03                 | kiss.deep_nesting                  | evidence    | No longer a standalone scored rule. Becomes hidden evidence that surfaces only when cited by a finding or with `--show-evidence`.                                                                     |
| HS004   | shared-mutable-state      | PY004     | HS-STATE-06                 | ENCAP006                           | on          | No change. Stays a scored, selectable rule.                                                                                                                                                           |
| HS005   | broad-exception           | PY005     | HS-FAIL-01/02/03            | ERR004 (+ 2 evidence)              | on (split)  | The swallowed-exception case stays scored as ERR004. The logged-only and re-raised variants become hidden evidence (`err.broad_exception_logged_only`, `err.broad_exception_reraised`).               |
| HS006   | multiple-mutation-owners  | PY006     | HS-STATE-04                 | encap.multiple_mutation_owners     | evidence    | No longer a standalone scored rule. Becomes hidden evidence. The concern re-surfaces through the "missing state owner" finding (ENCAP011).                                                            |
| HS007   | mixed-boundaries          | PY007     | HS-EFFECT-06, HS-FIND-01/02 | SOLID003, ERR008 (+ 1 evidence)    | on (split)  | The raw mixed-boundary signal becomes hidden evidence (`solid.mixed_effect_boundaries`). Its two findings stay scored: mixed responsibilities (SOLID003) and side-effect orchestration risk (ERR008). |
| HS008   | low-class-cohesion        | PY008     | HS-CLASS-01, HS-FIND-05     | SOLID005, SOLID008                 | on (split)  | No loss of scoring. Splits into two scored rules: low field cohesion (SOLID005) and incohesive class (SOLID008).                                                                                      |
| HS009   | long-function             | PY009     | HS-SHAPE-01                 | kiss.long_function                 | evidence    | No longer a standalone scored rule. Becomes hidden evidence.                                                                                                                                          |
| HS012   | many-class-attributes     | PY012     | HS-CLASS-03                 | solid.many_class_attributes        | evidence    | No longer a standalone scored rule. Becomes hidden evidence.                                                                                                                                          |
| HS013   | attribute-prefix-cluster  | PY013     | HS-CLASS-05                 | solid.attribute_prefix_cluster     | evidence    | No longer a standalone scored rule. Becomes hidden evidence.                                                                                                                                          |
| HS014   | validated-argument-bundle | PY014     | HS-INIT-07                  | contract.validated_argument_bundle | evidence    | No longer a standalone scored rule. Becomes hidden evidence.                                                                                                                                          |
| HS015   | static-method             | PY015     | (none in §9)                | YAGNI005                           | hint        | No longer contributes to the score. Becomes an unweighted reviewer hint in the review profile.                                                                                                        |
| HS016   | lambda-expression         | PY016     | (none in §9)                | SMELL023                           | hint        | No longer contributes to the score. Becomes an unweighted reviewer hint in the review profile.                                                                                                        |
| HS017   | long-file                 | PY017     | HS-SHAPE-10                 | kiss.long_module                   | evidence    | No longer a standalone scored rule. Becomes hidden evidence.                                                                                                                                          |
| HS018   | many-base-classes         | PY018     | HS-CLASS-08                 | solid.many_base_classes            | evidence    | No longer a standalone scored rule. Becomes hidden evidence.                                                                                                                                          |
| HS019   | many-branches             | PY019     | HS-SHAPE-04                 | kiss.many_branches                 | evidence    | No longer a standalone scored rule. Becomes hidden evidence.                                                                                                                                          |
| HS021   | lazy-import               | PY021     | (none in §9)                | IDIOM016                           | hint        | No longer contributes to the score. Becomes an unweighted reviewer hint in the review profile.                                                                                                        |
| HS022   | dense-function            | PY022     | HS-SHAPE-02                 | kiss.dense_function                | evidence    | No longer a standalone scored rule. Becomes hidden evidence.                                                                                                                                          |

Note on the three `hint` rows: §8 crosswalks PY015, PY016, and PY021 to "NIT
rule" or "IDIOM rule; reviewer hint only" without a `DOMAIN###` ID, and those
three IDs do not appear in the §9 ledger. The specific IDs come from the domain
pages themselves. `docs/site/planned/yagni.md` lists YAGNI005 ("Stateless
method declared on a class", "Prototype PY015"), `docs/site/planned/smell.md`
lists SMELL023 ("Named behavior expressed as lambda", "Prototype PY016"), and
`docs/site/planned/idiom.md` lists IDIOM016 ("Import inside function or
method", "Prototype PY021"). All three carry `default = hint`.

## The three gaps in the shipped numbering

The shipped codes skip HS010, HS011, and HS020. These line up with the three
prototype checks §8 marks `omitted`:

- PY010 (comments): "raw comment count was noisy and duplicated narration
    evidence."
- PY011 (docstrings): "raw docstring count did not establish a structural
    problem."
- PY020 (future annotations): "version-dependent modernization belongs to Ruff
    and loses value on newer Python."

These were never shipped, so nothing is lost for a user of the shipped tool.

## What to keep from the drop list

No shipped rule is removed from the catalog. Every one of the 19 survives as a
scored rule, an unweighted hint, or hidden evidence. The judgment calls are
about demotion from scored to unscored, not deletion.

### The three hint demotions look right

The brief flagged HS015, HS016, and HS021 as the most user-visible change.
Their demotion to unweighted hints is defensible:

- HS015 static-method and HS016 lambda-expression shipped with confidence 0.99
    and weight 3.0. High detection confidence is not the same as high concern. A
    static method on a class and a lambda holding named behavior are both style
    positions, not correctness or hazard signals. The regroup sends them to
    different homes: a static method is class machinery the class itself does not
    use, which is what YAGNI observes, and the lambda is a stylistic position,
    which is what SMELL collects. Both domains carry weight 0.00. Keeping the two
    visible but unweighted preserves the prompt to a reviewer without letting a
    stylistic preference move a score.
- HS021 lazy-import shipped as advisory weight 1.0. Lazy imports are frequently
    correct: they break import cycles and defer optional dependencies. IDIOM016's
    message even carves out "configured optional-dependency or cycle-breaking
    boundaries." A rule that fires on a legitimate pattern belongs as a hint, not
    a scored finding. This demotion looks right.

If any of the three were to be reconsidered for scoring, IDIOM016 (lazy-import)
is the weakest candidate to promote, because the false-positive rate on
intentional lazy imports is high. YAGNI005 and SMELL023 would stay unweighted.

### The evidence demotions are the larger change and are individually defensible

Ten shipped rules dropped from scored to hidden evidence: HS003, HS006, HS009,
HS012, HS013, HS014, HS017, HS018, HS019, HS022. This is a bigger shift in
scored behavior than the three hint demotions, because it is more rules.

Most of these are raw size or shape thresholds: deep-nesting, long-function,
dense-function, many-branches, long-file, many-class-attributes,
many-base-classes, attribute-prefix-cluster. A raw threshold on its own is a
weak basis for a score, and the new model routes these into KISS and SOLID as
inputs that findings can cite rather than as standalone penalties. That is a
reasonable design and none of them belongs back in the scored set on its own.

Two are worth a second look:

- HS006 multiple-mutation-owners (shipped warning, confidence 0.70) is now
    `encap.multiple_mutation_owners` evidence. The concern it raised is picked up
    by the "missing state owner" finding (HS-FIND-04 to ENCAP011, on), so the
    signal is not lost as long as that finding cites it. If it belonged anywhere
    as a scored rule again, it would be ENCAP.
- HS014 validated-argument-bundle (shipped warning, confidence 0.88) is now
    `contract.validated_argument_bundle` evidence. This shipped with high weight
    and confidence, so the demotion is the most aggressive of the ten. A validated
    argument bundle can be a legitimate pattern, so evidence is the safer default,
    but if it were promoted it would sit in CONTRACT.

### Residual risk this reconciliation cannot close

`evidence` surfaces to a default user only when a finding cites it or when
`--show-evidence` is passed. For the ten evidence demotions, the concern reaches
a default user only through some retained finding. The §9 ledger records the
disposition of each signal but not which findings cite which evidence, so this
reconciliation cannot confirm, for every evidence row, that a retained finding
actually cites it. Where no finding cites a given piece of evidence, that signal
is effectively silent by default. Confirming the citation edges for the ten
evidence rows is an open item that needs the finding definitions, not the
ledger.

## Behavior-change callouts

Every case below changes what a shipped user sees or how a score is computed.

**Scored to unweighted hint (3 rules):**

- HS015 static-method: warning weight 3.0 to YAGNI005 hint. No longer scored.
- HS016 lambda-expression: warning weight 3.0 to SMELL023 hint. No longer scored.
- HS021 lazy-import: advisory weight 1.0 to IDIOM016 hint. No longer scored.

**Scored to hidden evidence (10 rules):**

- HS003 deep-nesting, HS009 long-function, HS022 dense-function, HS019
    many-branches, HS017 long-file, HS012 many-class-attributes, HS013
    attribute-prefix-cluster, HS018 many-base-classes: each was scored and is now
    `kiss.*` or `solid.*` evidence, hidden by default.
- HS006 multiple-mutation-owners: scored to `encap.multiple_mutation_owners`
    evidence.
- HS014 validated-argument-bundle: scored to `contract.validated_argument_bundle`
    evidence.

**Split, with partial demotion (3 rules):**

- HS005 broad-exception: the swallowed case stays scored (ERR004); the
    logged-only and re-raised variants become evidence.
- HS007 mixed-boundaries: the raw signal becomes evidence
    (`solid.mixed_effect_boundaries`); two findings stay scored (SOLID003,
    ERR008).
- HS008 low-class-cohesion: no demotion. Splits into two scored rules (SOLID005,
    SOLID008).

**No change (4 rules):**

- HS001 (CONTRACT003), HS002 (SOLID012), HS004 (ENCAP006) stay scored and
    selectable. HS005's primary path (ERR004) also stays scored.

**Nothing dropped from the catalog.** No shipped rule maps to `omitted`,
`external`, or `off`. The three `omitted` prototype checks (PY010, PY011, PY020)
correspond to the unused HS010, HS011, and HS020 numbering gaps and were never
shipped.
</content>
</invoke>
