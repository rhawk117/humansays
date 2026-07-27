# POLA rules

POLA rules detect behavior that contradicts names, syntax, or ordinary API
expectations. These rules identify design decisions that violate the principle
of least astonishment, such as properties performing I/O, operators having
hidden effects, or helper functions reaching external systems.

None of the rules below are implemented yet. They are planned.

Background reading: the
[principle of least astonishment](https://en.wikipedia.org/wiki/Principle_of_least_astonishment)
and its
[original discussion on the WikiWikiWeb](https://wiki.c2.com/?PrincipleOfLeastAstonishment).

| ID      | Rule                            | Default | Concern |
| ------- | ------------------------------- | ------- | ------- |
| POLA001 | Effectful property              | on      | hazard  |
| POLA003 | Representation as identity      | on      | hazard  |
| POLA004 | Effectful operator overload     | on      | hazard  |
| POLA005 | None as command                 | on      | review  |
| POLA006 | Non-obvious arithmetic overload | on      | review  |

## Rule details

### POLA001 Effectful property

**Claim.** risk

**Detection/default.** Property performs I/O, mutation, locking, subprocess work or substantial computation

**Message template.** Property `permissions` performs a database query despite being presented as ordinary attribute access.

### POLA003 Representation as identity

**Claim.** risk

**Detection/default.** `str()` or `repr()` output becomes a persistent key, identifier, filename or protocol value

**Message template.** `repr(entity)` is used as a persistent cache key even though representation output is not an explicit identity contract.

### POLA004 Effectful operator overload

**Claim.** risk

**Detection/default.** Operator method performs I/O, external mutation, subprocess work or notification

**Message template.** `Deployment.__add__` performs network I/O even though `left + right` appears to be a local value operation.

### POLA005 None as command

**Claim.** design

**Detection/default.** `None` selects clearing, resetting, deletion or another alternate operation

**Message template.** Passing `None` to `update_name()` means "clear the name," hiding a command inside nullability.

### POLA006 Non-obvious arithmetic overload

**Claim.** design

**Detection/default.** Arithmetic, matrix, shift or bitwise operator lacks immediately obvious domain meaning

**Message template.** `{expression}` has no meaning a reader can infer without opening `{method}`; does a reader immediately know what this operation does?
