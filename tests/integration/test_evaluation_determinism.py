"""The same input produces the same bytes, run after run and process after process.

In-process repetition is not enough on its own. Rule metadata is loaded from
package data through a cached reader, adapters are held in module-level tuples,
and set and dict iteration order is only stable within one interpreter. A
difference that hash seeding introduces would be invisible to a loop inside a
single process.
"""

from __future__ import annotations

import subprocess
import sys

CORPUS = 'tests/golden/poc-parity/corpus/django'
RUNS = 3


def scan(output_format: str) -> str:
    completed = subprocess.run(  # noqa: S603
        [sys.executable, '-m', 'humansays', CORPUS, '--format', output_format],
        capture_output=True,
        text=True,
        env={'NO_COLOR': '1', 'PATH': '/usr/bin:/bin'},
        check=False,
    )
    assert completed.stdout, completed.stderr
    return completed.stdout


def test_repeated_process_invocations_produce_identical_text() -> None:
    outputs = {scan('text') for _ in range(RUNS)}
    assert len(outputs) == 1, 'text output differs between processes'


def test_repeated_process_invocations_produce_identical_json() -> None:
    outputs = {scan('json') for _ in range(RUNS)}
    assert len(outputs) == 1, 'json output differs between processes'
