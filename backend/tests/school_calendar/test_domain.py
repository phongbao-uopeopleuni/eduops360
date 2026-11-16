from dataclasses import FrozenInstanceError
from datetime import time
from uuid import uuid4

import pytest

from app.modules.school_calendar.domain import (
    DayOfWeek,
    ScheduleSlot,
    ScheduleTemplate,
    SchoolSession,
)


def test_weekdays_and_sessions_have_stable_locale_neutral_values() -> None:
    assert [day.value for day in DayOfWeek] == [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    assert [session.value for session in SchoolSession] == ["am", "pm"]


def test_schedule_template_is_scoped_to_exact_school_and_academic_year() -> None:
    school_id = uuid4()
    academic_year_id = uuid4()
    slot = ScheduleSlot(
        day_of_week=DayOfWeek.MONDAY,
        session=SchoolSession.AM,
        start_time=time(7, 0),
        end_time=time(7, 45),
    )

    template = ScheduleTemplate(
        school_id=school_id,
        academic_year_id=academic_year_id,
        slots=(slot,),
    )

    assert template.school_id == school_id
    assert template.academic_year_id == academic_year_id
    assert template.slots == (slot,)


def test_slot_keeps_day_session_and_time_values_without_timezone_conversion() -> None:
    slot = ScheduleSlot(
        day_of_week=DayOfWeek.SUNDAY,
        session=SchoolSession.PM,
        start_time=time(0, 0),
        end_time=time(1, 0),
    )

    assert slot.day_of_week is DayOfWeek.SUNDAY
    assert slot.session is SchoolSession.PM
    assert slot.start_time == time(0, 0)
    assert slot.end_time == time(1, 0)


def test_template_and_slots_are_immutable_domain_values() -> None:
    slot = ScheduleSlot(
        day_of_week=DayOfWeek.FRIDAY,
        session=SchoolSession.AM,
        start_time=time(8, 0),
        end_time=time(8, 45),
    )
    template = ScheduleTemplate(
        school_id=uuid4(),
        academic_year_id=uuid4(),
        slots=(slot,),
    )

    with pytest.raises(FrozenInstanceError):
        slot.start_time = time(9, 0)  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        template.slots = ()  # type: ignore[misc]


@pytest.mark.parametrize("slots", [[], ({"start_time": []},)])
def test_template_rejects_mutable_or_untyped_slots(slots):
    with pytest.raises(TypeError):
        ScheduleTemplate(uuid4(), uuid4(), slots)
