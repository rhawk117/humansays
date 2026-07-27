# LOD rules

LOD rules cover reaching past the object you were handed. A function that walks
through a collaborator to touch something the collaborator owns, or that writes
a field belonging to another object, has coupled itself to a structure it does
not control — and that structure can change without the function ever appearing
in the diff.

!!! warning "Not implemented"

    These rules are designed, not shipped. Nothing on this page runs in
    version `0.1.0a1`, which implements [19 rules](../rules/index.md).

Background reading: the
[Law of Demeter](https://en.wikipedia.org/wiki/Law_of_Demeter) and
[Hide Delegate](https://refactoring.com/catalog/hideDelegate.html) in Martin
Fowler's refactoring catalog.

| ID     | Rule                                      | Default | Concern |
| ------ | ----------------------------------------- | ------- | ------- |
| LOD001 | Field write outside owner                 | on      | hazard  |
| LOD002 | Single attribute dependency               | on      | review  |
| LOD003 | Chain reached past an unconstructed value | on      | review  |

## Rule details

### LOD001 Field write outside owner { #LOD001 }

Claim
:   risk

Detection
:   External code writes another object's non-private attribute

Message
:   `{symbol}` writes `{target}.{field}` from outside the owning object. Should the owner make the change?

### LOD002 Single attribute dependency { #LOD002 }

Claim
:   design

Detection
:   Function accepts an object but only reads one attribute from it

Message
:   `send_notice()` accepts `User` and reads only `user.email`. Should it take the value instead?

### LOD003 Chain reached past an unconstructed value { #LOD003 }

Claim
:   design

Detection
:   A call or attribute chain exceeding `max_chain_depth` on a value the function did not construct

Message
:   `{symbol}` reaches `{depth}` levels into `{root}`, a value it did not construct. Should the intermediate object expose what is needed?

!!! note "Two exemptions"

    A chain rooted in a value the function constructed itself is never
    reported. Reaching as far as you like into something you built couples you
    to nothing you do not already own.

    `allow_chaining`, a list of dotted names, exempts fluent-builder APIs where
    chaining is the intended interface rather than a leak of structure.
