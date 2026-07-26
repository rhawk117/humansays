from humansays.entrypoint import run_tool


def test_run_tool_returns_zero() -> None:
    assert run_tool() == 0
