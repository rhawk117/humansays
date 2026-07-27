# Identifier migration

The planned catalog was regrouped: 13 domains became 15, and 93 of the 158
rules changed identifier. This page is the record of that change. It exists so
a reader who arrives holding an old identifier can find where the rule went.

Nothing was deleted. Every rule listed below survives under its new
identifier, carrying the same claim, concern, default, detection statement and
message template it had before. Two kinds of change are recorded:

`renamed`
:   The domain was renamed and the number was kept. `STATE` became `ENCAP`,
    `FAIL` became `ERR`, and `NIT` became `SMELL`.

`migrated`
:   The rule moved to a different domain and received a new number there. These
    are the rules whose original domain no longer described them.

Old identifiers are retired, not aliased. Nothing resolves `SRP`, `COUP`,
`STATE`, `FAIL` or `NIT` after this change, and the vacated numbers listed at
the foot of this page are never reused.

## Mapping

| Old ID        | New ID     | Rule                                              | Change   |
| ------------- | ---------- | ------------------------------------------------- | -------- |
| `SRP001`      | `SOLID001` | Role conflict                                     | migrated |
| `SRP002`      | `SOLID002` | Effect in domain type                             | migrated |
| `SRP003`      | `SOLID003` | Mixed responsibilities                            | migrated |
| `SRP004`      | `SOLID004` | Mixed abstraction levels                          | migrated |
| `SRP005`      | `SOLID005` | Low field cohesion                                | migrated |
| `SRP006`      | `SOLID006` | God constructor                                   | migrated |
| `SRP007`      | `SOLID007` | Unclassifiable unit                               | migrated |
| `SRP008`      | `SOLID008` | Incohesive class                                  | migrated |
| `SRP009`      | `SOLID009` | Logging mixed with domain mutation                | migrated |
| `SRP010`      | `SOLID010` | Configuration object drives unrelated workflows   | migrated |
| `SRP011`      | `SOLID011` | Data object used as behavior switchboard          | migrated |
| `KISS003`     | `SOLID012` | Boolean mode switch                               | migrated |
| `KISS008`     | `SOLID013` | Repeated type or value dispatch                   | migrated |
| `CONTRACT010` | `SOLID014` | Function signature encodes multiple workflows     | migrated |
| `IDIOM011`    | `SOLID015` | Concrete factory return                           | migrated |
| `IDIOM015`    | `SOLID016` | Name mangled shadow                               | migrated |
| `COUP001`     | `SOLID017` | Undeclared dependency                             | migrated |
| `COUP002`     | `SOLID018` | Env read in logic                                 | migrated |
| `COUP003`     | `SOLID019` | Clock read inline                                 | migrated |
| `COUP004`     | `SOLID020` | Randomness inline                                 | migrated |
| `COUP005`     | `SOLID021` | Settings singleton access                         | migrated |
| `COUP006`     | `SOLID022` | Hidden dependency surface                         | migrated |
| `COUP007`     | `SOLID023` | Untestable without environment                    | migrated |
| `POLA002`     | `CQS004`   | Caller object mutation                            | migrated |
| `POLA007`     | `CQS005`   | Destructive mutation hidden from caller           | migrated |
| `POLA008`     | `CQS006`   | Persistence hidden in helper                      | migrated |
| `POLA009`     | `CQS007`   | Helper name hides external effects                | migrated |
| `STATE007`    | `LOD001`   | Field write outside owner                         | migrated |
| `COUP008`     | `LOD002`   | Single attribute dependency                       | migrated |
| `NIT002`      | `YAGNI001` | Zero state namespace                              | migrated |
| `NIT003`      | `YAGNI002` | Stateless single method                           | migrated |
| `NIT013`      | `YAGNI003` | Ceremonial abstraction                            | migrated |
| `NIT020`      | `YAGNI004` | Abc as interface                                  | migrated |
| `NIT022`      | `YAGNI005` | Stateless method declared on a class              | migrated |
| `NIT024`      | `YAGNI006` | Inheritance used only for configuration           | migrated |
| `DRY002`      | `YAGNI007` | Over parameterized helper                         | migrated |
| `IDIOM001`    | `SBD012`   | Process hash as identity                          | migrated |
| `IDIOM003`    | `SBD013`   | Import path mutation                              | migrated |
| `IDIOM004`    | `SBD014`   | Dynamic namespace access                          | migrated |
| `IDIOM006`    | `SBD015`   | Module object customization                       | migrated |
| `IDIOM009`    | `SBD016`   | Dynamic attribute mutation                        | migrated |
| `STATE001`    | `ENCAP001` | Excessive representable state space               | renamed  |
| `STATE002`    | `ENCAP002` | Module global read                                | renamed  |
| `STATE003`    | `ENCAP003` | Module global write                               | renamed  |
| `STATE004`    | `ENCAP004` | Mutable class attribute                           | renamed  |
| `STATE005`    | `ENCAP005` | Leaked internal mutable                           | renamed  |
| `STATE006`    | `ENCAP006` | Shared mutable binding                            | renamed  |
| `STATE008`    | `ENCAP008` | Aliased collection store                          | renamed  |
| `STATE009`    | `ENCAP009` | Partial init                                      | renamed  |
| `STATE010`    | `ENCAP010` | Invariant bypass                                  | renamed  |
| `STATE011`    | `ENCAP011` | Missing state owner                               | renamed  |
| `STATE012`    | `ENCAP012` | Unprotected invariant                             | renamed  |
| `STATE013`    | `ENCAP013` | Global declaration                                | renamed  |
| `STATE014`    | `ENCAP014` | Boolean state-space explosion                     | renamed  |
| `STATE015`    | `ENCAP015` | Nullable state-space explosion                    | renamed  |
| `STATE016`    | `ENCAP016` | Mutually dependent nullability                    | renamed  |
| `STATE017`    | `ENCAP017` | Duplicated state representation                   | renamed  |
| `STATE018`    | `ENCAP018` | Optional argument state product                   | renamed  |
| `STATE019`    | `ENCAP019` | State transition without explicit model           | renamed  |
| `STATE020`    | `ENCAP020` | Invariant spread across methods                   | renamed  |
| `FAIL001`     | `ERR001`   | Mutation between external effects                 | renamed  |
| `FAIL002`     | `ERR002`   | Unordered multi effect                            | renamed  |
| `FAIL003`     | `ERR003`   | Exception leaves partial state                    | renamed  |
| `FAIL004`     | `ERR004`   | Broad exception swallowed                         | renamed  |
| `FAIL005`     | `ERR005`   | Absence collapsed into failure                    | renamed  |
| `FAIL006`     | `ERR006`   | Retry without idempotence                         | renamed  |
| `FAIL007`     | `ERR007`   | Error message only                                | renamed  |
| `FAIL008`     | `ERR008`   | Side effect orchestration risk                    | renamed  |
| `FAIL009`     | `ERR009`   | Ambiguous failure contract                        | renamed  |
| `FAIL010`     | `ERR010`   | Silent infrastructure failure                     | renamed  |
| `FAIL011`     | `ERR011`   | External call inside validation logic             | renamed  |
| `FAIL012`     | `ERR012`   | Multiple failure modes collapse into one sentinel | renamed  |
| `FAIL013`     | `ERR013`   | Cleanup can mask the original failure             | renamed  |
| `FAIL014`     | `ERR014`   | Retry has no bounded policy                       | renamed  |
| `FAIL015`     | `ERR015`   | Error handling mutates durable state              | renamed  |
| `NIT001`      | `SMELL001` | Frozen candidate                                  | renamed  |
| `NIT004`      | `SMELL004` | Explicit deletion                                 | renamed  |
| `NIT005`      | `SMELL005` | Exception as control flow                         | renamed  |
| `NIT006`      | `SMELL006` | Handler over broad observed                       | renamed  |
| `NIT007`      | `SMELL007` | Sectioning comment                                | renamed  |
| `NIT008`      | `SMELL008` | Restating comment                                 | renamed  |
| `NIT009`      | `SMELL009` | Comment density high                              | renamed  |
| `NIT010`      | `SMELL010` | Docstring restates signature                      | renamed  |
| `NIT011`      | `SMELL011` | Todo marker                                       | renamed  |
| `NIT012`      | `SMELL012` | Placeholder implementation                        | renamed  |
| `NIT014`      | `SMELL014` | Compensating commentary                           | renamed  |
| `NIT015`      | `SMELL015` | Application contract typed as object              | renamed  |
| `NIT016`      | `SMELL016` | Direct environ index                              | renamed  |
| `NIT017`      | `SMELL017` | Cached singleton factory                          | renamed  |
| `NIT018`      | `SMELL018` | Missing dataclass slots                           | renamed  |
| `NIT019`      | `SMELL019` | Nested context managers                           | renamed  |
| `NIT021`      | `SMELL021` | Name mangled member                               | renamed  |
| `NIT023`      | `SMELL023` | Named behavior expressed as lambda                | renamed  |

## Vacated numbers

Seven numbers were left empty by rules that migrated out of a domain whose
other rules kept their numbering. They are not reused, so no future rule
carries an identifier a reader might remember as something else.

| Vacated    | Held by    | Now        |
| ---------- | ---------- | ---------- |
| `ENCAP007` | `STATE007` | `LOD001`   |
| `SMELL002` | `NIT002`   | `YAGNI001` |
| `SMELL003` | `NIT003`   | `YAGNI002` |
| `SMELL013` | `NIT013`   | `YAGNI003` |
| `SMELL020` | `NIT020`   | `YAGNI004` |
| `SMELL022` | `NIT022`   | `YAGNI005` |
| `SMELL024` | `NIT024`   | `YAGNI006` |

The `SRP` and `COUP` domains were dissolved rather than renamed, so neither
leaves vacated numbers behind: every rule in both moved, and both pages are
gone.
