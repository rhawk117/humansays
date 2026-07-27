"""The test named by the commit-format enforcement claim in
`.agent-specs/process/agent-protocol.md` section 8."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

GUARD = Path(__file__).resolve().parents[2] / 'scripts' / 'check_commit_msg.py'
_spec = importlib.util.spec_from_file_location('check_commit_msg', GUARD)
assert _spec
assert _spec.loader
check_commit_msg = importlib.util.module_from_spec(_spec)
sys.modules['check_commit_msg'] = check_commit_msg
_spec.loader.exec_module(check_commit_msg)

is_valid = check_commit_msg.is_valid


@pytest.mark.parametrize(
    'message',
    [
        'feat(analysis): split argument kinds',
        'chore(deps): bump ruff',
        'ops(ci): add deploy-site workflow',
        'fix(scope): add failing test for frozen facts',
        'release(0.2.0): cut the alpha',
        'docs(site): land criteria at site paths',
        'ops(tree-separation): split agent specs [merges #12]',
        'feat(analysis): split argument kinds\n\nBody paragraph here.',
    ],
)
def test_accepts_valid_messages(message: str) -> None:
    assert is_valid(message) is None


@pytest.mark.parametrize(
    ('message', 'reason'),
    [
        ('doc(readme): singular prefix', 'singular doc is not whitelisted'),
        ('feature(x): long-form prefix', 'feature is not whitelisted'),
        ('feat: missing scope', 'scope is required'),
        ('feat(analysis) missing colon', 'colon is required'),
        ('feat(analysis):no space after colon', 'space after colon required'),
        ('feat(analysis): ', 'summary must not be empty'),
        ('Merge branch develop', 'merge commits are not exempt'),
        ('', 'empty message'),
        ('feat(analysis): Capitalized summary', 'summary starts lowercase'),
        ('feat(analysis): trailing period.', 'no trailing period'),
    ],
)
def test_rejects_invalid_messages(message: str, reason: str) -> None:
    assert is_valid(message) is not None, reason


def test_ignores_comment_lines() -> None:
    message = 'feat(analysis): real summary\n# Please enter the commit message'
    assert is_valid(message) is None


def test_squash_merge_form_is_accepted() -> None:
    assert is_valid('ops(tree-separation): split specs [merges #7]') is None
