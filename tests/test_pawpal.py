"""Basic tests for the PawPal+ classes."""

from datetime import date, time, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def make_owner(available_time=0, *pets):
    """Return an owner with the given time budget and pets."""
    owner = Owner(name="Jordan", available_time=available_time)
    for pet in pets:
        owner.add_pet(pet)
    return owner


def test_mark_complete_changes_status():
    task = Task("Morning walk", time="08:00")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Breakfast", time="08:00"))

    assert len(pet.tasks) == 1


def test_sort_by_time_orders_tasks_and_puts_untimed_last():
    pet = Pet(name="Luna", species="cat")
    brush = Task("Brush fur")
    litter = Task("Clean litter box", time="12:30")
    breakfast = Task("Breakfast", time="08:00")
    pairs = [(pet, brush), (pet, litter), (pet, breakfast)]

    result = Scheduler(Owner(name="Jordan")).sort_by_time(pairs)

    assert [task for _, task in result] == [breakfast, litter, brush]


def test_filter_tasks_by_pet_name_and_completion_status():
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    walk = Task("Morning walk", time="07:30")
    breakfast = Task("Breakfast", time="08:00")
    litter = Task("Clean litter box", time="12:30")
    mochi.add_task(walk)
    luna.add_task(breakfast)
    luna.add_task(litter)
    breakfast.mark_complete()
    scheduler = Scheduler(owner)

    def tasks(pairs):
        return [task for _, task in pairs]

    assert tasks(scheduler.filter_tasks(pet_name="Luna")) == [breakfast, litter]
    assert tasks(scheduler.filter_tasks(completed=True)) == [breakfast]
    assert tasks(scheduler.filter_tasks(completed=False)) == [walk, litter]
    assert tasks(scheduler.filter_tasks(pet_name="Luna", completed=False)) == [litter]
    assert len(scheduler.filter_tasks()) == 3


def test_completing_daily_task_creates_one_due_tomorrow():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)
    walk = Task("Morning walk", time="07:30", frequency="daily")
    pet.add_task(walk)

    next_walk = Scheduler(owner).mark_task_complete(pet, walk)

    assert walk.completed is True
    assert next_walk is not None
    assert next_walk.completed is False
    assert next_walk.due_date == date.today() + timedelta(days=1)
    assert next_walk.description == "Morning walk" and next_walk.time == "07:30"
    assert pet.tasks == [walk, next_walk]


def test_completing_weekly_task_creates_one_due_next_week():
    owner = Owner(name="Jordan")
    pet = Pet(name="Luna", species="cat")
    owner.add_pet(pet)
    brush = Task("Brush fur", frequency="weekly")
    pet.add_task(brush)

    next_brush = Scheduler(owner).mark_task_complete(pet, brush)

    assert next_brush.due_date == date.today() + timedelta(days=7)


def test_completing_one_off_task_does_not_recur():
    owner = Owner(name="Jordan")
    pet = Pet(name="Luna", species="cat")
    owner.add_pet(pet)
    vet = Task("Vet visit", frequency="once")
    pet.add_task(vet)

    assert Scheduler(owner).mark_task_complete(pet, vet) is None
    assert pet.tasks == [vet]


def test_schedule_skips_tasks_not_yet_due():
    owner = Owner(name="Jordan", available_time=120)
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)
    walk = Task("Morning walk", time="07:30", frequency="daily")
    pet.add_task(walk)
    scheduler = Scheduler(owner)

    scheduler.mark_task_complete(pet, walk)

    assert scheduler.generate_schedule() == []


def test_detect_conflicts_flags_same_time_tasks_across_pets():
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    mochi.add_task(Task("Medication", time="08:00", duration_minutes=5))
    luna.add_task(Task("Breakfast", time="08:00", duration_minutes=10))

    conflicts = Scheduler(owner).detect_conflicts()

    assert len(conflicts) == 1
    assert "different pets" in conflicts[0]


def test_detect_conflicts_flags_overlap_for_same_pet():
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    owner.add_pet(mochi)
    mochi.add_task(Task("Morning walk", time="07:30", duration_minutes=45))
    mochi.add_task(Task("Breakfast", time="08:00", duration_minutes=10))

    conflicts = Scheduler(owner).detect_conflicts()

    assert len(conflicts) == 1
    assert "same pet" in conflicts[0]


def test_detect_conflicts_ignores_back_to_back_and_completed_tasks():
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    owner.add_pet(mochi)
    mochi.add_task(Task("Morning walk", time="07:30", duration_minutes=30))
    mochi.add_task(Task("Breakfast", time="08:00", duration_minutes=10))
    done = Task("Brush teeth", time="08:00", completed=True)
    mochi.add_task(done)

    assert Scheduler(owner).detect_conflicts() == []


def test_detect_conflicts_warns_on_invalid_time_instead_of_crashing():
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    owner.add_pet(mochi)
    mochi.add_task(Task("Walk", time="7:30"))
    mochi.add_task(Task("Dinner", time="25:00"))
    mochi.add_task(Task("Breakfast", time="08:00"))

    conflicts = Scheduler(owner).detect_conflicts()

    assert len(conflicts) == 2
    assert all(warning.startswith("Invalid time") for warning in conflicts)


# --- Sorting correctness ---


def test_generate_schedule_returns_tasks_in_chronological_order_across_pets():
    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner = make_owner(240, mochi, luna)
    mochi.add_task(Task("Evening walk", time="18:00", duration_minutes=30))
    luna.add_task(Task("Breakfast", time="08:00", duration_minutes=10))
    mochi.add_task(Task("Play", duration_minutes=20))
    luna.add_task(Task("Litter box", time="12:30", duration_minutes=10))

    schedule = Scheduler(owner).generate_schedule()

    starts = [start for start, _, _ in schedule]
    assert starts == sorted(starts)
    assert [task.description for _, _, task in schedule] == [
        "Breakfast", "Litter box", "Evening walk", "Play"
    ]


def test_sort_by_time_keeps_original_order_for_identical_times():
    pet = Pet(name="Luna", species="cat")
    first = Task("Breakfast", time="08:00")
    second = Task("Medication", time="08:00")

    result = Scheduler(make_owner()).sort_by_time([(pet, first), (pet, second)])

    assert [task for _, task in result] == [first, second]


def test_sort_by_time_on_empty_list_returns_empty_list():
    assert Scheduler(make_owner()).sort_by_time([]) == []


def test_same_time_tasks_are_scheduled_back_to_back_by_priority():
    mochi = Pet(name="Mochi", species="dog")
    owner = make_owner(60, mochi)
    mochi.add_task(Task("Brush", time="08:00", duration_minutes=10, priority="low"))
    mochi.add_task(Task("Medication", time="08:00", duration_minutes=5, priority="high"))

    schedule = Scheduler(owner).generate_schedule()

    assert [(start, task.description) for start, _, task in schedule] == [
        (time(8, 0), "Medication"),
        (time(8, 5), "Brush"),
    ]


def test_task_preferred_before_day_start_is_moved_to_day_start():
    mochi = Pet(name="Mochi", species="dog")
    owner = make_owner(60, mochi)
    mochi.add_task(Task("Early walk", time="06:00", duration_minutes=20))

    schedule = Scheduler(owner, day_start=time(8, 0)).generate_schedule()

    assert schedule[0][0] == time(8, 0)


# --- Priority and time budget ---


def test_owner_with_no_pets_or_tasks_gets_empty_plan():
    for owner in (make_owner(60), make_owner(60, Pet(name="Mochi", species="dog"))):
        scheduler = Scheduler(owner)
        assert scheduler.generate_schedule() == []
        assert scheduler.detect_conflicts() == []
        assert scheduler.explain_schedule() == ""


def test_zero_available_time_skips_every_task():
    mochi = Pet(name="Mochi", species="dog")
    owner = make_owner(0, mochi)
    mochi.add_task(Task("Walk", duration_minutes=15))
    scheduler = Scheduler(owner)

    assert scheduler.generate_schedule() == []
    assert [reason for _, _, reason in scheduler.skipped_tasks] == [
        "not enough time left today"
    ]


def test_task_that_exactly_fills_available_time_is_scheduled():
    mochi = Pet(name="Mochi", species="dog")
    owner = make_owner(30, mochi)
    mochi.add_task(Task("Walk", duration_minutes=30))

    assert len(Scheduler(owner).generate_schedule()) == 1


def test_high_priority_task_wins_when_time_is_limited():
    mochi = Pet(name="Mochi", species="dog")
    owner = make_owner(20, mochi)
    mochi.add_task(Task("Play", duration_minutes=20, priority="low"))
    mochi.add_task(Task("Medication", duration_minutes=20, priority="high"))
    scheduler = Scheduler(owner)

    schedule = scheduler.generate_schedule()

    assert [task.description for _, _, task in schedule] == ["Medication"]
    assert [task.description for _, task, _ in scheduler.skipped_tasks] == ["Play"]


def test_shorter_task_still_fits_after_a_long_one_is_skipped():
    mochi = Pet(name="Mochi", species="dog")
    owner = make_owner(30, mochi)
    mochi.add_task(Task("Grooming", duration_minutes=60, priority="high"))
    mochi.add_task(Task("Walk", duration_minutes=25, priority="low"))

    schedule = Scheduler(owner).generate_schedule()

    assert [task.description for _, _, task in schedule] == ["Walk"]


# --- Recurrence logic ---


def test_completed_daily_task_reappears_in_tomorrows_plan_not_todays():
    mochi = Pet(name="Mochi", species="dog")
    owner = make_owner(60, mochi)
    walk = Task("Walk", time="07:30", frequency="daily")
    mochi.add_task(walk)
    scheduler = Scheduler(owner)

    next_walk = scheduler.mark_task_complete(mochi, walk)

    assert next_walk.due_date - walk.due_date == timedelta(days=1)
    assert scheduler.filter_tasks(completed=False) == [(mochi, next_walk)]
    assert scheduler.generate_schedule() == []


def test_overdue_daily_task_recurs_from_today_not_from_old_due_date():
    mochi = Pet(name="Mochi", species="dog")
    owner = make_owner(60, mochi)
    walk = Task("Walk", frequency="daily", due_date=date.today() - timedelta(days=3))
    mochi.add_task(walk)

    next_walk = Scheduler(owner).mark_task_complete(mochi, walk)

    assert next_walk.due_date == date.today() + timedelta(days=1)


def test_overdue_incomplete_task_is_still_scheduled_today():
    mochi = Pet(name="Mochi", species="dog")
    owner = make_owner(60, mochi)
    mochi.add_task(Task("Walk", due_date=date.today() - timedelta(days=1)))

    assert len(Scheduler(owner).generate_schedule()) == 1


def test_next_occurrence_is_a_separate_copy():
    walk = Task("Walk", frequency="daily")

    next_walk = walk.next_occurrence()
    next_walk.description = "Changed"

    assert walk.description == "Walk"


# --- Conflict detection ---


def test_three_tasks_at_same_time_produce_a_warning_per_pair():
    mochi = Pet(name="Mochi", species="dog")
    owner = make_owner(0, mochi)
    for name in ("Walk", "Breakfast", "Medication"):
        mochi.add_task(Task(name, time="08:00", duration_minutes=10))

    assert len(Scheduler(owner).detect_conflicts()) == 3


def test_untimed_and_future_tasks_are_not_flagged_as_conflicts():
    mochi = Pet(name="Mochi", species="dog")
    owner = make_owner(0, mochi)
    mochi.add_task(Task("Walk", time="08:00"))
    mochi.add_task(Task("Play"))
    mochi.add_task(Task("Bath", time="08:00", due_date=date.today() + timedelta(days=1)))

    assert Scheduler(owner).detect_conflicts() == []


# --- Regression tests for fixed bugs ---


def test_generate_schedule_does_not_crash_on_invalid_time():
    mochi = Pet(name="Mochi", species="dog")
    owner = make_owner(60, mochi)
    mochi.add_task(Task("Walk", time="noon"))
    scheduler = Scheduler(owner)

    assert scheduler.generate_schedule() == []
    assert "invalid time" in scheduler.skipped_tasks[0][2]


def test_completing_same_task_twice_creates_only_one_next_occurrence():
    mochi = Pet(name="Mochi", species="dog")
    owner = make_owner(0, mochi)
    walk = Task("Walk", frequency="daily")
    mochi.add_task(walk)
    scheduler = Scheduler(owner)

    scheduler.mark_task_complete(mochi, walk)
    scheduler.mark_task_complete(mochi, walk)

    assert len(mochi.tasks) == 2


def test_schedule_does_not_wrap_past_midnight():
    mochi = Pet(name="Mochi", species="dog")
    owner = make_owner(120, mochi)
    mochi.add_task(Task("Late walk", time="23:50", duration_minutes=30))
    mochi.add_task(Task("Play", duration_minutes=10))

    starts = [start for start, _, _ in Scheduler(owner).generate_schedule()]

    assert starts == sorted(starts)
