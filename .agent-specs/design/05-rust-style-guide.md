# Rust Code Design and Review Criteria

## Purpose

Use this document when writing or reviewing Rust functions, structs, enums, traits, modules, and implementations. It defines criteria for cohesive, readable, testable code without encouraging excessive traits, tiny modules, unnecessary generics, or abstraction for its own sake.

The central rule is:

> Keep code together when it expresses one complete idea. Separate it when a part has its own responsibility, owned state, lifecycle, failure mode, substitution boundary, or reason to change.

Rust provides strong mechanisms for expressing ownership and invariants. Good Rust uses those mechanisms to make correct behavior obvious. Bad Rust can still hide responsibility behind excessive traits, `Arc<Mutex<_>>`, clones, generic wrappers, or modules that add navigation without meaning.

## 1. Classify the Unit

Before reviewing an implementation, identify its dominant role.

### Functions

A function should primarily perform one of these roles:

* **Calculation:** derives a result without observable side effects.
* **Query:** borrows state and returns information without intentionally changing it.
* **Command:** mutates owned or borrowed state.
* **Transformation:** consumes one representation and produces another.
* **Boundary operation:** performs database, filesystem, network, subprocess, or similar I/O.
* **Workflow:** coordinates domain operations and boundaries.
* **Construction:** establishes a valid value or resource owner.

### Rust types

| Kind               | Primary responsibility                        | Default design                                                   |
| ------------------ | --------------------------------------------- | ---------------------------------------------------------------- |
| Value type         | Represent meaningful data                     | Immutable by default; validated construction                     |
| Entity             | Preserve identity while state changes         | Private fields and controlled transitions                        |
| State owner        | Own a collection, cache, session, or resource | Narrow `impl`; mutation through methods                          |
| State enum         | Represent mutually exclusive states           | Exhaustive variants; associated state data                       |
| Policy or strategy | Make one decision                             | Function, closure, generic parameter, or small trait             |
| Use case           | Execute one application operation             | Explicit dependencies; minimal retained state                    |
| Repository         | Persist and retrieve domain state             | Trait only when multiple implementations or isolation are needed |
| Adapter            | Communicate with an external system           | Translate external types and errors at the boundary              |
| Coordinator        | Order several operations                      | Delegate decisions and technical details                         |
| Factory            | Select or construct implementations           | Hide meaningful construction rules                               |
| Resource guard     | Manage acquisition and release                | RAII; cleanup tied to ownership                                  |

If a function or type cannot be classified, it may combine unrelated responsibilities.

## 2. Read the Contract from the Signature

Rust signatures communicate behavior through both types and ownership.

```rust
fn evaluate_finding(
    finding: &Finding,
    policy: &RiskPolicy,
) -> RiskAssessment
```

This tells the reader:

* The function borrows both inputs.
* It does not require mutable access.
* It returns an owned result.
* It does not report an expected failure.

Compare:

```rust
fn process(data: &mut HashMap<String, Value>) -> Result<Value, Box<dyn Error>>
```

The second signature leaves the domain, mutation scope, and failure contract unclear.

### Ownership vocabulary

| Parameter form         | Meaning the API should intend                  |
| ---------------------- | ---------------------------------------------- |
| `value: T`             | Consume or take ownership of the value         |
| `value: &T`            | Observe without mutation or ownership          |
| `value: &mut T`        | Mutate the caller-owned value exclusively      |
| `value: impl Into<T>`  | Accept several owned input representations     |
| `value: impl AsRef<T>` | Borrow through several wrapper representations |
| `self`                 | Consume the object                             |
| `&self`                | Query or operate without mutation              |
| `&mut self`            | Mutate object-owned state                      |

### Criteria

* Ownership choices match actual behavior.
* A function does not take ownership when a borrow is sufficient.
* A function does not accept `&mut T` merely for convenience.
* Consuming methods use `self` when the old value should become unusable.
* Return types distinguish success, absence, and failure.
* Generic conversion bounds are introduced only when they improve real call sites.

## 3. Model Data with Types

Use types to represent domain distinctions rather than passing primitives with implied meanings.

Weak:

```rust
fn activate_user(user_id: String, status: String) -> Result<(), Error>
```

Stronger:

```rust
struct UserId(Uuid);

enum UserStatus {
    Pending,
    Active,
    Suspended,
}

fn activate_user(user_id: &UserId) -> Result<User, ActivateUserError>
```

### Value types

```rust
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct EmailAddress(String);

impl EmailAddress {
    pub fn parse(value: impl Into<String>) -> Result<Self, InvalidEmail> {
        let normalized = value.into().trim().to_lowercase();

        if !normalized.contains('@') {
            return Err(InvalidEmail);
        }

        Ok(Self(normalized))
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}
```

### Criteria

* Newtypes distinguish values that share the same primitive representation.
* Constructors validate and normalize once.
* Fields remain private when callers could violate invariants.
* `enum` represents alternatives instead of loosely related booleans.
* Domain types derive only traits that match their semantics.
* `Copy` is used for cheap value semantics, not added automatically.
* `Default` is implemented only when a meaningful valid default exists.

Avoid:

```rust
#[derive(Default)]
struct User {
    id: String,
    email: String,
}
```

An empty user is not a meaningful default merely because deriving it is convenient.

## 4. Make Invalid States Difficult to Represent

Prefer designs where the compiler eliminates invalid combinations.

Weak:

```rust
struct Job {
    is_running: bool,
    is_complete: bool,
    error: Option<String>,
}
```

This permits contradictory states such as running and complete simultaneously.

Stronger:

```rust
enum JobState {
    Pending,
    Running {
        started_at: Instant,
    },
    Completed {
        output: JobOutput,
    },
    Failed {
        error: JobError,
    },
}
```

### Criteria

* Mutually exclusive states use `enum`.
* Variant-specific data lives inside the relevant variant.
* Boolean fields are not used to encode a hidden state machine.
* Transitions consume or mutably borrow the current owner intentionally.
* Typestate is reserved for APIs where compile-time sequencing materially improves safety.

Do not introduce a complex typestate API for an ordinary three-step builder if a validated `build() -> Result<T, E>` is clearer.

## 5. Trace State Ownership

For every mutable value, determine:

1. Which value owns it?
2. How long should it live?
3. Which code may mutate it?
4. Is mutation exclusive, synchronized, or interior?

### Placement criteria

| State lifetime      | Recommended location                                |
| ------------------- | --------------------------------------------------- |
| One calculation     | Local binding                                       |
| One request or job  | Request/job value                                   |
| One domain entity   | Entity struct                                       |
| One component       | Component struct                                    |
| One task            | Task-owned value                                    |
| Shared across tasks | Explicit `Arc` owner with justified synchronization |
| Beyond the process  | Repository or persistent storage                    |

### Good state owner

```rust
pub struct CheckRegistry {
    checks: HashMap<CheckName, Box<dyn Check>>,
}

impl CheckRegistry {
    pub fn new() -> Self {
        Self {
            checks: HashMap::new(),
        }
    }

    pub fn register(
        &mut self,
        name: CheckName,
        check: impl Check + 'static,
    ) -> Result<(), DuplicateCheck> {
        if self.checks.contains_key(&name) {
            return Err(DuplicateCheck(name));
        }

        self.checks.insert(name, Box::new(check));
        Ok(())
    }

    pub fn get(&self, name: &CheckName) -> Option<&dyn Check> {
        self.checks.get(name).map(Box::as_ref)
    }
}
```

### Criteria

* Mutable state has one obvious owner.
* Mutation is performed through methods on that owner.
* Internal collections are not exposed mutably without a deliberate reason.
* Shared ownership is explicit rather than hidden.
* `Rc`, `Arc`, `RefCell`, `Mutex`, and `RwLock` are introduced because the ownership model requires them, not to silence borrow-checker friction.

### Warning signs

* Repeated `.clone()` calls whose ownership purpose is unclear.
* `Arc<Mutex<T>>` used as a default container.
* Broad use of `RefCell` to avoid designing mutation boundaries.
* Long-lived mutable borrows that block otherwise independent operations.
* Global mutable state, including hidden `static` registries.

## 6. Prefer Ordinary Ownership Before Shared Ownership

Start with one owner and borrowed access.

```rust
struct Application {
    registry: CheckRegistry,
    repository: SqliteRepository,
}
```

Add reference counting only when multiple owners genuinely outlive one another:

```rust
Arc<SharedState>
```

Add locking only when concurrent mutation is required:

```rust
Arc<Mutex<SharedState>>
```

### Criteria

* The need for multiple owners is explainable.
* The need for mutation is explainable separately.
* Lock scope is small and visible.
* Locks are not held across unrelated work or `.await`.
* Data is partitioned to reduce shared mutation where practical.
* Message passing is considered when it gives one task exclusive ownership.

The presence of `Arc<Mutex<_>>` should trigger an ownership review, not automatic rejection.

## 7. Trace Side Effects

Mark every interaction with:

* Database
* Network
* Filesystem
* Subprocess
* Cache
* Clock
* Random source
* Message broker
* Environment
* Logging or audit sink

### Criteria

* Side effects occur through named boundary components or focused functions.
* Core decisions can be understood without reading transport or storage mechanics.
* A workflow makes effect ordering visible.
* Partial failure and retry behavior are considered.
* External library types do not spread through the domain API unnecessarily.

A readable workflow usually resembles:

```text
Acquire input → validate → decide → construct result → persist or publish
```

## 8. Keep Code Together When It Is One Idea

Keep code inline when:

* It forms one short, linear operation.
* The steps share the same inputs and local state.
* The steps make sense only inside the operation.
* Extraction would create redundant names.
* The extracted function would not be independently tested or reused.
* The implementation is clearer than any helper name.

This is appropriately cohesive:

```rust
fn normalize_username(value: &str) -> Result<Username, InvalidUsername> {
    let normalized = value.trim().to_lowercase();

    if normalized.is_empty() || normalized.len() > 32 {
        return Err(InvalidUsername);
    }

    Ok(Username(normalized))
}
```

Do not fragment it into `trim_username`, `lowercase_username`, `validate_empty`, and `validate_length` unless those are independently meaningful rules.

## 9. Extract for Semantic Compression

Extract code when separation:

* Introduces a meaningful domain name.
* Establishes state ownership.
* Creates an explicit I/O boundary.
* Hides a lower abstraction level.
* Supports focused testing.
* Supports multiple implementations.
* Manages a separate lifecycle.
* Captures independently changing behavior.

Useful extraction:

```rust
if lockout_policy.should_lock(user, now) {
    user.lock(now);
}
```

The policy name communicates a business rule more clearly than an inline compound condition.

Weak extraction:

```rust
if has_many_attempts(user) && is_inside_window(user, now) {
    set_user_locked(user);
}
```

This distributes one rule across several navigation points without creating a stronger abstraction.

## 10. Keep One Abstraction Level per Function

Application workflows should not contain raw SQL, HTTP payload construction, domain decisions, and response formatting in the same body.

Mixed:

```rust
async fn register_user(command: RegisterUser) -> Result<User, Error> {
    sqlx::query("SELECT EXISTS ...").fetch_one(&pool).await?;
    client.post("/admin/users").json(&json!({ ... })).send().await?;
    // Domain construction and more SQL...
}
```

Balanced:

```rust
impl<R, I> RegisterUser<R, I>
where
    R: UserRepository,
    I: IdentityProvider,
{
    pub async fn execute(
        &self,
        command: RegisterUserCommand,
    ) -> Result<User, RegisterUserError> {
        let email = EmailAddress::parse(command.email)?;

        if self.users.exists_by_email(&email).await? {
            return Err(RegisterUserError::EmailAlreadyRegistered);
        }

        let identity = self.identities.create_user(&email).await?;
        let user = User::register(identity.id, email);

        self.users.add(&user).await?;
        Ok(user)
    }
}
```

The workflow stays together. Database and HTTP mechanics remain behind focused boundaries.

## 11. Function Argument Criteria

Argument counts are review thresholds, not correctness rules.

| Count | Review interpretation                                                      |
| ----: | -------------------------------------------------------------------------- |
|   0–3 | Usually clear                                                              |
|     4 | Inspect whether values form a concept                                      |
|   5–6 | Strong design smell                                                        |
|    7+ | Usually missing a request/configuration type or combining responsibilities |

The kinds of arguments matter more than the raw count:

* Operation input
* Borrowed dependency
* Configuration
* Repeated data group
* Boolean mode
* Generic strategy

### Criteria

* Values that form a real concept become a struct.
* Long-lived dependencies live on the owning use-case or component struct.
* Configuration uses a named configuration type.
* Booleans that select behavior become an enum.
* A builder is used only when construction has many optional or staged choices.
* A parameter struct is not a meaningless bag created only to reduce the count.

Prefer:

```rust
struct ScanRequest {
    repository: RepositoryId,
    revision: Revision,
    path: PathBuf,
    minimum_severity: Severity,
    ignored_files: IgnorePolicy,
}

fn run_scan(request: &ScanRequest) -> Result<ScanResult, ScanError>
```

Over:

```rust
fn run_scan(
    repository: &str,
    revision: &str,
    path: &Path,
    minimum_severity: Severity,
    include_ignored: bool,
    follow_links: bool,
) -> Result<ScanResult, ScanError>
```

## 12. Criteria for Extracting a Struct with Behavior

Rust does not have classes, but a `struct` plus `impl` fills the state-owning role.

Extract a struct when:

* State must survive between calls.
* Several operations act on the same private state.
* Dependencies or configuration are established once and reused.
* Construction enforces invariants.
* The value has meaningful identity.
* It owns a resource.
* It implements a genuine trait contract.

Functions carrying the same state reveal a possible owner:

```rust
fn register_check(
    checks: &mut HashMap<CheckName, CheckType>,
    check: CheckType,
) -> Result<(), DuplicateCheck>

fn resolve_check(
    checks: &HashMap<CheckName, CheckType>,
    name: &CheckName,
) -> Option<&CheckType>
```

Extract:

```rust
struct CheckRegistry {
    checks: HashMap<CheckName, CheckType>,
}
```

### Do not extract a struct solely because

* A function is longer than expected.
* The function has several arguments.
* Rust supports methods.
* A trait might be useful later.
* The struct would be a zero-state namespace for one function.

Keep stateless behavior as a function:

```rust
fn normalize_email(value: &str) -> String {
    value.trim().to_lowercase()
}
```

Do not add ceremony:

```rust
struct EmailNormalizer;

impl EmailNormalizer {
    fn normalize(&self, value: &str) -> String {
        value.trim().to_lowercase()
    }
}
```

## 13. Trait Criteria

Traits define shared behavior contracts. They should not be created for every concrete type.

Use a trait when:

* Multiple implementations already exist or are intentionally required.
* Callers depend on behavior rather than representation.
* A boundary needs substitution in tests or deployments.
* Generic algorithms operate over a coherent capability.
* The trait communicates a stable semantic contract.

### Good criteria

* Traits are small and cohesive.
* Required behavior is meaningful to callers.
* The trait is defined near the consumer when it exists primarily for that consumer.
* Implementations obey semantic behavior, not just matching signatures.
* Generic dispatch and dynamic dispatch are chosen intentionally.
* Associated types represent one implementation-specific type relationship.
* Generic parameters do not expose unnecessary implementation details to callers.

### Static versus dynamic dispatch

Use generics when:

* The concrete type can be known at compile time.
* Monomorphization is acceptable.
* The caller benefits from static dispatch.

```rust
struct RegisterUser<R, I> {
    users: R,
    identities: I,
}
```

Use `dyn Trait` when:

* Implementations must be selected or stored at runtime.
* Heterogeneous implementations share one collection.
* Reducing type propagation matters more than static dispatch.

```rust
struct CheckRegistry {
    checks: HashMap<CheckName, Box<dyn Check>>,
}
```

### Warning signs

* A trait exists only to mock one concrete implementation.
* A trait has one implementation and no real substitution need.
* A trait mirrors every method of a large concrete type.
* Every dependency becomes a generic parameter and infects the public API.
* `Box<dyn Trait>` is used without a runtime-substitution requirement.

## 14. Error Handling Criteria

Use `Option<T>` for expected absence and `Result<T, E>` for operations that can fail.

### Criteria

* Error types communicate failures the caller may handle differently.
* `?` propagates errors while preserving useful context.
* Parsing, validation, domain, and infrastructure failures are not collapsed carelessly.
* Library APIs expose stable typed errors where callers need to react.
* Application boundaries may aggregate errors when detailed recovery is unnecessary.
* `panic!`, `unwrap()`, and `expect()` are reserved for proven invariants, tests, initialization failures, or truly unrecoverable conditions.
* `expect()` states the violated invariant rather than saying only “failed.”

Prefer:

```rust
let configuration = load_configuration()
    .context("failed to load agent configuration")?;
```

Over:

```rust
let configuration = load_configuration().unwrap();
```

Avoid error erasure in reusable domain APIs:

```rust
fn register_user(...) -> Result<User, Box<dyn Error>>
```

Prefer a meaningful error contract:

```rust
enum RegisterUserError {
    InvalidEmail(InvalidEmail),
    EmailAlreadyRegistered,
    IdentityProvider(IdentityProviderError),
    Repository(RepositoryError),
}
```

## 15. Iterator and Collection Criteria

Iterator chains can make transformations concise, but density is not automatically clarity.

Good:

```rust
let active_ids: Vec<UserId> = users
    .iter()
    .filter(|user| user.is_active())
    .map(|user| user.id().clone())
    .collect();
```

Prefer a loop when:

* Several branches require names or comments.
* Mutation occurs across several structures.
* Error handling becomes difficult to follow.
* The iterator chain requires repeated inspection to understand.

### Criteria

* Intermediate collections are not created without need.
* `.collect()` has an intentional target type.
* `.clone()` is not used merely to satisfy ownership without understanding it.
* Iterator chains remain readable at one abstraction level.
* A direct loop is preferred over clever combinator nesting when behavior is stateful or branch-heavy.

## 16. Async and Concurrency Criteria

Async code should make ownership, cancellation, and synchronization clear.

### Criteria

* Async is used for concurrency involving waits, not as a default for pure computation.
* Blocking work does not run directly on an async executor.
* Locks are not held across `.await` unless the lock is designed and justified for it.
* Spawned tasks have explicit ownership and shutdown behavior.
* Cancellation does not leave partially committed state.
* Channels have intentional capacity and backpressure behavior.
* Shared state is minimized.
* `Send + Sync + 'static` bounds are introduced because task movement requires them, not copied blindly.

### Warning signs

* Detached tasks with no failure observation.
* Unbounded channels without a load argument.
* `Arc<Mutex<_>>` surrounding an entire application state object.
* A synchronous trait forced into async through ad hoc boxing everywhere.
* A transaction or guard held across remote calls unnecessarily.

## 17. Resource and Lifecycle Criteria

Rust’s RAII model should make resource lifetime visible through ownership.

```rust
struct TemporaryWorkspace {
    path: PathBuf,
}

impl Drop for TemporaryWorkspace {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.path);
    }
}
```

### Criteria

* Resource acquisition produces an owner.
* Release happens when the owner is dropped.
* Borrowed handles cannot outlive the owner.
* Fallible cleanup has an explicit method when callers must observe failure.
* `Drop` does not contain essential fallible behavior that callers need to verify.
* Guards represent scoped locks, transactions, temporary changes, or cleanup.

Use:

```rust
workspace.close()?;
```

when cleanup failure matters. `Drop` may remain a best-effort fallback.

## 18. Unsafe Code Criteria

Every `unsafe` block creates an obligation that the compiler cannot verify.

### Required criteria

* `unsafe` is isolated behind a small safe API.
* The safety invariant is stated precisely.
* Every pointer, aliasing, lifetime, alignment, initialization, and thread-safety assumption is justified.
* The safe wrapper prevents callers from violating the invariant.
* Tests cover boundary cases, but tests are not treated as proof of safety.
* Existing safe abstractions were considered first.
* `unsafe impl Send` or `Sync` receives especially strict review.

Avoid expanding `unsafe` scope merely to reduce the number of blocks. Smaller blocks make obligations easier to audit.

## 19. Module and Visibility Criteria

Modules should group cohesive concepts and control the public API.

### Criteria

* Modules are organized around capabilities or domain concepts.
* `pub` is used only when another module or crate requires access.
* `pub(crate)` and private visibility are preferred for internal implementation.
* Re-exports simplify the intended public API rather than exposing the file layout.
* Tiny modules are not created for every type.
* Large modules are split when they contain independently changing concepts.
* `mod.rs` or file layout choices remain consistent and predictable.

The goal is not one type per file. The goal is one understandable capability per module boundary.

## 20. Testability Criteria

Good Rust code is usually testable by constructing values and invoking behavior.

```rust
#[test]
fn active_user_can_be_suspended() {
    let mut user = User::active(
        UserId::new(),
        EmailAddress::parse("beast@example.com").unwrap(),
    );

    user.suspend().unwrap();

    assert_eq!(user.status(), UserStatus::Suspended);
}
```

### Good criteria

* Pure decisions require no external infrastructure.
* Mutable state is isolated per test.
* Boundary implementations can be replaced with focused in-memory implementations.
* Traits are introduced for real boundaries rather than blanket mockability.
* Tests assert outcomes and invariants.
* Integration tests exercise public APIs and compiled binaries where appropriate.
* Unit tests remain near private logic only when that logic has meaningful independent behavior.

### Warning signs

* Global test serialization is required because state leaks between tests.
* Every dependency requires a large mock expectation script.
* Tests duplicate implementation call order instead of checking results.
* Simple rules require a database, network, or executor.
* Private implementation details are made `pub` only for tests.

## 21. Review Thresholds

These signals require inspection but do not mandate refactoring.

| Signal                                         | Question to ask                                           |
| ---------------------------------------------- | --------------------------------------------------------- |
| Function exceeds roughly 30–50 lines           | Is it mixing workflow, decisions, and technical details?  |
| More than 3 indentation levels                 | Can early returns, `match`, or extraction clarify it?     |
| More than 4 parameters                         | Do some values form one request or configuration concept? |
| More than 5 stored dependencies                | Does the struct coordinate too many responsibilities?     |
| More than 7–10 public methods                  | Is the public API cohesive?                               |
| More than 2–3 generic type parameters          | Is generic complexity leaking beyond its value?           |
| Repeated lifetime annotations dominate the API | Is ownership overly coupled or is an owned value clearer? |
| Frequent `.clone()`                            | Is ownership unclear or intentionally shared?             |
| Frequent `Arc<Mutex<_>>`                       | Can ownership be singular or state partitioned?           |
| Large error enum with unrelated variants       | Is one operation handling unrelated concerns?             |
| One-line helpers spread across modules         | Has extraction increased navigation cost?                 |

## 22. Review Scorecard

Score each category from 0 to 2.

| Category        | 0                             | 1                          | 2                          |
| --------------- | ----------------------------- | -------------------------- | -------------------------- |
| Purpose         | Unclear                       | Broad                      | One clear job              |
| Ownership       | Shared or obscured            | Understandable with effort | Explicit and natural       |
| State ownership | Multiple uncontrolled writers | Partially controlled       | One clear owner            |
| Type modeling   | Primitive or boolean-heavy    | Some domain types          | Invalid states constrained |
| Side effects    | Hidden or scattered           | Visible but mixed          | Explicit boundaries        |
| Errors          | Panics or erased failures     | Partially typed            | Actionable semantics       |
| Traits/generics | Ceremonial or contagious      | Mostly justified           | Focused and useful         |
| Concurrency     | Shared by default             | Controlled with complexity | Minimal and deliberate     |
| Testability     | Requires environment          | Requires broad mocks       | Construct and call         |
| Abstraction     | Fragmented or mixed           | Minor mixing               | Cohesive and navigable     |

Interpretation:

| Score | Interpretation                                       |
| ----: | ---------------------------------------------------- |
| 17–20 | Strong design                                        |
| 13–16 | Generally sound; inspect weak areas                  |
|  9–12 | Significant design debt                              |
|   0–8 | Ownership and responsibility likely require redesign |

The score identifies reasoning difficulty. It must not be used as an automatic refactoring trigger.

## 23. Pull Request Checklist

### Responsibility

* [ ] Each changed function, type, trait, and module has one dominant responsibility.
* [ ] Names communicate domain intent.
* [ ] Related code remains together.
* [ ] Extraction adds semantic value rather than narration.

### Ownership and state

* [ ] Ownership choices match the API’s actual behavior.
* [ ] Mutable state has one clear owner.
* [ ] Clones are intentional and reasonably cheap.
* [ ] `Arc`, `Mutex`, `RwLock`, and `RefCell` are justified.
* [ ] Internal mutable collections are not leaked.
* [ ] Resource lifetime is represented through ownership or a guard.

### Types and invariants

* [ ] Domain distinctions use meaningful types.
* [ ] Constructors establish valid values.
* [ ] Mutually exclusive states use enums where appropriate.
* [ ] Boolean flags do not conceal a state machine.
* [ ] `Default`, `Copy`, and other derives match semantics.

### Functions and APIs

* [ ] Functions with more than four parameters were reviewed for missing concepts.
* [ ] Structs with more than five dependencies were reviewed for excessive responsibility.
* [ ] Ownership and borrowing in public signatures are intentional.
* [ ] Public visibility is no broader than necessary.
* [ ] Iterator chains prioritize clarity over density.

### Traits and abstraction

* [ ] Every new trait has a real consumer or substitution need.
* [ ] Static versus dynamic dispatch is intentional.
* [ ] Generic parameters do not spread unnecessary complexity.
* [ ] Trait contracts are semantically substitutable.
* [ ] No zero-state struct exists merely as a function namespace.

### Errors, concurrency, and safety

* [ ] Expected absence uses `Option`; recoverable failure uses `Result`.
* [ ] `unwrap`, `expect`, and `panic` are justified.
* [ ] External errors preserve useful context.
* [ ] Lock scope, cancellation, and task shutdown were considered.
* [ ] Every unsafe operation documents and preserves its safety invariant.

### Tests

* [ ] Important decisions can be tested without external infrastructure.
* [ ] Tests construct values and dependencies directly.
* [ ] Tests assert behavior and invariants rather than incidental call order.
* [ ] Integration tests cover public APIs or binaries where that is the stronger boundary.
* [ ] Tests do not depend on leaked global state.

## Final Decision Rule

When deciding whether to leave code inline, extract a function, introduce a struct, or define a trait:

1. **Leave it inline** when it is one readable part of a cohesive operation.
2. **Extract a function** when a block forms a named calculation, rule, transformation, or lower-level operation without persistent state.
3. **Extract a struct with methods** when behavior requires owned state, shared configuration, identity, invariants, dependencies, or resource lifecycle.
4. **Define a trait** when callers need a stable behavior contract with meaningful substitution.
5. **Create a boundary adapter** when external technology should not define the application or domain API.
6. **Use shared ownership or synchronization** only after ordinary ownership cannot express the required lifetime or concurrency.

The final test is:

> Did the design make ownership, valid state, effects, and intent easier to understand without forcing the reader through more types, traits, and modules than the problem requires?
