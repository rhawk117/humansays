# KISS rules

KISS rules catch code that's needlessly complex, deeply nested, or indirectly
structured, making it harder to follow. These patterns add control-flow
pressure that obscures intent.

!!! warning "Not implemented"

    These rules are designed, not shipped. Nothing on this page runs in
    version `0.1.0a1`, which implements [19 rules](../rules/index.md).

Background reading:
[Extract Function](https://refactoring.com/catalog/extractFunction.html),
[Decompose Conditional](https://refactoring.com/catalog/decomposeConditional.html)
and
[Replace Nested Conditional with Guard Clauses](https://refactoring.com/catalog/replaceNestedConditionalWithGuardClauses.html)
in Martin Fowler's refactoring catalog.

| ID      | Rule                      | Default | Concern |
| ------- | ------------------------- | ------- | ------- |
| KISS001 | Effect in comprehension   | on      | review  |
| KISS002 | Helper chain              | on      | review  |
| KISS004 | Control flow pressure     | on      | review  |
| KISS005 | Long loop body            | on      | review  |
| KISS006 | Branch pyramid            | on      | review  |
| KISS007 | Compound domain condition | on      | review  |
| KISS009 | Exception handler fanout  | on      | review  |

## Rule details

### KISS001 Effect in comprehension { #KISS001 }

Claim
:   design

Detection
:   Effect call inside a comprehension or generator

Message
:   This comprehension performs `{effect}` while presenting the operation as value construction.

### KISS002 Helper chain { #KISS002 }

Claim
:   design

Detection
:   ≥3 private helpers callable only in sequence

Message
:   `{class}` contains a chain of `{helper_count}` private helpers that can only execute in one sequence.

### KISS004 Control flow pressure { #KISS004 }

Claim
:   design

Detection
:   cf + shp

Message
:   `{symbol}` combines nesting `{nesting}`, `{branches}` branches, and `{exits}` exits into one control-flow region.

### KISS005 Long loop body { #KISS005 }

Claim
:   design

Detection
:   Loop body exceeds the configured logical-statement or control-flow threshold

Message
:   This loop contains 14 statements, four branches and three effects, making iteration and workflow inseparable.

### KISS006 Branch pyramid { #KISS006 }

Claim
:   design

Detection
:   One operation is buried beneath at least three control-flow layers

Message
:   The primary operation is reached only after an `if`, loop and nested `if`, indicating guard-clause or extraction pressure.

### KISS007 Compound domain condition { #KISS007 }

Claim
:   design

Detection
:   Conditional contains more than three Boolean operands or mixes several domain decisions

Message
:   This predicate has `{operand_count}` Boolean inputs and a theoretical truth table of `{representable_states}` combinations.

### KISS009 Exception handler fanout { #KISS009 }

Claim
:   design

Detection
:   One `try` statement has more than six distinct handlers

Message
:   This operation defines seven exception branches and five distinct recovery behaviors in one control-flow region.
