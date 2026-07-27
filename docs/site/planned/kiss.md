# KISS rules

KISS rules catch code that's needlessly complex, deeply nested, or indirectly
structured, making it harder to follow. These patterns add control-flow
pressure that obscures intent.

None of the rules below are implemented yet. They are planned.

Background reading:
[Extract Function](https://refactoring.com/catalog/extractFunction.html),
[Decompose Conditional](https://refactoring.com/catalog/decomposeConditional.html)
and
[Replace Nested Conditional with Guard Clauses](https://refactoring.com/catalog/replaceNestedConditionalWithGuardClauses.html)
in Martin Fowler's refactoring catalog.

| ID | Rule | Default | Concern |
|---|---|---|---|
| KISS001 | Effect in comprehension | on | review |
| KISS002 | Helper chain | on | review |
| KISS003 | Boolean mode switch | on | review |
| KISS004 | Control flow pressure | on | review |
| KISS005 | Long loop body | on | review |
| KISS006 | Branch pyramid | on | review |
| KISS007 | Compound domain condition | on | review |
| KISS008 | Repeated type or value dispatch | on | review |
| KISS009 | Exception handler fanout | on | review |

## Rule details

### KISS001 Effect in comprehension

**Claim.** design

**Detection/default.** Effect call inside a comprehension or generator

**Message template.** This comprehension performs `{effect}` while presenting the operation as value construction.

### KISS002 Helper chain

**Claim.** design

**Detection/default.** ≥3 private helpers callable only in sequence

**Message template.** `{class}` contains a chain of `{helper_count}` private helpers that can only execute in one sequence.

### KISS003 Boolean mode switch

**Claim.** design

**Detection/default.** Boolean selecting between two behaviors in the body

**Message template.** Boolean `{parameter}` selects between `{mode_count}` workflows inside `{symbol}`.

### KISS004 Control flow pressure

**Claim.** design

**Detection/default.** cf + shp

**Message template.** `{symbol}` combines nesting `{nesting}`, `{branches}` branches, and `{exits}` exits into one control-flow region.

### KISS005 Long loop body

**Claim.** design

**Detection/default.** Loop body exceeds the configured logical-statement or control-flow threshold

**Message template.** This loop contains 14 statements, four branches and three effects, making iteration and workflow inseparable.

### KISS006 Branch pyramid

**Claim.** design

**Detection/default.** One operation is buried beneath at least three control-flow layers

**Message template.** The primary operation is reached only after an `if`, loop and nested `if`, indicating guard-clause or extraction pressure.

### KISS007 Compound domain condition

**Claim.** design

**Detection/default.** Conditional contains more than three Boolean operands or mixes several domain decisions

**Message template.** This predicate has `{operand_count}` Boolean inputs and a theoretical truth table of `{representable_states}` combinations.

### KISS008 Repeated type or value dispatch

**Claim.** design

**Detection/default.** Conditional chain selects behavior from one type, tag, enum or literal discriminator

**Message template.** Eight branches differ only by the selected callable, so this conditional is functioning as a dispatch dictionary.

### KISS009 Exception handler fanout

**Claim.** design

**Detection/default.** One `try` statement has more than six distinct handlers

**Message template.** This operation defines seven exception branches and five distinct recovery behaviors in one control-flow region.
