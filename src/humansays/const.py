"""Plain constants.

Data only. Functions live in ``factories``, class definitions in ``models``,
and the rule catalog in ``catalog`` (which needs ``models`` and would otherwise
make this module part of an import cycle).
"""

from collections import defaultdict, deque
from types import MappingProxyType

from humansays.enums import Grade, Severity

MAPPING_PROXY = type(MappingProxyType({}))

MUTABLE_COLLECTION_TYPES = (bytearray, dict, list, set, defaultdict, deque)
MUTABLE_METHOD_PAIRS = (
    (bytearray, bytes),
    (dict, MAPPING_PROXY),
    (list, tuple),
    (set, frozenset),
    (deque, tuple),
)
NON_MUTATING_METHOD_DIFFERENCES = frozenset({'copy', 'fromkeys'})
IMPLICIT_PARAMETERS = frozenset({'self', 'cls'})

BROAD_EXCEPTION_NAMES = frozenset({
    'BaseException',
    'Exception',
    'builtins.BaseException',
    'builtins.Exception',
})
CLASS_VAR_NAMES = frozenset({'ClassVar', 'typing.ClassVar'})
BOOL_NAMES = frozenset({'bool', 'builtins.bool'})
FUTURE_MODULE = '__future__'
FUTURE_ANNOTATIONS = 'annotations'

BOUNDARY_MODULES = MappingProxyType({
    'database': frozenset({'sqlite3'}),
    'filesystem': frozenset({'os', 'pathlib', 'shutil', 'tempfile'}),
    'network': frozenset({
        'ftplib',
        'http.client',
        'smtplib',
        'socket',
        'urllib.request',
    }),
    'process': frozenset({'multiprocessing', 'subprocess'}),
})
DEFAULT_EXCLUDES = frozenset({
    '.git',
    '.mypy_cache',
    '.pytest_cache',
    '.ruff_cache',
    '.tox',
    '.venv',
    '__pycache__',
    'build',
    'dist',
    'node_modules',
    'site-packages',
    'venv',
})
NON_STRUCTURAL_PREFIXES = frozenset({
    'can',
    'did',
    'does',
    'has',
    'is',
    'self',
    'should',
    'was',
    'will',
})

SEVERITY_ORDER = MappingProxyType({Severity.WARNING: 0, Severity.ADVISORY: 1})
UNKNOWN_SEVERITY_ORDER = 2
SEVERITY_STYLES = MappingProxyType({
    Severity.WARNING: 'bold yellow',
    Severity.ADVISORY: 'cyan',
})

GRADE_BANDS = ((90.0, Grade.A), (75.0, Grade.B), (60.0, Grade.C), (40.0, Grade.D))
GRADE_STYLES = MappingProxyType({
    Grade.A: 'bold green',
    Grade.B: 'green',
    Grade.C: 'yellow',
    Grade.D: 'bold yellow',
    Grade.F: 'bold red',
})
SCORE_WINDOW = 100.0
SCORE_TOLERANCE = 7.5
PERFECT_SCORE = 100.0

CLUSTER_MINIMUM = 3
MUTATION_OWNER_MINIMUM = 3
BOUNDARY_MINIMUM = 3
COHESION_METHOD_MINIMUM = 4
COHESION_FIELD_MINIMUM = 3
EVIDENCE_LIMIT = 10
UNPARSE_LIMIT = 80

STDIN_SPEC = '-'
DEFAULT_CONFIG_NAMES = ('humansays.toml', 'pyproject.toml')
NO_FILES_EXIT = 3
MISSING_SYMBOL_EXIT = 2
FINDINGS_EXIT = 1
CONFIG_ERROR_EXIT = 4
INTERNAL_ERROR_EXIT = 70

CLI_DESTINATIONS = MappingProxyType({
    'paths': ('selection', 'paths'),
    'exclude': ('selection', 'exclude'),
    'symbol': ('selection', 'symbol'),
    'output_format': ('report', 'format'),
    'limit': ('report', 'limit'),
    'fail_on': ('report', 'fail_on'),
    'min_score': ('report', 'min_score'),
    'max_arguments': ('thresholds', 'functions', 'max_arguments'),
    'max_nesting': ('thresholds', 'functions', 'max_nesting'),
    'class_nesting_bonus': ('thresholds', 'functions', 'class_nesting_bonus'),
    'max_branches': ('thresholds', 'functions', 'max_branches'),
    'max_function_lines': ('thresholds', 'functions', 'max_lines'),
    'max_code_lines': ('thresholds', 'functions', 'max_code_lines'),
    'max_class_attributes': ('thresholds', 'classes', 'max_attributes'),
    'max_base_classes': ('thresholds', 'classes', 'max_base_classes'),
    'max_file_lines': ('thresholds', 'modules', 'max_lines'),
})
PYPROJECT_SECTION = ('tool', 'humansays')
