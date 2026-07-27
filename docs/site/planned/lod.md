# LOD rules

LOD rules cover reaching past the object you were handed. A function that walks
through a collaborator to touch something the collaborator owns, or that writes
a field belonging to another object, has coupled itself to a structure it does
not control — and that structure can change without the function ever appearing
in the diff.

None of the rules below are implemented yet. They are planned.

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

### LOD001 Field write outside owner

**Claim.** risk

**Detection/default.** External code writes another object's non-private attribute

**Message template.** `{symbol}` writes `{target}.{field}` from outside the owning object.

### LOD002 Single attribute dependency

**Claim.** design

**Detection/default.** Function accepts an object but only reads one attribute from it

**Message template.** `send_notice()` accepts `User` but depends only on `user.email`, unnecessarily coupling the function to the entire class.

### LOD003 Chain reached past an unconstructed value

**Claim.** design

**Detection/default.** A call or attribute chain exceeding `max_chain_depth` on a value the function did not construct

**Message template.** `{symbol}` reaches `{depth}` levels into `{root}`, a value it did not construct. Should the intermediate object expose what is needed?

Two exemptions apply. A chain rooted in a value the function constructed itself
is never reported — reaching as far as you like into something you built couples
you to nothing you do not already own. And `allow_chaining`, a list of dotted
names, exempts fluent-builder APIs where chaining is the intended interface
rather than a leak of structure.
