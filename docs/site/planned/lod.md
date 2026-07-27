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

| ID     | Rule                        | Default | Concern |
| ------ | --------------------------- | ------- | ------- |
| LOD001 | Field write outside owner   | on      | hazard  |
| LOD002 | Single attribute dependency | on      | review  |

## Rule details

### LOD001 Field write outside owner

**Claim.** risk

**Detection/default.** External code writes another object's non-private attribute

**Message template.** `{symbol}` writes `{target}.{field}` from outside the owning object.

### LOD002 Single attribute dependency

**Claim.** design

**Detection/default.** Function accepts an object but only reads one attribute from it

**Message template.** `send_notice()` accepts `User` but depends only on `user.email`, unnecessarily coupling the function to the entire class.
