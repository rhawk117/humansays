"""Line-keyed scope lookup, built during extraction and read by it alone."""

from dataclasses import dataclass, field
from operator import attrgetter

from humansays.facts.values import Scope


@dataclass(slots=True)
class ScopeIndex:
    scopes: list[Scope] = field(default_factory=list)

    def add(self, scope: Scope) -> None:
        self.scopes.append(scope)

    def for_line(self, line: int) -> Scope:
        candidates = [scope for scope in self.scopes if scope.contains(line)]
        if not candidates:
            return self.scopes[0]

        return min(candidates, key=attrgetter('span'))
