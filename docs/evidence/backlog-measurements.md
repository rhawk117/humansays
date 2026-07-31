# Measurements recorded in the retired backlog

`.agent-specs/backlog.md` was deleted on 2026-07-30 when the project stopped
keeping a backlog. Four of its entries carried measurements rather than
intentions. Those are recorded here so the deletion loses no evidence, per
`CLAUDE.md` rule 11 and `agent-protocol.md` §9.

Nothing here is a plan. Each section states what was measured, when, and what
the measurement settled.

## Folding `FunctionVisitor` into the single descent — measured payoff is nil

Extraction runs one shallow visitor pass per function alongside the descent that
finds lambdas. Merging them was considered and measured rather than assumed.

- Extraction reaches each AST node **1.69–1.91 times**.
- `lambda_nodes` accounts for **52.5%** of all node-reach events — exactly one
  full extra pass.
- Stubbing it out changes wall-clock by **+0.3%** on the poc-parity corpus and
  **−2.3%** on `src/humansays`, both inside a **~2 ms** standard deviation over
  **40** interleaved trials. The two corpora disagree on the sign.

The merge would also perturb the append order of `BodyFacts.incidents`, which is
load-bearing: incidents of one signal in one function share a location, so their
findings tie on `Finding.sort_key` and the stable sort is what preserves their
order.

**Settled:** the payoff is nil, so the merge is not worth the behaviour risk.
`tests/unit/test_extraction_cost.py` pins the ratio instead, which is what keeps
a third pass from landing unnoticed.

## The traversal ceiling is deliberately loose

`tests/unit/test_extraction_cost.py` sets the ceiling at **2.5** reaches per node
against a measured **1.69–1.91**. The width absorbs drift in `ast.unparse`
internals across interpreter versions.

**Settled:** it catches a new full pass, which would land near **2.9**. It does
not catch incremental creep. If the ratio is ever driven down deliberately, the
ceiling has to be tightened in the same change or the gain is not held.

## Version normalization inside `humansays.analysis` is not warranted

Measured before deciding not to build it:

- **Zero** `sys.version_info` branches in `src/`.
- No reference to `ast.Str`, `ast.Num`, `type_params` or `ast.TypeAlias`.
- CI already runs the suite on **3.11 through 3.14**.

`tests/integration/test_analysis_confinement.py` fails if `version_info` appears
anywhere in `facts` or `rules`. `tests/unit/test_version_gated_syntax.py`
exercises PEP 695 type parameters, PEP 696 defaults, PEP 701 f-strings and
`ast.TypeAlias` under version gates across the same matrix. Extraction handled
all of them already.

**Settled:** a normalization boundary with no divergence to normalize and no
test that can fail is speculative. Revisit only if a fixture diverges.

## The byte-diff parity corpus is thin, and known to be

Measured July 2026:

- `poc` is **14** files and **0** signals, so four of its eight captured files
  are empty finding lists and comparing them proves nothing.
- `django` is **3** files and **9** findings, and is the whole of the evidence.

Phase C1 reported an empty byte diff at all **seven** commits on that basis.

The `poc` corpus is clean for a legitimate reason: it is the prototype's own
source, whose 20 self-findings were all comment and docstring counting, retired
as HS010 and HS011.

**Settled:** the corpus needs replacing rather than fixing, and a replacement
should fire every shipped rule at least once, asserted, so the gate cannot go
thin unnoticed. The capture script this measurement used (`.migration/capture.sh`)
no longer exists; `.migration/` was gitignored and has been deleted.
