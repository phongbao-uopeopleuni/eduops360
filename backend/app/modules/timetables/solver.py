"""CP-SAT timetable model and independent validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from ortools.sat.python import cp_model


class SolverStatus(StrEnum):
    OPTIMAL = "optimal"
    FEASIBLE = "feasible"
    INFEASIBLE = "infeasible"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class TeachingAssignment:
    assignment_id: str
    teacher_id: str
    class_id: str
    subject_id: str
    room_id: str | None
    required_lessons: int


@dataclass(frozen=True)
class AvailableSlot:
    slot_id: str
    weekday: int
    start_minute: int
    end_minute: int


@dataclass(frozen=True)
class ScheduleEntry:
    assignment_id: str
    teacher_id: str
    class_id: str
    subject_id: str
    room_id: str | None
    slot_id: str
    weekday: int
    start_minute: int
    end_minute: int


@dataclass(frozen=True)
class Snapshot:
    school_id: str
    academic_year_id: str
    assignments: tuple[TeachingAssignment, ...]
    slots: tuple[AvailableSlot, ...]
    closed_slots: frozenset[str] = frozenset()


def prevalidate_snapshot(snapshot: Snapshot) -> str | None:
    if not snapshot.assignments:
        return "NO_TEACHING_ASSIGNMENTS"
    if not snapshot.slots:
        return "NO_AVAILABLE_SLOTS"
    for assignment in snapshot.assignments:
        if assignment.required_lessons < 1:
            return f"{assignment.assignment_id}:INVALID_REQUIRED_LESSONS"
    available_slots = [
        slot.slot_id for slot in snapshot.slots if slot.slot_id not in snapshot.closed_slots
    ]
    if not available_slots:
        return "NO_OPEN_SLOTS"
    for class_id in {assignment.class_id for assignment in snapshot.assignments}:
        required = sum(
            assignment.required_lessons
            for assignment in snapshot.assignments
            if assignment.class_id == class_id
        )
        if required > len(available_slots):
            return f"{class_id}:LOWER_BOUND_SLOT_INSUFFICIENT"
    return None


def map_solver_status(status: cp_model.CpSolverStatus) -> SolverStatus:
    if status == cp_model.OPTIMAL:
        return SolverStatus.OPTIMAL
    if status == cp_model.FEASIBLE:
        return SolverStatus.FEASIBLE
    if status == cp_model.INFEASIBLE:
        return SolverStatus.INFEASIBLE
    return SolverStatus.UNKNOWN


def solve_timetable(
    snapshot: Snapshot,
    *,
    time_limit_seconds: float = 10.0,
    random_seed: int = 360,
) -> tuple[SolverStatus, list[ScheduleEntry], dict[str, Any]]:
    preflight_error = prevalidate_snapshot(snapshot)
    if preflight_error:
        return (
            SolverStatus.INFEASIBLE,
            [],
            {
                "reason": preflight_error,
                "objective": None,
                "elapsed_seconds": 0.0,
            },
        )

    model = cp_model.CpModel()
    variables: dict[tuple[str, str], Any] = {}
    open_slots = [slot for slot in snapshot.slots if slot.slot_id not in snapshot.closed_slots]

    for assignment in snapshot.assignments:
        for slot in open_slots:
            variables[(assignment.assignment_id, slot.slot_id)] = model.new_bool_var(
                f"x_{assignment.assignment_id}_{slot.slot_id}"
            )
        model.add(
            sum(variables[(assignment.assignment_id, slot.slot_id)] for slot in open_slots)
            == assignment.required_lessons
        )

    for slot in open_slots:
        class_assignments = [
            assignment
            for assignment in snapshot.assignments
            if any(variables[(assignment.assignment_id, slot.slot_id)].name for _ in (0,))
        ]
        for class_id in {assignment.class_id for assignment in class_assignments}:
            model.add(
                sum(
                    variables[(assignment.assignment_id, slot.slot_id)]
                    for assignment in snapshot.assignments
                    if assignment.class_id == class_id
                )
                <= 1
            )
        for teacher_id in {assignment.teacher_id for assignment in class_assignments}:
            model.add(
                sum(
                    variables[(assignment.assignment_id, slot.slot_id)]
                    for assignment in snapshot.assignments
                    if assignment.teacher_id == teacher_id
                )
                <= 1
            )
        room_assignments = {
            assignment.room_id for assignment in class_assignments if assignment.room_id is not None
        }
        for room_id in room_assignments:
            model.add(
                sum(
                    variables[(assignment.assignment_id, slot.slot_id)]
                    for assignment in snapshot.assignments
                    if assignment.room_id == room_id
                )
                <= 1
            )

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max(0.1, min(time_limit_seconds, 300.0))
    solver.parameters.random_seed = random_seed
    solver.parameters.num_search_workers = 1
    status = solver.solve(model)
    mapped = map_solver_status(status)
    elapsed = float(solver.wall_time)
    if mapped not in {SolverStatus.OPTIMAL, SolverStatus.FEASIBLE}:
        return (
            mapped,
            [],
            {
                "reason": "NO_SOLUTION_RETURNED" if mapped == SolverStatus.UNKNOWN else None,
                "objective": None,
                "elapsed_seconds": elapsed,
            },
        )

    entries: list[ScheduleEntry] = []
    assignment_by_id = {assignment.assignment_id: assignment for assignment in snapshot.assignments}
    slot_by_id = {slot.slot_id: slot for slot in open_slots}
    for (assignment_id, slot_id), variable in variables.items():
        if solver.value(variable):
            assignment = assignment_by_id[assignment_id]
            slot = slot_by_id[slot_id]
            entries.append(
                ScheduleEntry(
                    assignment_id=assignment.assignment_id,
                    teacher_id=assignment.teacher_id,
                    class_id=assignment.class_id,
                    subject_id=assignment.subject_id,
                    room_id=assignment.room_id,
                    slot_id=slot.slot_id,
                    weekday=slot.weekday,
                    start_minute=slot.start_minute,
                    end_minute=slot.end_minute,
                )
            )

    entries.sort(key=lambda item: (item.weekday, item.start_minute, item.class_id))
    validation_error = validate_schedule_entries(entries)
    if validation_error:
        return (
            SolverStatus.UNKNOWN,
            [],
            {
                "reason": f"POST_SOLVE_VALIDATION_FAILED:{validation_error}",
                "objective": None,
                "elapsed_seconds": elapsed,
            },
        )
    return (
        mapped,
        entries,
        {
            "reason": None,
            "objective": float(solver.objective_value),
            "elapsed_seconds": elapsed,
        },
    )


def validate_schedule_entries(entries: list[ScheduleEntry]) -> str | None:
    seen_class_slots: set[tuple[str, str]] = set()
    seen_teacher_slots: set[tuple[str, str]] = set()
    seen_room_slots: set[tuple[str, str]] = set()
    for entry in entries:
        slot_key = (entry.slot_id, str(entry.weekday))
        class_key = (entry.class_id, slot_key[0])
        if class_key in seen_class_slots:
            return f"CLASS_COLLISION:{entry.class_id}:{entry.slot_id}"
        seen_class_slots.add(class_key)

        teacher_key = (entry.teacher_id, slot_key[0])
        if teacher_key in seen_teacher_slots:
            return f"TEACHER_COLLISION:{entry.teacher_id}:{entry.slot_id}"
        seen_teacher_slots.add(teacher_key)

        if entry.room_id:
            room_key = (entry.room_id, slot_key[0])
            if room_key in seen_room_slots:
                return f"ROOM_COLLISION:{entry.room_id}:{entry.slot_id}"
            seen_room_slots.add(room_key)
    return None
