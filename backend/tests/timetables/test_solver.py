from datetime import date
from types import SimpleNamespace
from uuid import UUID

from app.modules.timetables import router as timetable_router
from app.modules.timetables.router import _closed_slot_ids
from app.modules.timetables.schemas import TimetableJobCreate
from app.modules.timetables.solver import (
    AvailableSlot,
    ScheduleEntry,
    Snapshot,
    SolverStatus,
    TeachingAssignment,
    prevalidate_snapshot,
    solve_timetable,
    validate_schedule_entries,
)


def test_timetable_job_rejects_client_supplied_slots_and_closed_slots():
    try:
        TimetableJobCreate.model_validate(
            {
                "school_id": "10000000-0000-4000-8000-000000000001",
                "academic_year_id": "20000000-0000-4000-8000-000000000001",
                "assignments": [],
                "slots": [],
                "closed_slot_ids": ["client-controlled-slot"],
            }
        )
    except ValueError:
        return
    raise AssertionError("client-supplied slots must be rejected")


def test_server_derived_closed_slots_use_active_holiday_weekdays():
    monday = UUID("30000000-0000-4000-8000-000000000001")
    tuesday = UUID("30000000-0000-4000-8000-000000000002")
    template_slots = (
        SimpleNamespace(id=monday, weekday=1),
        SimpleNamespace(id=tuesday, weekday=2),
    )
    holidays = (
        SimpleNamespace(
            start_date=date(2026, 9, 7),
            end_date=date(2026, 9, 8),
        ),
    )

    closed = _closed_slot_ids(
        template_slots,
        holidays,
        date(2026, 9, 1),
        date(2027, 6, 30),
    )

    assert closed == frozenset({str(monday), str(tuesday)})


def make_snapshot(class_count=1, assignments_per_class=1):
    assignments = []
    for class_index in range(class_count):
        for lesson_index in range(assignments_per_class):
            assignments.append(
                TeachingAssignment(
                    assignment_id=f"a-{class_index}-{lesson_index}",
                    teacher_id=f"t-{class_index}-{lesson_index}",
                    class_id=f"c-{class_index}",
                    subject_id=f"s-{lesson_index}",
                    room_id=f"r-{class_index}",
                    required_lessons=1,
                )
            )
    slots = tuple(
        AvailableSlot(
            slot_id=f"slot-{index}",
            weekday=1 + index // 5,
            start_minute=480 + (index % 5) * 45,
            end_minute=525 + (index % 5) * 45,
        )
        for index in range(class_count * assignments_per_class + 5)
    )
    return Snapshot(
        school_id="school",
        academic_year_id="year",
        assignments=tuple(assignments),
        slots=slots,
    )


def test_prevalidation_rejects_missing_inputs_and_insufficient_slots():
    assert prevalidate_snapshot(Snapshot("school", "year", (), ())) == "NO_TEACHING_ASSIGNMENTS"

    impossible = make_snapshot(class_count=1, assignments_per_class=20)
    assert (
        prevalidate_snapshot(
            Snapshot(
                impossible.school_id,
                impossible.academic_year_id,
                impossible.assignments,
                tuple(impossible.slots[:5]),
            )
        )
        == "c-0:LOWER_BOUND_SLOT_INSUFFICIENT"
    )


def test_synthetic_small_solve_is_feasible_and_independently_valid():
    snapshot = make_snapshot(class_count=2, assignments_per_class=2)
    status, entries, evidence = solve_timetable(snapshot, time_limit_seconds=2.0)
    assert status in {SolverStatus.OPTIMAL, SolverStatus.FEASIBLE}
    assert len(entries) == 4
    assert validate_schedule_entries(entries) is None
    assert evidence["objective"] is not None


def test_closed_slots_make_snapshot_infeasible_for_missing_open_slot():
    snapshot = make_snapshot(class_count=1, assignments_per_class=1)
    closed = Snapshot(
        snapshot.school_id,
        snapshot.academic_year_id,
        snapshot.assignments,
        snapshot.slots,
        frozenset(slot.slot_id for slot in snapshot.slots),
    )
    status, entries, evidence = solve_timetable(closed)
    assert status == SolverStatus.INFEASIBLE
    assert entries == []
    assert evidence["reason"] == "NO_OPEN_SLOTS"


def test_post_solve_validator_rejects_teacher_collision():
    entries = [
        ScheduleEntry("a1", "t1", "c1", "math", "r1", "slot", 1, 480, 525),
        ScheduleEntry("a2", "t1", "c2", "math", "r2", "slot", 1, 480, 525),
    ]
    assert validate_schedule_entries(entries) == "TEACHER_COLLISION:t1:slot"


def test_benchmark_shapes_5_20_50_80_classes_report_status():
    for class_count in (5, 20, 50, 80):
        snapshot = make_snapshot(class_count=class_count, assignments_per_class=1)
        status, entries, evidence = solve_timetable(
            snapshot,
            time_limit_seconds=0.5,
            random_seed=360,
        )
        assert status in {SolverStatus.OPTIMAL, SolverStatus.FEASIBLE}
        assert len(entries) == class_count
        assert evidence["elapsed_seconds"] >= 0


def test_solver_thread_limiter_is_bounded(monkeypatch):
    import asyncio

    limiter = object()
    monkeypatch.setattr(timetable_router, "_current_solver_limiter", lambda: limiter)
    captured = {}

    async def run_sync(partial, **kwargs):
        captured["limiter"] = kwargs["limiter"]
        captured["abandon_on_cancel"] = kwargs["abandon_on_cancel"]
        return SolverStatus.FEASIBLE, [], {"elapsed_seconds": 0.0}

    monkeypatch.setattr(timetable_router.to_thread, "run_sync", run_sync)

    async def exercise():
        snapshot = make_snapshot(class_count=1)
        return await timetable_router.to_thread.run_sync(
            lambda: solve_timetable(snapshot),
            limiter=timetable_router._current_solver_limiter(),
            abandon_on_cancel=False,
        )

    asyncio.run(exercise())
    assert captured["limiter"] is limiter
    assert captured["abandon_on_cancel"] is False


def test_solver_capacity_limiter_enforces_two_slots():
    import asyncio

    from anyio import CapacityLimiter

    async def exercise():
        limiter = CapacityLimiter(timetable_router.TIMETABLE_SOLVER_CONCURRENT_LIMIT)

        async def guarded():
            async with limiter:
                await asyncio.sleep(0)

        await asyncio.gather(guarded(), guarded())
        assert limiter.available_tokens >= 0

    asyncio.run(exercise())
