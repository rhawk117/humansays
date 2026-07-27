# Function shape

These eight rules read the shape of a single function: how many arguments it
declares, how deep its control flow runs, how long it is, and whether it
validates its own inputs. Each one raises a review lead, not a verdict. The
tool reports structure it can see in the syntax tree, and the review question
attached to each finding is the thing a human still has to answer.

## HS001 many-arguments

| Field           | Value                                                                                        |
| --------------- | -------------------------------------------------------------------------------------------- |
| Severity        | WARNING                                                                                      |
| Confidence      | 0.80                                                                                         |
| Weight          | 3.0                                                                                          |
| Tuned by        | `thresholds.functions.max_arguments`, default `3`                                            |
| Review question | Do these values form a request object, reusable configuration, or multiple responsibilities? |

**When it fires.** The count of operation parameters is strictly greater than
`max_arguments`. Operation parameters are every declared argument: positional
only, positional or keyword, keyword only, plus `*args` and `**kwargs` if
present, each counted as one. Any parameter literally named `self` or `cls` is
excluded, wherever it appears in the signature. Defaults do not reduce the
count, so a function with three required arguments and two optional ones counts
five. With the default threshold of `3`, four operation parameters is the
smallest signature that fires.

**What tunes it.** `thresholds.functions.max_arguments`, default `3`. In
`pyproject.toml` that is `[tool.humansays.thresholds.functions]`, and the CLI
flag is `--max-arguments`.

**Why it matters.** A long parameter list is usually several smaller ideas that
have not been given a name yet, and callers have to reconstruct the grouping
every time they call. Once a signature passes four or five values, argument
order becomes something the reader has to remember rather than something the
types enforce. See [arguments and failure](../philosophy/arguments-and-failure.md).

```python
# fires: four operation parameters, self excluded
def send(self, recipient, subject, body, retries):
    ...
```

```python
# does not fire: three operation parameters
def send(self, recipient, message, retries):
    ...
```

## HS002 boolean-modes

| Field           | Value                                                                                       |
| --------------- | ------------------------------------------------------------------------------------------- |
| Severity        | ADVISORY                                                                                    |
| Confidence      | 0.82                                                                                        |
| Weight          | 1.0                                                                                         |
| Tuned by        | Not configurable                                                                            |
| Review question | Would keyword-only arguments, an enum, or separate operations communicate the modes better? |

**When it fires.** At least one operation parameter is boolean, and the
function is not an exempt setter. A parameter counts as boolean when its
annotation resolves to `bool` or `builtins.bool`, or when its default value is
the constant `True` or `False`. Parameters named `self` or `cls` are excluded.
There is no count threshold: one boolean parameter is enough. The single
exemption is a function whose name starts with `set_` and which declares
exactly one operation parameter, so `set_enabled(self, enabled: bool)` stays
quiet.

**What tunes it.** Not configurable. The names recognized as boolean
annotations are fixed in the `BOOL_NAMES` constant in `src/humansays/const.py`,
and the `self` and `cls` exclusion comes from `IMPLICIT_PARAMETERS` in the same
file.

**Why it matters.** A boolean argument at a call site carries no name, so
`render(data, True)` tells the reader nothing about what was switched on. A
flag that selects behavior usually means the function contains two operations
sharing a body, and splitting them or naming the modes with an enum makes the
choice visible at the call site. See [contracts](../philosophy/contracts.md).

```python
# fires: boolean parameter selects a mode
def render(data, pretty=False):
    ...
```

```python
# does not fire: the mode is a named value
def render(data, style: Style):
    ...
```

## HS003 deep-nesting

| Field           | Value                                                                                      |
| --------------- | ------------------------------------------------------------------------------------------ |
| Severity        | WARNING                                                                                    |
| Confidence      | 0.76                                                                                       |
| Weight          | 3.0                                                                                        |
| Tuned by        | `thresholds.functions.max_nesting`, default `3`, plus `class_nesting_bonus`, default `1`   |
| Review question | Would guard clauses, a state model, or one meaningful extraction clarify the control flow? |

**When it fires.** The deepest nesting reached in the body is strictly greater
than the limit. For a module-level function the limit is `max_nesting`. For a
method the limit is `max_nesting + class_nesting_bonus`, so with the defaults a
plain function fires above depth `3` and a method fires above depth `4`.

Depth increases for the body of an `if`, a `for` or `async for`, a `while`, a
`try` in all its parts, a `with` or `async with`, and each `case` of a `match`.
The test or subject expression of a compound statement is visited at the
enclosing depth, so a condition does not add a level by itself. An `elif` chain
stays flat: the `else` branch of an `if` counts as nested only when it is not a
single following `if`. Nested function definitions, nested classes, and lambdas
are not descended into, so their inner depth belongs to their own analysis
rather than to the enclosing function.

**What tunes it.** `thresholds.functions.max_nesting`, default `3`, and
`thresholds.functions.class_nesting_bonus`, default `1`. The CLI flags are
`--max-nesting` and `--class-nesting-bonus`.

**Why it matters.** Nesting depth is a direct measure of how much state the
reader has to hold to understand the innermost line. At depth four, the
conditions guarding a statement are spread across four separate places on the
screen. Inverting the conditions into early returns usually removes most of the
depth without changing the logic. See [structure](../philosophy/structure.md).

```python
# fires: depth 4 in a module-level function
def settle(orders):
    for order in orders:
        if order.active:
            if order.total:
                if order.paid:
                    record(order)
```

```python
# does not fire: guard clauses flatten the same logic to depth 2
def settle(orders):
    for order in orders:
        if not (order.active and order.total and order.paid):
            continue

        record(order)
```

## HS009 long-function

| Field           | Value                                                                                    |
| --------------- | ---------------------------------------------------------------------------------------- |
| Severity        | ADVISORY                                                                                 |
| Confidence      | 0.55                                                                                     |
| Weight          | 1.0                                                                                      |
| Tuned by        | `thresholds.functions.max_lines`, default `50`                                           |
| Review question | Is the function cohesive, or does it mix workflow, decisions, and lower-level mechanics? |

**When it fires.** The physical span of the definition is strictly greater than
`max_lines`. The span is `end_line - start_line + 1`, measured from the `def`
line to the last line of the body. Decorators sit above the `def` line and are
not counted. Everything inside the span is counted, including blank lines,
comments, the docstring, and any nested definitions. With the default of `50`,
a definition spanning 51 lines is the shortest that fires.

Confidence is the lowest in this group, at `0.55`, because length alone is weak
evidence: a long dispatch table and a long tangle of logic look the same to a
line count.

**What tunes it.** `thresholds.functions.max_lines`, default `50`. The CLI flag
is `--max-function-lines`.

**Why it matters.** A function that does not fit on a screen forces the reader
to scroll while holding earlier lines in memory, and the parts that could be
named separately stay anonymous. The useful question is not whether the
function is too long but whether it is doing one thing at one level of
abstraction. See [structure](../philosophy/structure.md).

```python
# fires: span from the def line exceeds 50 lines
def build_report(records):
    header = compose_header(records)
    # ... 55 more lines of body ...
    return header
```

```python
# does not fire: the same work split across named steps
def build_report(records):
    header = compose_header(records)
    body = compose_body(records)
    return join(header, body)
```

## HS014 validated-argument-bundle

| Field           | Value                                                                                           |
| --------------- | ----------------------------------------------------------------------------------------------- |
| Severity        | WARNING                                                                                         |
| Confidence      | 0.88                                                                                            |
| Weight          | 3.0                                                                                             |
| Tuned by        | `thresholds.functions.max_arguments`, default `3`                                               |
| Review question | Should these arguments and their validation become one request, value, or configuration object? |

**When it fires.** This rule is checked only after HS001 has fired, so the
function must already declare more operation parameters than `max_arguments`.
Given that, it fires when at least one of those operation parameters is
validated inside the body.

A parameter counts as validated when the body contains either an `assert` whose
test expression mentions the parameter name, or an `if` statement whose test
mentions the parameter name and whose body contains a `raise` anywhere within
it. Only names referenced directly in the test count; a parameter checked
indirectly through a helper call does not register. The evidence attached to
the finding names each validated parameter and the line where the check
appears.

**What tunes it.** There is no separate key. The rule inherits
`thresholds.functions.max_arguments`, default `3`, through its dependency on
HS001, and the validation detection itself has no threshold.

**Why it matters.** When a function both accepts a wide bundle of values and
checks their consistency, the bundle already has invariants, which means it
already has an identity that no type currently carries. Moving the values and
their checks into one object validates once at construction instead of at every
call site. See [arguments and failure](../philosophy/arguments-and-failure.md).

```python
# fires: four operation parameters, two of them guarded in the body
def schedule(start, end, retries, channel):
    if start > end:
        raise ValueError('start must precede end')

    assert retries >= 0
    return dispatch(start, end, retries, channel)
```

```python
# does not fire: the bundle and its invariants live in one object
def schedule(window: Window, policy: RetryPolicy):
    return dispatch(window, policy)
```

## HS016 lambda-expression

| Field           | Value                                                                                          |
| --------------- | ---------------------------------------------------------------------------------------------- |
| Severity        | WARNING                                                                                        |
| Confidence      | 0.99                                                                                           |
| Weight          | 3.0                                                                                            |
| Tuned by        | Not configurable                                                                               |
| Review question | What would this expression be named, and would a named function make it testable and reusable? |

**When it fires.** Every `lambda` expression in the module fires, once each.
The rule walks the whole tree rather than one function body, so lambdas in
default arguments, class bodies, comprehensions, and decorator arguments are
all found. There is no threshold and no exemption for short lambdas or for
`key=` callbacks. The finding is attributed to the innermost scope containing
the lambda's line, which is the enclosing function or method when there is one
and `<module>` otherwise. Confidence is `0.99` because the detection is purely
syntactic: either the token is there or it is not.

**What tunes it.** Not configurable. The only constant involved is
`UNPARSE_LIMIT` in `src/humansays/const.py`, which caps the unparsed source
snippet quoted as evidence at 80 characters, and has no effect on whether the
rule fires.

**Why it matters.** A lambda cannot be imported, so it cannot be tested on its
own or reused from anywhere else, and the stack trace it appears in shows
`<lambda>` rather than a name. Naming the expression usually costs one line and
answers the reader's question about what the callback is for. See
[testability](../philosophy/testability.md).

```python
# fires: anonymous callback
active = sorted(users, key=lambda user: user.last_seen)
```

```python
# does not fire: the same expression, named and importable
def last_seen(user):
    return user.last_seen


active = sorted(users, key=last_seen)
```

## HS019 many-branches

| Field           | Value                                                                                                |
| --------------- | ---------------------------------------------------------------------------------------------------- |
| Severity        | WARNING                                                                                              |
| Confidence      | 0.74                                                                                                 |
| Weight          | 3.0                                                                                                  |
| Tuned by        | `thresholds.functions.max_branches`, default `5`                                                     |
| Review question | Do these conditionals encode one decision that belongs in a table, mapping, or polymorphic dispatch? |

**When it fires.** The branch count for the body is strictly greater than
`max_branches`. The counter increments once for every `if` statement reached in
the body, and because an `elif` is represented as a nested `if`, each `elif`
adds one as well. A plain `else` adds nothing. Nested `if` statements count
toward the same total as top-level ones.

Loops, `try` blocks, `with` blocks, `match` cases, boolean operators, and
conditional expressions such as `a if b else c` are not counted. Nested
functions, nested classes, and lambdas are not descended into. With the default
of `5`, six `if` or `elif` statements is the smallest body that fires.

**What tunes it.** `thresholds.functions.max_branches`, default `5`. The CLI
flag is `--max-branches`.

**Why it matters.** A run of conditionals over the same value is usually one
decision written out longhand, and each new case means editing the function
again. When the branches map an input to a behavior, a dictionary or a
dispatched method turns the decision into data that can be extended and tested
without touching control flow. See [structure](../philosophy/structure.md).

```python
# fires: six if/elif statements
def rate(kind):
    if kind == 'basic':
        return 1
    elif kind == 'plus':
        return 2
    elif kind == 'pro':
        return 3
    elif kind == 'team':
        return 4
    elif kind == 'scale':
        return 5
    elif kind == 'enterprise':
        return 6
    return 0
```

```python
# does not fire: the decision is a table
RATES = {'basic': 1, 'plus': 2, 'pro': 3, 'team': 4, 'scale': 5, 'enterprise': 6}


def rate(kind):
    return RATES.get(kind, 0)
```

## HS022 dense-function

| Field           | Value                                                                      |
| --------------- | -------------------------------------------------------------------------- |
| Severity        | WARNING                                                                    |
| Confidence      | 0.72                                                                       |
| Weight          | 3.0                                                                        |
| Tuned by        | `thresholds.functions.max_code_lines`, default `65`                        |
| Review question | How many distinct steps are in here, and which of them has a name already? |

**When it fires.** The count of executable lines in the definition is strictly
greater than `max_code_lines`. Counting runs over the same span as HS009, from
the `def` line to the last body line, but skips three kinds of line: blank
lines, lines whose first non-whitespace character is `#`, and every line of the
docstring. The signature lines themselves are counted, and so are nested
definitions inside the function. With the default of `65`, sixty six counted
lines fires.

HS009 and HS022 measure the same region differently and can both fire on one
function. Because counted lines are a subset of the span, a body with more than
`65` counted lines necessarily spans more than `50` physical lines, so under
the shipped defaults HS022 never fires without HS009 also firing. Raising
`max_lines` above `max_code_lines` separates them.

**What tunes it.** `thresholds.functions.max_code_lines`, default `65`. The CLI
flag is `--max-code-lines`.

**Why it matters.** Stripping blanks, comments, and the docstring measures the
work rather than the presentation, so a function cannot lower the number by
deleting the whitespace that made it readable. Density counted this way is a
better proxy than raw length for how many distinct steps the reader has to
follow. See [structure](../philosophy/structure.md).

```python
# fires: 70 counted lines of code between the signature and the last line
def reconcile(ledger, statements):
    """Blank lines and this docstring are not counted."""
    opened = ledger.open()
    # ... 68 more executable lines ...
    return opened
```

```python
# does not fire: the steps are extracted and named
def reconcile(ledger, statements):
    opened = ledger.open()
    matched = match_entries(opened, statements)
    return close(ledger, matched)
```
