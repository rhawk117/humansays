# SBD rules

SBD rules cover trust boundaries, unbounded resources, unverified assumptions
about input, and constructs that defeat static auditability.

This is not a security scanner. It does not duplicate `bandit`: a rule belongs
here only when a conventional scanner would stay quiet and the finding still
concerns one of those four things. The admission test that decides membership,
and the list of things this domain deliberately does not do, are published on
this page alongside the rules.

None of the rules below are implemented yet. They are planned.

| ID     | Rule                        | Default | Concern |
| ------ | --------------------------- | ------- | ------- |
| SBD012 | Process hash as identity    | on      | hazard  |
| SBD013 | Import path mutation        | on      | hazard  |
| SBD014 | Dynamic namespace access    | on      | hazard  |
| SBD015 | Module object customization | on      | hazard  |
| SBD016 | Dynamic attribute mutation  | on      | hazard  |

## Rule details

### SBD012 Process hash as identity

**Claim.** risk

**Detection/default.** `hash()` output crosses a process boundary or enters persistent storage

**Message template.** `hash(value)` is persisted even though Python hashes may change between processes.

### SBD013 Import path mutation

**Claim.** risk

**Detection/default.** Mutation of `sys.path`, `sys.meta_path`, `sys.path_hooks` or related import machinery

**Message template.** `sys.path.insert()` changes process-global import resolution instead of using the package structure.

### SBD014 Dynamic namespace access

**Claim.** risk

**Detection/default.** Calls to `locals()` or `globals()`

**Message template.** `locals()` converts implementation-local names into an implicit runtime data contract.

### SBD015 Module object customization

**Claim.** risk

**Detection/default.** Replacement or class mutation of the current module through `sys.modules`

**Message template.** This module replaces or mutates its own module object, making runtime behavior differ from its source namespace.

### SBD016 Dynamic attribute mutation

**Claim.** risk

**Detection/default.** Dynamic `setattr`, `delattr` or `__dict__.update()` changes object state

**Message template.** `setattr(target, name, value)` mutates an attribute whose existence and type are unavailable to static review.
