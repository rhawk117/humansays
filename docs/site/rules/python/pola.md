# POLA rules

POLA rules detect behavior that contradicts names, syntax, or ordinary API expectations. These rules identify design decisions that violate the principle of least astonishment, such as properties performing I/O, operators having hidden effects, or helper functions reaching external systems.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| POLA001 | Effectful property | risk | hazard | on | HS-EFFECT-15 | Property performs I/O, mutation, locking, subprocess work or substantial computation | Property `permissions` performs a database query despite being presented as ordinary attribute access. |
| POLA002 | Caller object mutation | risk | hazard | on | HS-STATE-05 | Mutates a parameter the caller owns | `{symbol}` mutates caller-owned `{parameter}` without making destructive behavior explicit. |
| POLA003 | Representation as identity | risk | hazard | on | HS-PURPOSE-15 | `str()` or `repr()` output becomes a persistent key, identifier, filename or protocol value | `repr(entity)` is used as a persistent cache key even though representation output is not an explicit identity contract. |
| POLA004 | Effectful operator overload | risk | hazard | on | HS-EFFECT-16 | Operator method performs I/O, external mutation, subprocess work or notification | `Deployment.__add__` performs network I/O even though `left + right` appears to be a local value operation. |
| POLA005 | None as command | design | review | on | HS-ARGS-12 | `None` selects clearing, resetting, deletion or another alternate operation | Passing `None` to `update_name()` means "clear the name," hiding a command inside nullability. |
| POLA006 | Non-obvious arithmetic overload | design | review | on | HS-CLASS-17 | Arithmetic, matrix, shift or bitwise operator lacks immediately obvious domain meaning | `{expression}` has no meaning a reader can infer without opening `{method}`; does a reader immediately know what this operation does? |
| POLA007 | Destructive mutation hidden from caller | risk | hazard | on | HS-FIND-19 | own + (nam or shp) | normalize() deletes and rewrites entries in its input mapping although its name and return contract do not communicate destructive mutation. |
| POLA008 | Persistence hidden in helper | risk | hazard | on | Later combined catalog. | A generic helper name reaches a database write or commit boundary. | Helper `{helper}` performs `{persistence_effect}` although its name does not communicate durable mutation. |
| POLA009 | Helper name hides external effects | design | review | on | Later combined catalog. | A generic or pure-looking helper reaches network, filesystem, database, notification, or subprocess effects. | Helper `{helper}` performs `{effects}`, behavior a caller cannot infer from its name. |
