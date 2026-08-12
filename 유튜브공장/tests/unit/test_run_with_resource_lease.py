from __future__ import annotations

from pathlib import Path

from scripts.orca.run_with_resource_lease import run_with_lease


def test_wrapper_holds_lease_during_command_and_releases_afterward(
    tmp_path: Path,
) -> None:
    lock = tmp_path / "resource.lease"
    observations: list[tuple[list[str], bool]] = []

    def runner(command: list[str]) -> int:
        observations.append((command, lock.is_file()))
        return 7

    result = run_with_lease(
        lock,
        lane="local_text",
        owner="task-1",
        command=["fake", "--flag"],
        runner=runner,
    )

    assert result == 7
    assert observations == [(["fake", "--flag"], True)]
    assert not lock.exists()

