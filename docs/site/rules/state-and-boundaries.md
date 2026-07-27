# State and boundaries

Four rules that ask who owns a piece of state, how long it lives, and how many
kinds of outside world one function reaches into. Every finding here is a review
lead, not a verdict: the scanner reads syntax, so it can point at a shape and ask
a question about it, but it cannot decide whether the shape is right for your
design. Background on the reasoning behind these rules lives in
[state and effects](../philosophy/state-and-effects.md) and
[testability](../philosophy/testability.md).

## HS004 shared-mutable-state

| Field           | Value                                                                             |
| --------------- | --------------------------------------------------------------------------------- |
| Severity        | WARNING                                                                           |
| Confidence      | 0.95                                                                              |
| Weight          | 3.0                                                                               |
| Tuned by        | Not configurable                                                                  |
| Review question | Is the lifetime intentional, who owns mutation, and can tests isolate this state? |

**When it fires.** The scanner walks two scopes: the statements directly in the
module body, and the statements directly in each class body. Function bodies and
nested statements are not scanned, so a mutable local inside a function is never
flagged. Within those two scopes it looks at `Assign` and `AnnAssign` statements
that have a value and whose target is a plain name, then asks whether the
assigned expression builds something mutable.

An expression counts as mutable in two cases. First, if it is one of six literal
forms: a dict display, a list display, a set display, a dict comprehension, a
list comprehension, or a set comprehension. Tuple and frozenset literals do not
count. Second, if it is a call whose function is a dotted name that resolves to
one of six constructors: `bytearray`, `dict`, `list`, `set`,
`collections.defaultdict`, `collections.deque`. Resolution uses the aliases
collected from the module's top level imports, and only the leading segment of
the dotted name is substituted. So `from collections import deque as ring` makes
`ring()` resolve to `collections.deque` and fire, while a local rebinding inside
a function does not participate. Names are not filtered by case, so an uppercase
module constant assigned a dict is flagged the same as a lowercase one.

**Why it matters.** A mutable object bound at module or class scope outlives
every call that touches it, and its contents at any moment depend on the order in
which unrelated code ran. That is the state most awkward to isolate in a test,
because each test either inherits what the last one left behind or has to reach
in and reset it. The finding does not say the binding is wrong: caches, registries
and interning tables are all legitimate. It says the lifetime is now a design
decision worth naming, along with which code is allowed to write to it.

Fires:

```python
CACHE = {}


class Registry:
    handlers = []
```

Does not fire:

```python
CACHE = ()


class Registry:
    handlers = frozenset()
```

## HS006 multiple-mutation-owners

| Field           | Value                                                                               |
| --------------- | ----------------------------------------------------------------------------------- |
| Severity        | WARNING                                                                             |
| Confidence      | 0.70                                                                                |
| Weight          | 3.0                                                                                 |
| Tuned by        | Not configurable                                                                    |
| Review question | Are mutation authority, transaction boundaries, and partial-failure behavior clear? |

**When it fires.** While walking one function body, the scanner attributes each
apparent mutation to an owner and fires once the count of distinct owners reaches
`MUTATION_OWNER_MINIMUM`, which is `3` in `const.py`. Nested functions, nested
classes and lambdas are not descended into, so the count belongs to one body.

An owner is the root name of the mutated expression, and only three kinds of root
qualify: `self`, a name declared as a parameter of the enclosing function, or a
name bound at module level. A purely local variable is never an owner, which is
what keeps ordinary scratch work out of the count. Subscripts and attribute
chains resolve to their root, so `journal.entries[0]` and `journal.total` both
count as the single owner `journal`.

Two kinds of statement register a mutation. Assignment and deletion, meaning
`Assign`, `AnnAssign`, `AugAssign` and `Delete` targets. And method calls whose
attribute name appears in the mutating-method vocabulary, provided the receiver
resolves to an owner. That vocabulary is derived at runtime in `factories.py`
rather than hardcoded: for each mutable type it takes the public callables the
type has and its immutable counterpart lacks, comparing `bytearray` against
`bytes`, `dict` against a mapping proxy, `list` against `tuple`, `set` against
`frozenset`, and `deque` against `tuple`, then removes `copy` and `fromkeys`.
The result is names like `append`, `extend`, `insert`, `pop`, `remove`, `sort`,
`update`, `setdefault`, `add`, `discard`, `clear` and the deque-specific
`appendleft`, `popleft`, `rotate`. Because the match is on the method name alone,
a call to `.update()` on an object that is not a dict still registers.

**Why it matters.** A function writing to three independent owners is the point
where partial failure becomes hard to reason about: if the third write raises,
the first two have already happened, and nothing in the signature tells a caller
that. It is also the shape that makes a function hard to test in pieces, since
each owner has to be constructed and inspected separately. The review question
worth answering is which of the three owners this function actually has authority
over, and whether the others belong behind a call it makes rather than a write it
performs.

Fires:

```python
class Ledger:
    def post(self, entry, journal, audit):
        self.balance += entry.amount
        journal.append(entry)
        audit.add(entry.id)
```

Does not fire:

```python
class Ledger:
    def post(self, entry, journal):
        posted = [*journal, entry]
        self.balance += entry.amount
        return posted, entry.id
```

## HS007 mixed-boundaries

| Field           | Value                                                                                   |
| --------------- | --------------------------------------------------------------------------------------- |
| Severity        | WARNING                                                                                 |
| Confidence      | 0.65                                                                                    |
| Weight          | 3.0                                                                                     |
| Tuned by        | Not configurable                                                                        |
| Review question | Should one function coordinate this many standard-library boundary categories directly? |

**When it fires.** As it walks a function body the scanner resolves every dotted
attribute reference and every call target through the module's import aliases,
then checks the resolved name against four categories of standard-library module
listed in `BOUNDARY_MODULES`:

| Category     | Modules                                                        |
| ------------ | -------------------------------------------------------------- |
| `database`   | `sqlite3`                                                      |
| `filesystem` | `os`, `pathlib`, `shutil`, `tempfile`                          |
| `network`    | `ftplib`, `http.client`, `smtplib`, `socket`, `urllib.request` |
| `process`    | `multiprocessing`, `subprocess`                                |

A name matches if it equals a listed module or begins with that module plus a
dot, so `pathlib.Path.write_text` lands in `filesystem`. The rule fires when the
number of distinct categories touched reaches `BOUNDARY_MINIMUM`, which is `3` in
`const.py`. Since there are only four categories, three is close to the ceiling.
The list is deliberately limited to the standard library, so a database reached
through a third-party driver contributes nothing.

This is a syntactic reach, not an observation of behavior. A resolved reference
to `subprocess.run` is evidence that the function may start a process, and it
sits on a line the report will cite, but the scanner never runs the code and
cannot say whether the call is taken, guarded, or dead. Read the finding as
"three kinds of outside world are named in one body", not as proof that three
kinds of side effect occur.

**Why it matters.** Each category needs different failure handling, different
test doubles and different permissions to exercise. A function that names three
of them directly usually has no seam where a test can substitute one, so testing
any part of it means having all three available. Splitting along those lines
tends to be the cheapest way to make the workflow testable without changing what
it does.

Fires:

```python
import os
import socket
import subprocess


def deploy(path, command):
    os.makedirs(path)
    host = socket.gethostname()
    subprocess.run(command, check=True)
    return host
```

Does not fire:

```python
import os


def deploy(path, host, runner):
    os.makedirs(path)
    return runner.reload(host)
```

## HS017 long-file

| Field           | Value                                                                                         |
| --------------- | --------------------------------------------------------------------------------------------- |
| Severity        | WARNING                                                                                       |
| Confidence      | 0.60                                                                                          |
| Weight          | 3.0                                                                                           |
| Tuned by        | `thresholds.modules.max_lines`, default `500`                                                 |
| Review question | Does this file hold one subject, or have several modules been accumulated into one namespace? |

**When it fires.** This is the one module-level rule of the four, and it is
emitted from `module_scale_findings` in `analysis/python_ast.py` rather than from
the ruleset evaluator that produces the other three. It compares the total number
of source lines in the file, taken by splitting the source text, against the
configured module threshold, and reports when the count is strictly greater.
Every physical line counts, including blanks, comments and the module docstring.
The finding is attached to the symbol `<module>` and spans line 1 to the last
line, and the configured threshold is included in the evidence so a report is
readable without the config file next to it.

**What tunes it.** The `[tool.humansays.thresholds.modules]` table:

```toml
[tool.humansays.thresholds.modules]
max_lines = 500
```

The CLI flag `--max-file-lines` sets the same value. It must be at least `1`.

**Why it matters.** File length is the weakest of the four signals, which is why
its confidence is the lowest in this group. A long file is not itself a problem;
a long file that has quietly become three subjects sharing one namespace is,
because nothing in the import graph records that the three parts are separate and
nothing stops them growing into each other. The threshold exists to prompt that
check at a size where the answer is still easy to see.

**Example.** A worked fixture is impractical here, since the smallest file that
fires under the default configuration is 501 lines. To see it, either point the
scanner at any file over 500 lines, or lower the threshold in a scratch config
and run against a small file: with `max_lines = 5`, a six line file reports one
`long-file` finding at `<module>`, with evidence reading
`configured threshold: 5`.
