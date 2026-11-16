from dataclasses import FrozenInstanceError, replace
from datetime import date, time
from uuid import uuid4

import pytest

from app.modules.school_calendar.domain import DayOfWeek, SchoolSession
from app.modules.timetables.snapshot import (
    ClassGroupLoadSnapshot,
    ClassroomSnapshot,
    HolidaySnapshot,
    MutableSnapshotCollectionError,
    ScheduleSlotSnapshot,
    SchedulingInputSnapshot,
    TeachingAssignmentSnapshot,
)


def build_snapshot() -> SchedulingInputSnapshot:
    class_group_id = uuid4()
    return SchedulingInputSnapshot(
        snapshot_id=uuid4(),
        school_id=uuid4(),
        academic_year_id=uuid4(),
        teaching_assignments=(
            TeachingAssignmentSnapshot(
                assignment_id=uuid4(),
                teacher_id=uuid4(),
                class_group_id=class_group_id,
                subject_id=uuid4(),
                required_weekly_lessons=4,
            ),
        ),
        classrooms=(ClassroomSnapshot(classroom_id=uuid4(), capacity=40),),
        class_group_loads=(
            ClassGroupLoadSnapshot(class_group_id=class_group_id, student_count=35),
        ),
        slots=(
            ScheduleSlotSnapshot(
                slot_id=uuid4(),
                day_of_week=DayOfWeek.MONDAY,
                session=SchoolSession.AM,
                start_time=time(7, 0),
                end_time=time(7, 45),
            ),
        ),
        holidays=(
            HolidaySnapshot(
                holiday_id=uuid4(),
                start_date=date(2026, 11, 16),
                end_date=date(2026, 11, 18),
                start_time=None,
                end_time=None,
            ),
        ),
    )


def test_snapshot_captures_every_required_input_for_one_school_and_year() -> None:
    snapshot = build_snapshot()

    assert snapshot.school_id
    assert snapshot.academic_year_id
    assert len(snapshot.teaching_assignments) == 1
    assert len(snapshot.classrooms) == 1
    assert len(snapshot.class_group_loads) == 1
    assert len(snapshot.slots) == 1
    assert len(snapshot.holidays) == 1


def test_snapshot_and_projection_records_are_immutable() -> None:
    snapshot = build_snapshot()

    with pytest.raises(FrozenInstanceError):
        snapshot.school_id = uuid4()  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        snapshot.teaching_assignments[0].required_weekly_lessons = 5  # type: ignore[misc]


def test_snapshot_rejects_mutable_input_collections() -> None:
    snapshot = build_snapshot()

    with pytest.raises(MutableSnapshotCollectionError):
        SchedulingInputSnapshot(
            snapshot_id=snapshot.snapshot_id,
            school_id=snapshot.school_id,
            academic_year_id=snapshot.academic_year_id,
            teaching_assignments=list(snapshot.teaching_assignments),  # type: ignore[arg-type]
            classrooms=snapshot.classrooms,
            class_group_loads=snapshot.class_group_loads,
            slots=snapshot.slots,
            holidays=snapshot.holidays,
        )


def test_snapshot_preserves_local_time_and_partial_holiday_bounds() -> None:
    snapshot = build_snapshot()
    partial_holiday = HolidaySnapshot(
        holiday_id=uuid4(),
        start_date=date(2026, 11, 20),
        end_date=date(2026, 11, 20),
        start_time=time(0, 0),
        end_time=time(12, 0),
    )

    assert snapshot.slots[0].start_time == time(7, 0)
    assert partial_holiday.start_time == time(0, 0)
    assert partial_holiday.end_time == time(12, 0)


@pytest.mark.parametrize(
    "field", ["teaching_assignments", "classrooms", "class_group_loads", "slots", "holidays"]
)
def test_snapshot_rejects_untyped_nested_elements(field):
    with pytest.raises(TypeError):
        replace(build_snapshot(), **{field: ({"mutable": []},)})


@pytest.mark.parametrize(
    "collection,field",
    [
        ("teaching_assignments", "teacher_id"),
        ("classrooms", "capacity"),
        ("class_group_loads", "student_count"),
        ("slots", "start_time"),
        ("holidays", "end_time"),
    ],
)
def test_snapshot_leaf_records_reject_mutable_scalar_values(collection, field):
    record = getattr(build_snapshot(), collection)[0]
    with pytest.raises(TypeError):
        replace(record, **{field: []})
