# Failure and imports

Two rules cover the moments where a function body stops describing its own work
and reaches outside itself: once to a failure path, and once to the module
system. Both are recorded as incidents while walking a single function body, so
each occurrence produces its own finding rather than a count compared against a
threshold. Neither is a verdict. Each one is a place worth a second look during
review.

## HS005 broad-exception

| Field           | Value                                                                    |
| --------------- | ------------------------------------------------------------------------ |
| Severity        | WARNING                                                                  |
| Confidence      | 0.96                                                                     |
| Weight          | 3.0                                                                      |
| Tuned by        | Not configurable (`BROAD_EXCEPTION_NAMES` in `src/humansays/const.py`)   |
| Review question | Which exceptions are expected, and should unexpected failures propagate? |

**When it fires.** The body visitor inspects every `ast.ExceptHandler` it
reaches, including handlers on `try` and on `except*`, and records an incident
in two cases.

The first case is a bare `except:` with no exception type at all. The evidence
string is `bare except`.

The second case is a handler whose type resolves to a dotted name in
`BROAD_EXCEPTION_NAMES`, which holds exactly four spellings: `BaseException`,
`Exception`, `builtins.BaseException`, and `builtins.Exception`. The evidence
string is `broad exception`. If the handler body is empty, or consists only of
`pass` statements, the evidence becomes `broad exception silently ignored`
instead. That is the only distinction the rule draws between one handler body
and another.

Several things follow from how narrow that match is, and they are worth stating
plainly because they are the difference between what the rule looks like it does
and what it does.

A tuple of exception types never fires, even when one of the members is broad.
`except (ValueError, Exception):` is a `ast.Tuple` node, the dotted-name reader
returns nothing for a tuple, and no incident is recorded. The same is true of
any handler type that is not a plain name or an attribute chain, for example a
name looked up out of a variable.

The name is matched literally, without alias resolution. A handler written as
`except Exception:` fires; the same handler reached through a local rebinding or
through an alias other than the `builtins.` prefix does not.

The rule does not distinguish a handler that re-raises from one that swallows.
`except Exception: raise` and `except Exception: log.warning(...)` and
`except Exception: return None` all record the same `broad exception` evidence.
The only body-shape check in the code is the `pass`-only test described above,
so a handler that logs and continues reads identically to one that recovers
deliberately. Nor does the rule care whether the exception is bound with `as`,
whether the handler is the last of several, or whether a narrower handler
precedes it.

Handlers inside a nested function, a nested class, or a lambda are not seen by
the enclosing function's visitor. It refuses to recurse into those nodes.

**What tunes it.** Not configurable. There is no threshold and no config key.
The set of matched names is the frozen `BROAD_EXCEPTION_NAMES` constant.

**Why it matters.** A handler that catches `Exception` catches the failure you
planned for and every failure you did not, which means a typo in the handled
block and a network timeout arrive at the same place and get the same response.
That collapse is usually invisible until the day the wrong one is silently
absorbed. The rule cannot tell whether the breadth was chosen, so what it asks
is whether the set of failures reaching this handler is one you can name. See
[failure as an argument](../philosophy/arguments-and-failure.md) for the
reasoning behind treating the failure path as part of a function's interface.

```python
# fires: handler type is a plain `Exception`, body is pass-only,
# so the evidence reads `broad exception silently ignored`
def load_settings(path):
    try:
        return read_toml(path)
    except Exception:
        pass

    return {}
```

```python
# does not fire: the handler names the failures it expects
def load_settings(path):
    try:
        return read_toml(path)
    except (OSError, TomlDecodeError):
        return {}
```

## HS021 lazy-import

| Field           | Value                                                                                           |
| --------------- | ----------------------------------------------------------------------------------------------- |
| Severity        | ADVISORY                                                                                        |
| Confidence      | 0.85                                                                                            |
| Weight          | 1.0                                                                                             |
| Tuned by        | Not configurable (no threshold or constant)                                                     |
| Review question | Is this hiding a cycle, an optional dependency, or a startup cost that belongs at module scope? |

**When it fires.** Any `import` or `from ... import` statement reached while
walking a function body records an incident, one per statement. Position within
the body does not matter: the first line of the function, inside an `if`, inside
a `try`, or inside a `with` all count the same. There is no notion of a
conditional or guarded import.

Only function bodies are walked, so module-level imports and imports in a class
body are never reported. The visitor also refuses to descend into a nested
`def`, `async def`, `class`, or `lambda`, so an import inside a closure is not
attributed to the enclosing function. Nested functions are not evaluated as
targets in their own right either, so such an import goes unreported entirely.

The evidence string is the module text, formatted from the statement itself.
For a plain `import`, it is the imported module names sorted alphabetically and
joined with `, `, so `import zlib, base64` yields `base64, zlib`. For a
`from ... import`, it is the module name alone without the imported symbols, so
`from json import loads` yields `json`. A relative import with no module part,
such as `from . import helpers`, yields `.`. The relative level is not included
in the evidence, so `from .parser import Node` yields `parser` with no leading
dot.

Importing the same module twice in one body records two incidents, and both
become findings.

**What tunes it.** Not configurable. There is no threshold, no allowlist, and no
named constant. Every deferred import in an evaluated function body is reported.

**Why it matters.** A deliberate lazy import is a legitimate technique. It
breaks an import cycle, defers an expensive module so that startup stays fast,
or keeps an optional dependency optional. It is also what an import looks like
when someone needed a name and added it in place without going back to the top
of the file. The rule cannot tell those apart. All it observes is that a module
is being pulled in at call time rather than at load time, and that the cost and
the failure mode of the import now belong to whoever calls this function. The
review question exists because the answer is yours to supply: if the import is
deliberate, a one-line comment naming the cycle or the cost converts the finding
into a documented decision. See
[state and effects](../philosophy/state-and-effects.md) for why load-time and
call-time work are treated differently.

```python
# fires: `import` reached inside the body, evidence reads `csv`
def export_rows(rows, destination):
    import csv

    writer = csv.writer(destination)
    writer.writerows(rows)
```

```python
# does not fire: the import is at module scope
import csv


def export_rows(rows, destination):
    writer = csv.writer(destination)
    writer.writerows(rows)
```

## Why these two are grouped

Both rules mark a point where a body stops being straight-line logic about its
own inputs and reaches outside itself.

HS005 marks a reach toward the failure path. The function is declaring that
something below it may fail and that it intends to absorb the result, which is a
claim about code it does not contain.

HS021 marks a reach toward the module system. The function is pulling in code at
call time, so the import graph now depends on which functions run rather than on
which modules load.

In both cases the shape is visible in the syntax while the intent is not, which
is why each rule ships a question instead of a fix. The evidence tells you where
to look. The judgement stays with the reviewer.
