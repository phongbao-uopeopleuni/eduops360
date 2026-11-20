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
