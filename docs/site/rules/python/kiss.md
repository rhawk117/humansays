# KISS rules

KISS rules catch code that's needlessly complex, deeply nested, or indirectly structured, making it harder to follow. These patterns add control-flow pressure that obscures intent.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| KISS001 | Effect in comprehension | design | review | on | HS-EFFECT-11 | Effect call inside a comprehension or generator | This comprehension performs `{effect}` while presenting the operation as value construction. |
| KISS002 | Helper chain | design | review | on | HS-SHAPE-07 | ≥3 private helpers callable only in sequence | `{class}` contains a chain of `{helper_count}` private helpers that can only execute in one sequence. |
| KISS003 | Boolean mode switch | design | review | on | HS-ARGS-03 | Boolean selecting between two behaviors in the body | Boolean `{parameter}` selects between `{mode_count}` workflows inside `{symbol}`. |
| KISS004 | Control flow pressure | design | review | on | HS-FIND-06 | cf + shp | `{symbol}` combines nesting `{nesting}`, `{branches}` branches, and `{exits}` exits into one control-flow region. |
| KISS005 | Long loop body | design | review | on | HS-SHAPE-13 | Loop body exceeds the configured logical-statement or control-flow threshold | This loop contains 14 statements, four branches and three effects, making iteration and workflow inseparable. |
| KISS006 | Branch pyramid | design | review | on | HS-SHAPE-14 | One operation is buried beneath at least three control-flow layers | The primary operation is reached only after an `if`, loop and nested `if`, indicating guard-clause or extraction pressure. |
| KISS007 | Compound domain condition | design | review | on | HS-SHAPE-15 | Conditional contains more than three Boolean operands or mixes several domain decisions | This predicate has `{operand_count}` Boolean inputs and a theoretical truth table of `{representable_states}` combinations. |
| KISS008 | Repeated type or value dispatch | design | review | on | HS-SHAPE-18 | Conditional chain selects behavior from one type, tag, enum or literal discriminator | Eight branches differ only by the selected callable, so this conditional is functioning as a dispatch dictionary. |
| KISS009 | Exception handler fanout | design | review | on | HS-FAIL-13 | One `try` statement has more than six distinct handlers | This operation defines seven exception branches and five distinct recovery behaviors in one control-flow region. |
