# Contracts and inputs

A contract is what a caller can rely on without reading the body. When the name,
the parameters and the return type do not carry that promise, every caller has
to reconstruct it by reading the implementation, and every change to the
implementation risks breaking an expectation nobody wrote down. Hidden inputs
make the same problem worse in a second direction: a function that reaches for
module state, the clock, the environment or the filesystem cannot be understood
from its signature, cannot be exercised without arranging the world it expects,
and changes behavior when unrelated code runs first. Code like this is not hard
to change because it is complicated. It is hard to change because the set of
things that depend on it is not visible from the code itself.

## 2. Read the Contract

Determine what the name and signature promise before reading the body.

The unit should be describable in one sentence:

> Given **input**, it **performs one operation** and returns **result**.

### Good criteria

- The name uses domain vocabulary.
- Input and return types communicate the contract.
- Mutation or I/O is not disguised as a calculation or query.
- Normal absence and failure behavior are represented clearly.
- The description does not require several unrelated “and then” clauses.

### Warning signs

- Names such as `Manager`, `Helper`, `Utils`, `Processor`, or `handle`.
- Generic inputs such as `data: dict[str, object]`.
- A method named `get_*` that also writes state.
- A function whose real dependencies are missing from its signature.

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

- Function parameters
- Constructor dependencies
- Object-owned state

### Hidden inputs

- Mutable module state
- Environment variables read deep inside logic
- Global settings
- System time
- Randomness
- Filesystem state
- Network services
- Databases and caches

### Criteria

- Meaningful runtime dependencies are explicit.
- Long-lived dependencies are passed through constructors.
- Operation-specific data is passed to the method performing the operation.
- Stable constants remain constants; they do not need dependency injection.
- Tests construct dependencies instead of patching global state.

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

## What enforces this

Five shipped rules read structure that bears on the criteria above. Each one
raises a review question at a location; none of them decides whether the
contract is right.

| Code                                      | Signal                      | What it reads                                                                 | Criterion it touches                                                  |
| ----------------------------------------- | --------------------------- | ----------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| [HS001](../rules/function-shape.md)       | `many-arguments`            | More operation parameters than `max_arguments`, default `3`                   | Input types communicate the contract                                  |
| [HS002](../rules/function-shape.md)       | `boolean-modes`             | A boolean operation parameter, outside the single-argument `set_*` exemption  | The description does not require several unrelated “and then” clauses |
| [HS014](../rules/function-shape.md)       | `validated-argument-bundle` | A wide parameter list whose members are validated in the body                 | Input types communicate the contract                                  |
| [HS004](../rules/state-and-boundaries.md) | `shared-mutable-state`      | A mutable object bound at module or class scope                               | Hidden inputs: mutable module state                                   |
| [HS007](../rules/state-and-boundaries.md) | `mixed-boundaries`          | Three or more standard-library boundary categories named in one function body | Hidden inputs: filesystem, network, databases                         |

Several criteria on this page have no shipped rule, and the tool will not report
them:

- Naming criteria. Nothing detects `Manager`, `Helper`, `Utils`, `Processor` or
    `handle`, and nothing checks whether a name uses domain vocabulary.
- Generic inputs such as `data: dict[str, object]`. No rule inspects annotation
    content for vagueness.
- A `get_*` method that writes state. No shipped rule pairs a name prefix with
    the mutations in a body.
- Hidden inputs other than module and class scope bindings. Environment
    variables, global settings, system time and randomness are not detected.
- Whether long-lived dependencies arrive through the constructor, and whether
    tests construct dependencies rather than patching global state.

## References

- Martin Fowler, [Introduce Parameter Object](https://refactoring.com/catalog/introduceParameterObject.html),
    the refactoring behind HS001 and HS014: a repeated group of arguments is an
    object that has not been named yet.
- Martin Fowler, [CommandQuerySeparation](https://martinfowler.com/bliki/CommandQuerySeparation.html),
    the source of the rule that a query must not change observable state, which is
    what the `get_*` warning sign is an instance of.
- Martin Fowler, [Replace Parameter With Query](https://refactoring.com/catalog/replaceParameterWithQuery.html),
    the counterweight: not every value belongs in the signature, and a parameter
    the callee can derive is one the caller should not have to supply.
- [PEP 3102](https://peps.python.org/pep-3102/), keyword-only arguments, the
    language feature that makes a mode visible at the call site rather than
    positional.
