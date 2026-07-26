# Python Code Design and Review Criteria

## Purpose

Use this document when writing or reviewing Python functions and classes. It defines criteria for readable, cohesive, testable code without encouraging excessive abstraction or fragmented one-line helpers.

The central rule is:

> Keep code together when it expresses one complete idea. Separate it when a part has its own responsibility, state, lifecycle, failure mode, or reason to change.

These criteria are review signals, not mechanical limits. A cohesive 60-line parser can be better than twelve five-line functions spread across several modules.

## 1. Classify the Unit

Before reviewing an implementation, identify its dominant role.

### Functions

A function should primarily perform one of these roles:

* **Calculation:** derives a result without side effects.
* **Query:** reads state without intentionally changing it.
* **Command:** changes state.
* **Boundary operation:** performs database, filesystem, network, subprocess, or similar I/O.
* **Workflow:** coordinates several domain operations or boundaries.
* **Construction:** creates a valid object.

### Classes

A class should have one dominant role:

| Kind               | Primary responsibility                  | Default design                                |
| ------------------ | --------------------------------------- | --------------------------------------------- |
| Value object       | Represent a meaningful value            | Immutable and validated                       |
| DTO                | Carry data across a boundary            | Simple and usually immutable                  |
| Entity             | Preserve identity while state changes   | Controlled domain transitions                 |
| State owner        | Manage a mutable collection or resource | Private state and narrow API                  |
| Policy or strategy | Make one decision                       | Deterministic and replaceable                 |
| Use case           | Execute one application operation       | Explicit dependencies; minimal retained state |
| Repository         | Persist and retrieve domain state       | Hide storage details                          |
| Adapter or gateway | Communicate with an external system     | Translate at the boundary                     |
| Coordinator        | Order several operations                | Delegate decisions and I/O                    |
| Factory            | Select or construct objects             | Hide meaningful construction rules            |

If the function or class cannot be classified, it may combine unrelated responsibilities.

## 2. Read the Contract

Determine what the name and signature promise before reading the body.

The unit should be describable in one sentence:

> Given **input**, it **performs one operation** and returns **result**.

### Good criteria

* The name uses domain vocabulary.
* Input and return types communicate the contract.
* Mutation or I/O is not disguised as a calculation or query.
* Normal absence and failure behavior are represented clearly.
* The description does not require several unrelated “and then” clauses.

### Warning signs

* Names such as `Manager`, `Helper`, `Utils`, `Processor`, or `handle`.
* Generic inputs such as `data: dict[str, object]`.
* A method named `get_*` that also writes state.
* A function whose real dependencies are missing from its signature.

```python
def evaluate_finding(
    finding: Finding,
    policy: RiskPolicy,
) -> RiskAssessment:
    ...
```

This communicates substantially more than:

```python
def process(data: dict[str, object]) -> dict[str, object]:
    ...
```

## 3. Trace Inputs and Dependencies

List every value the implementation depends on, including hidden inputs.

### Explicit inputs

* Function parameters
* Constructor dependencies
* Object-owned state

### Hidden inputs

* Mutable module state
* Environment variables read deep inside logic
* Global settings
* System time
* Randomness
* Filesystem state
* Network services
* Databases and caches

### Criteria

* Meaningful runtime dependencies are explicit.
* Long-lived dependencies are passed through constructors.
* Operation-specific data is passed to the method performing the operation.
* Stable constants remain constants; they do not need dependency injection.
* Tests construct dependencies instead of patching global state.

```python
class RegisterUser:
    def __init__(
        self,
        users: UserRepository,
        identities: IdentityProvider,
        clock: Clock,
    ) -> None:
        self._users = users
        self._identities = identities
        self._clock = clock

    def execute(self, command: RegisterUserCommand) -> User:
        ...
```

## 4. Trace State Ownership

For every mutable value, determine:

1. Who owns it?
2. How long should it live?
3. Who may mutate it?
4. How can other code observe it?

### Placement criteria

| State lifetime         | Recommended location                          |
| ---------------------- | --------------------------------------------- |
| One calculation        | Local variable                                |
| One request or job     | Explicit request/context object               |
| One value              | Immutable value object                        |
| One entity             | Entity instance                               |
| One stateful component | Component instance                            |
| Entire application     | Explicitly constructed application dependency |
| Beyond the process     | Repository or persistent storage              |

### Good criteria

* Mutable state has one clear owner.
* Mutation occurs through meaningful methods on that owner.
* Internal mutable collections are not returned directly.
* An object’s lifetime matches the lifetime required by its state.
* `ClassVar` is not used merely to disguise global mutable state.

```python
class CheckRegistry:
    def __init__(self) -> None:
        self._check_types: dict[str, type[Check]] = {}

    def register(self, check_type: type[Check]) -> None:
        ...

    def resolve(self, check_name: str) -> type[Check]:
        ...

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._check_types))
```

### Warning signs

* A method mutates several passed objects.
* Callers receive and modify an owner’s internal dictionary or list.
* Mutable `ClassVar` collections are shared unintentionally.
* State survives longer than the operation that needs it.
* Tests must reset global state between cases.

## 5. Trace Side Effects

Mark every interaction with:

* Database
* Network
* Filesystem
* Subprocess
* Cache
* Message broker
* Clock
* Random source
* Logging or audit sink

### Criteria

* Side effects are visible through named collaborators or boundary functions.
* Business decisions are separated from technical I/O where practical.
* A workflow makes effect ordering understandable.
* Partial-failure behavior is considered when multiple effects occur.
* Domain objects do not contain vendor-specific networking or persistence logic.

A readable flow normally resembles:

```text
Acquire input → make decisions → create result → persist or publish
```

## 6. Protect Invariants

Objects that own state should also own the rules governing that state.

### Good criteria

* Construction produces a valid, usable object.
* Invalid values are rejected during construction.
* Entities expose domain transitions rather than generic setters.
* Callers cannot bypass important transition rules.
* Failed operations preserve valid state.

Prefer:

```python
user.activate()
account.withdraw(amount)
```

Over:

```python
user.status = UserStatus.ACTIVE
account.balance -= amount
```

Avoid temporal coupling:

```python
client = ApiClient()
client.configure(settings)
client.authenticate()
client.connect()
```

Prefer construction that establishes validity:

```python
client = ApiClient(
    settings=settings,
    credentials=credentials,
)
```

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

## 9. Function Argument Criteria

Argument counts are review thresholds, not correctness rules.

| Count | Review interpretation                                   |
| ----: | ------------------------------------------------------- |
|   0–3 | Usually clear                                           |
|     4 | Inspect whether values form a concept                   |
|   5–6 | Strong design smell                                     |
|    7+ | Usually missing an object or combining responsibilities |

### Evaluate the argument kinds

Distinguish:

* Operation input
* Optional configuration
* Long-lived dependency
* Repeated data group
* Boolean mode switch

### Criteria

* Parameters that form a real concept become a value or request object.
* Long-lived dependencies move to a constructor.
* Optional settings are keyword-only.
* Positional booleans are avoided.
* Parameter objects are not meaningless bags created only to lower the count.
* Several repeated dependencies do not automatically justify one broad service class.

```python
@dataclass(frozen=True, slots=True)
class ScanRequest:
    repository: str
    revision: str
    path: Path
    minimum_severity: Severity
    include_ignored: bool = False
```

```python
def run_scan(request: ScanRequest) -> ScanResult:
    ...
```

For secondary options:

```python
def run_scan(
    target: ScanTarget,
    *,
    minimum_severity: Severity = Severity.MEDIUM,
    include_ignored: bool = False,
) -> ScanResult:
    ...
```

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
| More than 7–10 public methods            | Does the API serve unrelated callers?                  |
| Many private helpers                     | Are several components hidden inside one class?        |
| Generic `Manager` or `Service` name      | What specific capability does it own?                  |
| Mutable `ClassVar`                       | Is this process-global state disguised as class state? |
| Several setup methods after construction | Can invalid intermediate states be removed?            |
| Networking or SQL inside an entity       | Has an infrastructure boundary leaked into the domain? |

## 12. Failure Criteria

For every branch and external call, determine:

* What can fail?
* What exception or result represents that failure?
* Can state be partially mutated?
* May the caller retry safely?
* Is ordinary absence distinct from infrastructure failure?

### Good criteria

* Expected absence is represented explicitly, such as `User | None`.
* Domain failures use meaningful exceptions or result types.
* Infrastructure errors are not silently converted into unrelated outcomes.
* Broad `except Exception` blocks do not swallow programming errors.
* Multi-step effects have explicit transaction, compensation, or idempotency behavior where required.

## 13. Testability Criteria

Try to sketch a test before approving the design.

Good code usually allows:

```python
repository = InMemoryUserRepository()
identity_provider = FakeIdentityProvider()
clock = FixedClock(...)

use_case = RegisterUser(
    users=repository,
    identities=identity_provider,
    clock=clock,
)

result = use_case.execute(command)
```

### Good criteria

* Tests construct inputs and dependencies directly.
* Tests do not require application startup for domain behavior.
* Each test receives isolated mutable state.
* Pure decisions can be tested without I/O.
* External boundaries can be replaced with small in-memory or fake implementations.
* Protocols are introduced at real boundaries, not for every class.

### Warning signs

* Extensive monkeypatching of module globals.
* Environment variables required for unit tests.
* Tests must clear caches or registries between cases.
* A simple rule requires a real network, database, or filesystem.
* Tests assert implementation call sequences instead of outcomes.

## 14. Review Thresholds

These signals require inspection but do not mandate refactoring.

| Signal                                    | Question to ask                                          |
| ----------------------------------------- | -------------------------------------------------------- |
| Function exceeds roughly 30–50 lines      | Is it mixing workflow, decisions, and technical details? |
| More than 3 indentation levels            | Can guard clauses or extraction flatten it?              |
| More than 4 parameters                    | Do some parameters form one concept?                     |
| More than 5 constructor dependencies      | Does the class have multiple responsibilities?           |
| More than 7–10 public methods             | Is the public API cohesive?                              |
| Same arguments repeatedly travel together | Is there a missing value object or state owner?          |
| One-line helpers are spread across files  | Has extraction increased navigation cost?                |
| A method mutates multiple owners          | Is the transaction or authority unclear?                 |

## 15. Review Scorecard

Score each category from 0 to 2.

| Category        | 0                      | 1                    | 2                    |
| --------------- | ---------------------- | -------------------- | -------------------- |
| Purpose         | Unclear                | Broad                | One clear job        |
| Inputs          | Mostly hidden          | Mixed                | Explicit             |
| State ownership | Shared or unclear      | Partially controlled | One clear owner      |
| Side effects    | Hidden or scattered    | Visible but mixed    | Explicit boundaries  |
| Invariants      | Unprotected            | Partially enforced   | Enforced by owner    |
| Failures        | Swallowed or ambiguous | Inconsistent         | Explicit semantics   |
| Dependencies    | Global or concrete     | Partially injected   | Explicit and focused |
| Testability     | Requires environment   | Requires patching    | Construct and call   |
| Naming          | Generic                | Understandable       | Domain-specific      |
| Abstraction     | Mixed levels           | Minor mixing         | Consistent level     |

Interpretation:

| Score | Interpretation                                             |
| ----: | ---------------------------------------------------------- |
| 17–20 | Strong design                                              |
| 13–16 | Generally sound; inspect weak areas                        |
|  9–12 | Significant design debt                                    |
|   0–8 | Responsibility and state ownership likely require redesign |

The score identifies reasoning difficulty. It must not be used as an automatic refactoring trigger.

## 16. Pull Request Checklist

### Responsibility

* [ ] Each changed function or class has one dominant responsibility.
* [ ] Names communicate domain intent.
* [ ] Related code remains together.
* [ ] Extracted code introduces a real abstraction rather than narration.

### Inputs and state

* [ ] Meaningful dependencies are explicit.
* [ ] Mutable state has one clear owner.
* [ ] Object lifetimes match state lifetimes.
* [ ] Mutable internals are not exposed.
* [ ] Mutable `ClassVar` or module state is deliberately justified.

### Behavior

* [ ] Business rules are owned by the appropriate entity or policy.
* [ ] Workflows coordinate rather than implement every dependency detail.
* [ ] External I/O is isolated behind clear boundaries.
* [ ] Commands and queries are not misleadingly combined.

### Construction and arguments

* [ ] Constructors produce valid objects.
* [ ] Functions with more than four parameters were reviewed for missing concepts.
* [ ] Constructors with more than five dependencies were reviewed for excessive responsibility.
* [ ] Parameter objects represent meaningful concepts.
* [ ] Optional and boolean parameters are keyword-only where useful.

### Failures and tests

* [ ] Failure behavior is explicit.
* [ ] Partial mutation and retry behavior were considered.
* [ ] Tests construct dependencies instead of repairing global state.
* [ ] Important decisions can be tested without external infrastructure.
* [ ] Tests assert behavior and outcomes rather than incidental implementation details.

## Final Decision Rule

When deciding whether to leave code inline, extract a function, or create a class:

1. **Leave it inline** when it is one readable part of a cohesive operation.
2. **Extract a function** when a block forms a named calculation, rule, or lower-level operation without needing persistent state.
3. **Extract a class** when behavior requires owned state, shared configuration, injected dependencies, identity, interchangeable implementations, or resource lifecycle.
4. **Create a boundary abstraction** when external technology should not define the application or domain API.

The final test is:

> Did the change make ownership, intent, and behavior easier to understand without forcing the reader to navigate more code than necessary?
