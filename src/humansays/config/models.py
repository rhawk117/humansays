"""Configuration models.

Frozen dataclasses carrying anything that can come from a config file or the
command line, so bad values fail at load time with a real error message.
"""

from dataclasses import dataclass, field

from humansays.const import DEFAULT_EXCLUDES
from humansays.enums import FailOn, OutputFormat
from humansays.findings.models import check_bounds


@dataclass(frozen=True, slots=True)
class FunctionThresholds:
    max_arguments: int = 3
    max_nesting: int = 3
    class_nesting_bonus: int = 1
    max_branches: int = 5
    max_lines: int = 50
    max_code_lines: int = 65

    def __post_init__(self) -> None:
        check_bounds((
            (self.max_arguments, 0, None, 'max_arguments'),
            (self.max_nesting, 0, None, 'max_nesting'),
            (self.class_nesting_bonus, 0, None, 'class_nesting_bonus'),
            (self.max_branches, 0, None, 'max_branches'),
            (self.max_lines, 1, None, 'max_lines'),
            (self.max_code_lines, 1, None, 'max_code_lines'),
        ))

    def nesting_limit(self, class_name: str | None = None) -> int:
        if class_name is None:
            return self.max_nesting
        return self.max_nesting + self.class_nesting_bonus


@dataclass(frozen=True, slots=True)
class ClassThresholds:
    max_attributes: int = 6
    max_base_classes: int = 1

    def __post_init__(self) -> None:
        check_bounds((
            (self.max_attributes, 0, None, 'max_attributes'),
            (self.max_base_classes, 0, None, 'max_base_classes'),
        ))


@dataclass(frozen=True, slots=True)
class ModuleThresholds:
    max_lines: int = 500

    def __post_init__(self) -> None:
        check_bounds(((self.max_lines, 1, None, 'max_lines'),))


@dataclass(frozen=True, slots=True)
class Thresholds:
    functions: FunctionThresholds = field(default_factory=FunctionThresholds)
    classes: ClassThresholds = field(default_factory=ClassThresholds)
    modules: ModuleThresholds = field(default_factory=ModuleThresholds)


@dataclass(frozen=True, slots=True)
class Selection:
    paths: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    symbol: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, 'paths', tuple(self.paths))
        object.__setattr__(self, 'exclude', tuple(self.exclude))

    @property
    def excludes(self) -> frozenset[str]:
        return DEFAULT_EXCLUDES | frozenset(self.exclude)


@dataclass(frozen=True, slots=True)
class Report:
    format: OutputFormat = OutputFormat.TEXT
    limit: int = 200
    fail_on: FailOn = FailOn.NEVER
    min_score: float = 0.0
    show_evidence: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, 'format', OutputFormat(self.format))
        object.__setattr__(self, 'fail_on', FailOn(self.fail_on))
        check_bounds((
            (self.limit, 0, None, 'limit'),
            (self.min_score, 0.0, 100.0, 'min_score'),
        ))


@dataclass(frozen=True, slots=True)
class ScannerSettings:
    thresholds: Thresholds = field(default_factory=Thresholds)
    selection: Selection = field(default_factory=Selection)
    report: Report = field(default_factory=Report)
