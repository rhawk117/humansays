# Class design

Five rules read the shape of a class: how its methods share state, how much
state it owns, whether the attribute names hide a smaller object, whether the
class is a namespace for functions, and how many parents it has. Every finding
is a review lead, a question to answer during review, not a verdict about the
code. Version `0.1.0a1`. These rules are evaluated for classes defined at
module level, in `src/humansays/analysis/rules.py`.

## HS008 low-class-cohesion

| Field           | Value                                                                                                 |
| --------------- | ----------------------------------------------------------------------------------------------------- |
| Severity        | ADVISORY                                                                                              |
| Confidence      | `0.65`                                                                                                |
| Weight          | `1.0`                                                                                                 |
| Tuned by        | Not configurable (`COHESION_METHOD_MINIMUM`, `COHESION_FIELD_MINIMUM`)                                |
| Review question | Do these clusters represent independently changing responsibilities that should have separate owners? |

**When it fires.** For every method, humansays collects the `self` attributes it
reads and the ones it writes, then subtracts any name that is also a method of
the class or is called as `self.name(...)`, so bound methods reached through
`self` do not count as fields. A method is eligible for the cohesion check when
it is not `__init__`, is not a trivial accessor (a single-statement body that
only returns or only assigns a `self` attribute), and touches at least one
field. The rule then requires at least `COHESION_METHOD_MINIMUM` eligible
methods and at least `COHESION_FIELD_MINIMUM` distinct fields across them,
which are 4 and 3. Both gates must pass before anything is computed further.

Cohesion itself is a connected-components walk: two methods are joined when
they share at least one field, and the relation is transitive, so a third
method sharing a field with either pulls into the same component. The finding
is recorded when the walk produces two or more components, and the evidence
lists each component's methods with the fields they use.

**What tunes it.** Nothing in `[tool.humansays]`. Both minimums are fixed
constants in `src/humansays/const.py`: `COHESION_METHOD_MINIMUM = 4` and
`COHESION_FIELD_MINIMUM = 3`.

**Why it matters.** Disconnected field clusters mean the class has two groups of
methods that never touch the same data. Each group can usually be moved, tested
and changed without the other, which is the working definition of a separate
responsibility. See [structure](../philosophy/structure.md).

Fires: two components, `{add_row, summary}` over `rows`/`total` and
`{connect, send}` over `smtp_host`/`smtp_port`.

```python
class Report:
    def __init__(self, host, port):
        self.rows = []
        self.total = 0
        self.smtp_host = host
        self.smtp_port = port

    def add_row(self, row):
        self.rows.append(row)
        self.total += 1

    def summary(self):
        return f'{self.total} rows recorded'

    def connect(self):
        return open_session(self.smtp_host, self.smtp_port)

    def send(self, body):
        return self.connect().deliver(self.smtp_host, body)
```

Does not fire: delivery moved out, so every remaining method reaches the same
field cluster and the walk finds one component.

```python
class Report:
    def __init__(self, mailer):
        self.rows = []
        self.total = 0
        self.mailer = mailer

    def add_row(self, row):
        self.rows.append(row)
        self.total += 1

    def summary(self):
        return f'{self.total} rows recorded'

    def publish(self):
        return self.mailer.deliver(self.summary(), self.rows)
```

## HS012 many-class-attributes

| Field           | Value                                                                               |
| --------------- | ----------------------------------------------------------------------------------- |
| Severity        | ADVISORY                                                                            |
| Confidence      | `0.72`                                                                              |
| Weight          | `1.0`                                                                               |
| Tuned by        | `thresholds.classes.max_attributes` (default `6`)                                   |
| Review question | Do subsets of this state have separate invariants, lifetimes, or reasons to change? |

**When it fires.** The rule counts the class state surface, which is the union
of two sets. The first is what the class body declares:

- Every string entry in a `__slots__` assignment.
- Every annotated assignment whose target is a plain name, unless the
    annotation is `ClassVar` or `typing.ClassVar` (the `CLASS_VAR_NAMES` set).
- Every plain assignment to a name target, unless the name is all uppercase
    (treated as a constant) or the assigned value is a bare name matching a
    method defined in the same class body (a method alias such as
    `render = to_html`).

The second is every attribute written through `self` anywhere in the class's
methods, so `self.x = ...` in `__init__` or in any other method counts even
when nothing is declared in the class body. Deletions through `self` count as
writes too. The finding is recorded when the size of that union is strictly
greater than `max_attributes`, and the evidence lists the attribute names
sorted.

**What tunes it.** `max_attributes` under `[tool.humansays.thresholds.classes]`,
default `6`. Seven attributes fire at the default.

**Why it matters.** Each attribute is one more thing a reader has to hold while
judging any method, and one more thing a test has to set up. When subsets of
the state have different lifetimes or invariants, they usually want to be
separate objects with separate construction rules. See
[state and effects](../philosophy/state-and-effects.md).

Fires: seven attributes on the state surface, five declared and two written
only through `self`.

```python
class Job:
    name: str
    queue: str
    retries: int = 0
    timeout: float = 30.0
    payload: dict | None = None

    def start(self, clock):
        self.started_at = clock.now()
        self.worker_id = clock.worker
```

Does not fire: six attributes. `MAX_RETRIES` is uppercase, `LOGGER` is
uppercase, `kind` is annotated `ClassVar`, and `run = start` is a method alias,
so none of the four is counted.

```python
from typing import ClassVar


class Job:
    MAX_RETRIES = 5
    LOGGER = get_logger(__name__)
    kind: ClassVar[str] = 'batch'

    name: str
    queue: str
    retries: int = 0
    timeout: float = 30.0
    payload: dict | None = None

    def start(self, clock):
        self.started_at = clock.now()

    run = start
```

## HS013 attribute-prefix-cluster

| Field           | Value                                                                                                                |
| --------------- | -------------------------------------------------------------------------------------------------------------------- |
| Severity        | WARNING                                                                                                              |
| Confidence      | `0.84`                                                                                                               |
| Weight          | `3.0`                                                                                                                |
| Tuned by        | `thresholds.classes.max_attributes` (default `6`) gates it; the cluster size is not configurable (`CLUSTER_MINIMUM`) |
| Review question | Does each prefix identify a cohesive value object or component hidden inside this class?                             |

**When it fires.** HS013 is evaluated only after HS012 has already fired for the
same class, so a class at or under `max_attributes` is never checked for
clusters. Given the same attribute set, each name is stripped of leading
underscores and split at its first remaining underscore. A name with no
underscore after stripping contributes nothing. The part before that underscore
is the prefix, and it is discarded when it appears in `NON_STRUCTURAL_PREFIXES`:
`can`, `did`, `does`, `has`, `is`, `self`, `should`, `was`, `will`. Names are
grouped by surviving prefix, and a group becomes a cluster only when it holds at
least `CLUSTER_MINIMUM` distinct names, which is 3. The finding is recorded when
at least one cluster survives, and the evidence names each prefix with its
members.

**What tunes it.** There is no cluster-specific key. The gate is
`max_attributes` under `[tool.humansays.thresholds.classes]`, default `6`. The
required group size is the fixed constant `CLUSTER_MINIMUM = 3` in
`src/humansays/const.py`, and the excluded prefixes are the fixed
`NON_STRUCTURAL_PREFIXES` set in the same file.

**Why it matters.** A repeated prefix is a name the author already chose for a
grouping that has no type yet. Three `smtp_*` fields are an SMTP configuration
that has been flattened into the enclosing class, and giving it a type moves its
invariants and its construction into one place. See
[structure](../philosophy/structure.md).

Fires: eight attributes, and `smtp_host`, `smtp_port`, `smtp_user` form one
cluster of three.

```python
class Mailer:
    def __init__(self, config):
        self.smtp_host = config.host
        self.smtp_port = config.port
        self.smtp_user = config.user
        self.template_dir = config.templates
        self.retries = 3
        self.timeout = 30.0
        self.queue = []
        self.sent = 0
```

Does not fire for HS013: nine attributes, so HS012 reports, but no prefix
reaches three names. `is_ready` and `has_queue` are stripped as non-structural
prefixes, and `smtp` now holds two names.

```python
class Mailer:
    def __init__(self, config):
        self.smtp = SmtpEndpoint(config.host, config.port, config.user)
        self.smtp_user = config.user
        self.template_dir = config.templates
        self.retries = 3
        self.timeout = 30.0
        self.queue = []
        self.sent = 0
        self.is_ready = False
        self.has_queue = False
```

## HS015 static-method

| Field           | Value                                                                                                             |
| --------------- | ----------------------------------------------------------------------------------------------------------------- |
| Severity        | WARNING                                                                                                           |
| Confidence      | `0.99`                                                                                                            |
| Weight          | `3.0`                                                                                                             |
| Tuned by        | Not configurable (`STATIC_DECORATOR`)                                                                             |
| Review question | The method can reach neither instance nor class state, so what does class scope buy over a module-level function? |

**When it fires.** Every function defined directly in a class body is checked
for its decorator names, resolved through their dotted form, with any call form
such as `@decorator(...)` reduced to the decorated name. The finding is
recorded when one of those names is exactly `staticmethod`. Nothing about the
body matters, and there is no threshold, so a single `@staticmethod` reports.
The high confidence reflects that the condition is a syntactic fact rather than
a heuristic.

**What tunes it.** Nothing in `[tool.humansays]`. The matched name is the fixed
constant `STATIC_DECORATOR = 'staticmethod'` in
`src/humansays/analysis/python_ast.py`.

**Why it matters.** A static method receives neither `self` nor `cls`, so the
class is acting as a namespace rather than as a type. Moving the function to
module level makes it importable and callable on its own, which usually makes
it easier to test in isolation. See
[testability](../philosophy/testability.md).

Fires.

```python
class Invoice:
    def __init__(self, lines):
        self.lines = lines

    @staticmethod
    def format_currency(amount):
        return f'${amount:,.2f}'

    def render(self):
        return [Invoice.format_currency(line) for line in self.lines]
```

Does not fire: the same function at module level.

```python
def format_currency(amount):
    return f'${amount:,.2f}'


class Invoice:
    def __init__(self, lines):
        self.lines = lines

    def render(self):
        return [format_currency(line) for line in self.lines]
```

## HS018 many-base-classes

| Field           | Value                                                                                           |
| --------------- | ----------------------------------------------------------------------------------------------- |
| Severity        | WARNING                                                                                         |
| Confidence      | `0.78`                                                                                          |
| Weight          | `3.0`                                                                                           |
| Tuned by        | `thresholds.classes.max_base_classes` (default `1`)                                             |
| Review question | Is this composition, mixin layering, or an inheritance chain that hides the real collaborators? |

**When it fires.** The rule reads the base expressions listed in the `class`
statement, rendering each as its dotted name where it has one and as a source
snippet otherwise, so `pkg.mod.Base` and a subscripted generic base both count
as one entry. Keyword arguments in the class header, such as `metaclass=`, are
not bases and are not counted. The finding is recorded when the number of base
expressions is strictly greater than `max_base_classes`, and the evidence lists
the rendered base names.

**What tunes it.** `max_base_classes` under
`[tool.humansays.thresholds.classes]`, default `1`. Two bases fire at the
default. Setting it to `0` reports any subclass at all.

**Why it matters.** With more than one parent, the method resolution order
decides which implementation runs, and that order is a property of the whole
inheritance graph rather than of the file in front of the reader. Holding a
collaborator as an attribute keeps the dispatch visible at the call site. See
[structure](../philosophy/structure.md).

Fires: two bases.

```python
class Report(JsonSerializable, TimestampMixin):
    def __init__(self, rows):
        self.rows = rows
```

Does not fire: one base, with the second capability held as a collaborator.

```python
class Report(JsonSerializable):
    def __init__(self, rows, clock):
        self.rows = rows
        self.clock = clock

    def stamped(self):
        return self.clock.now()
```
