# Keeping and extracting

Where a boundary falls decides how expensive the next change is. Code split too
finely spreads one operation across a dozen names, and reading it means holding
the whole call chain in your head before you can judge any single link. Code
kept together too long collects unrelated reasons to change, so a request that
touches one of them forces you to reason about all of them. Both failures look
the same from the outside: a small edit that cannot be made confidently in one
place. The criteria below are about choosing which shape a given piece of code
should have, and they are the reason several of the shipped rules exist.

## 7. Decide Whether to Keep Code Together

Keep code together when:

* It implements one short, linear operation.
* The steps share the same inputs and local state.
* The steps make sense only as part of that operation.
* Extraction would create vague or redundant names.
* The extracted code would not be tested, reused, or changed independently.
* The implementation is already clearer than an extracted name.

Do not split straightforward code into narration:

```python
value = strip_username(value)
value = lowercase_username(value)
validate_username_not_empty(value)
validate_username_length(value)
```

If the whole operation is clearer inline:

```python
normalized = value.strip().casefold()

if not normalized:
    raise ValueError("Username cannot be empty")

if len(normalized) > 32:
    raise ValueError("Username cannot exceed 32 characters")
```

## 8. Decide Whether to Extract

Extract code when separation provides at least one concrete benefit:

* Introduces a meaningful domain name
* Establishes clear state ownership
* Creates an explicit side-effect boundary
* Hides a lower abstraction level
* Supports focused independent testing
* Supports independent replacement
* Manages a separate lifecycle
* Captures behavior reused in multiple places
* Isolates an independent reason to change

### Semantic-compression test

An extraction is valuable when its name communicates more than its implementation details.

```python
if lockout_policy.should_lock(user):
    ...
```

This hides a meaningful business rule. A helper that merely renames one obvious line adds navigation without abstraction.

### Abstraction-level test

A function should generally operate at one abstraction level. Application workflows should not contain raw SQL, HTTP payload construction, and domain decisions in the same body.

```python
def register_user(command: RegisterUserCommand) -> User:
    email = EmailAddress(command.email)

    if users.exists_by_email(email):
        raise EmailAlreadyRegistered(email)

    identity = identities.create_user(email)
    user = User.register(identity.id, email)
    users.add(user)

    return user
```

The workflow remains together while SQL and HTTP mechanics remain behind repositories and adapters.

## 10. Criteria for Extracting a Class

Extract a class when behavior needs a stable owner.

### Strong reasons

* State must survive between calls.
* Several operations act on the same private state.
* Dependencies or configuration are established once and reused.
* Construction must enforce invariants.
* The object has meaningful identity.
* Multiple implementations are intentionally interchangeable.
* A resource requires acquisition and cleanup.
* Related functions collectively form one cohesive abstraction.

### Example: state ownership

These functions reveal a missing state-owning object:

```python
def register_check(
    checks: dict[str, type[Check]],
    check_type: type[Check],
) -> None:
    ...


def resolve_check(
    checks: dict[str, type[Check]],
    name: str,
) -> type[Check]:
    ...
```

Extract:

```python
class CheckRegistry:
    def __init__(self) -> None:
        self._checks: dict[str, type[Check]] = {}

    def register(self, check_type: type[Check]) -> None:
        ...

    def resolve(self, name: str) -> type[Check]:
        ...
```

### Do not extract a class solely because

* A function is longer than expected.
* Several functions are loosely related.
* The codebase uses object-oriented programming.
* The signature has too many arguments.
* Polymorphism might be useful someday.
* The class would contain one stateless method.
* The proposed name is `Helper`, `Utils`, or `Manager`.

Keep stateless behavior as a function:

```python
def normalize_email(value: str) -> str:
    return value.strip().casefold()
```

Do not add ceremony:

```python
class EmailNormalizer:
    def normalize(self, value: str) -> str:
        return value.strip().casefold()
```

## 11. Class Cohesion Criteria

A good class should:

* Have one dominant responsibility.
* Own the state its methods mutate.
* Have a small, cohesive public API.
* Establish valid state in its constructor.
* Keep dependencies explicit.
* Avoid leaking mutable internals.
* Preserve the semantic contract of its base class.
* Be named after a domain concept or operation.

### Warning signals

| Signal                                   | Review question                                        |
| ---------------------------------------- | ------------------------------------------------------ |
| More than 5 constructor dependencies     | Does the class coordinate too many responsibilities?   |
| More than 7 to 10 public methods         | Does the API serve unrelated callers?                  |
| Many private helpers                     | Are several components hidden inside one class?        |
| Generic `Manager` or `Service` name      | What specific capability does it own?                  |
| Mutable `ClassVar`                       | Is this process-global state disguised as class state? |
| Several setup methods after construction | Can invalid intermediate states be removed?            |
| Networking or SQL inside an entity       | Has an infrastructure boundary leaked into the domain? |

## What enforces this

Eight shipped rules put a location on the page against criteria from this page.
None of them decides whether the criterion is met. Each one marks a place where
the question is worth asking.

Section 8, deciding whether to extract:

* [HS009 `long-function`](../rules/function-shape.md#hs009-long-function) and
  [HS022 `dense-function`](../rules/function-shape.md#hs022-dense-function)
  report a function whose span or executable-line count exceeds the configured
  limit. Size is not the criterion, but it is where "does this mix workflow,
  decisions, and mechanics" gets asked.
* [HS003 `deep-nesting`](../rules/function-shape.md#hs003-deep-nesting) reports
  control flow nested past the limit, which is one of the shapes a missing
  extraction takes.
* [HS007 `mixed-boundaries`](../rules/state-and-boundaries.md#hs007-mixed-boundaries)
  reports a function that touches several categories of standard-library
  boundary directly. This is the abstraction-level test with a threshold on it.

Section 10, extracting a class:

* [HS013 `attribute-prefix-cluster`](../rules/class-design.md#hs013-attribute-prefix-cluster)
  reports groups of attributes sharing a name prefix, the shape the
  state-ownership example describes.
* [HS015 `static-method`](../rules/class-design.md#hs015-static-method) reports
  a `staticmethod`, which is the "class would contain one stateless method"
  entry in the do-not-extract list.

Section 11, class cohesion:

* [HS008 `low-class-cohesion`](../rules/class-design.md#hs008-low-class-cohesion)
  reports methods that split into disconnected clusters over the fields they
  touch, which is the closest mechanical reading of "one dominant
  responsibility".
* [HS012 `many-class-attributes`](../rules/class-design.md#hs012-many-class-attributes)
  reports a state surface above the configured limit, covering the constructor
  dependency signal.
* [HS018 `many-base-classes`](../rules/class-design.md#hs018-many-base-classes)
  reports more bases than the limit, which bears on preserving a base class
  contract.
* [HS004 `shared-mutable-state`](../rules/state-and-boundaries.md#hs004-shared-mutable-state)
  reports a mutable object bound in a class body, which is the mutable
  `ClassVar` signal.
* [HS017 `long-file`](../rules/state-and-boundaries.md#hs017-long-file) works at
  module rather than class scale, and asks the same question of a file that
  section 11 asks of a class.

Several criteria on this page have no shipped rule and are not detected at all:

* Section 7 in full. Nothing reports over-extraction, narration chains, or a
  helper that renames one obvious line. Every size rule above fires on code
  that is too large, never on code that has been split too finely.
* The public-method-count and private-helper-count signals in section 11.
* Naming criteria: the generic `Manager` or `Service` signal, and "named after
  a domain concept". Rule conditions are read off structure, not vocabulary.
* Setup methods called after construction, leaking mutable internals, and
  whether a constructor establishes valid state.

## References

The criteria above restate long-standing refactoring guidance rather than
inventing it. Primary sources:

* Martin Fowler, [Extract Function](https://refactoring.com/catalog/extractFunction.html),
  refactoring catalog.
* Martin Fowler, [Extract Class](https://refactoring.com/catalog/extractClass.html),
  refactoring catalog.
* Robert C. Martin, [The Single Responsibility Principle](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html),
  which is the "independent reason to change" criterion in section 8.
