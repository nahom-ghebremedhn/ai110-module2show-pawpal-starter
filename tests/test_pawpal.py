"""Basic tests for the PawPal+ classes."""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


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
