from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from multiprocessing import Process, Queue
from pathlib import Path

import pytest

from lib.resource_lease import LeaseConflictError, ResourceLease


def test_conflicting_local_lane_cannot_be_acquired(tmp_path: Path) -> None:
    lock = tmp_path / "local-resource.lease"
    text = ResourceLease(lock, lane="local_text", owner="task-research", ttl_seconds=60)
    text.acquire()

    media = ResourceLease(lock, lane="local_media", owner="task-render", ttl_seconds=60)
    with pytest.raises(LeaseConflictError, match="task-research"):
        media.acquire()

    text.release()
    media.acquire()
    media.release()


def _try_acquire(lock: str, owner: str, output: Queue) -> None:
    lease = ResourceLease(Path(lock), lane="local_text", owner=owner, ttl_seconds=60)
    try:
        lease.acquire()
    except LeaseConflictError:
        output.put("conflict")
    else:
        output.put("acquired")


def test_atomic_create_allows_only_one_concurrent_owner(tmp_path: Path) -> None:
    lock = tmp_path / "race.lease"
    output: Queue = Queue()
    workers = [
        Process(target=_try_acquire, args=(str(lock), f"owner-{index}", output))
        for index in range(4)
    ]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(timeout=5)
        assert worker.exitcode == 0

    results = sorted(output.get(timeout=1) for _ in workers)
    assert results.count("acquired") == 1
    assert results.count("conflict") == 3


def test_expired_lease_requires_explicit_recovery(tmp_path: Path) -> None:
    lock = tmp_path / "expired.lease"
    expired = datetime.now(timezone.utc) - timedelta(minutes=5)
    lock.write_text(
        json.dumps(
            {
                "version": "1.0",
                "lane": "local_text",
                "owner": "dead-task",
                "acquired_at": expired.isoformat(),
                "expires_at": expired.isoformat(),
                "pid": 999999,
            }
        ),
        encoding="utf-8",
    )

    lease = ResourceLease(lock, lane="local_media", owner="coordinator", ttl_seconds=60)
    with pytest.raises(LeaseConflictError, match="expired"):
        lease.acquire()

    recovered = lease.recover_expired(authority="control")
    assert recovered["owner"] == "dead-task"
    lease.acquire()
    lease.release()


def test_only_control_can_recover_expired_lease(tmp_path: Path) -> None:
    lock = tmp_path / "expired.lease"
    expired = datetime.now(timezone.utc) - timedelta(minutes=1)
    lock.write_text(
        json.dumps(
            {
                "version": "1.0",
                "lane": "local_text",
                "owner": "dead-task",
                "acquired_at": expired.isoformat(),
                "expires_at": expired.isoformat(),
                "pid": 999999,
            }
        ),
        encoding="utf-8",
    )

    lease = ResourceLease(lock, lane="local_media", owner="qa", ttl_seconds=60)
    with pytest.raises(PermissionError, match="control"):
        lease.recover_expired(authority="qa")

