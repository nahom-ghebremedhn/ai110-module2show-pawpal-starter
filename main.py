"""Demo script: build an owner with pets and tasks, then print today's schedule."""

from pawpal_system import Owner, Pet, Scheduler, Task


def print_tasks(title: str, pairs: list[tuple[Pet, Task]]) -> None:
    """Print a titled list of (pet, task) pairs."""
    print(f"\n{title}")
    for pet, task in pairs:
        status = "done" if task.completed else "todo"
        print(f"  {task.time or '--:--'}  {pet.name:<6} {task.description} "
              f"({status}, due {task.due_date})")


def main() -> None:
    owner = Owner(name="Jordan", available_time=120)

    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Tasks are added out of time order on purpose to show sort_by_time().
    mochi.add_task(Task("Evening walk", time="18:00", duration_minutes=30, priority="medium"))
    luna.add_task(Task("Brush fur", duration_minutes=20, priority="low", frequency="weekly"))
    luna.add_task(Task("Clean litter box", time="12:30", duration_minutes=15, priority="medium"))
    mochi.add_task(Task("Morning walk", time="07:30", duration_minutes=30, priority="high"))
    luna.add_task(Task("Breakfast", time="08:00", duration_minutes=10, priority="high"))
    # Same time as Luna's breakfast, to show conflict detection.
    mochi.add_task(Task("Medication", time="08:00", duration_minutes=5, priority="high"))

    scheduler = Scheduler(owner)
    all_tasks = owner.get_all_tasks()

    print_tasks("Tasks as added:", all_tasks)
    print_tasks("Sorted by time:", scheduler.sort_by_time(all_tasks))

    # Brush fur is weekly, so completing it adds a new copy due next week.
    scheduler.mark_task_complete(luna, luna.tasks[0])
    print_tasks("Luna's tasks:", scheduler.filter_tasks(pet_name="Luna"))
    print_tasks("Completed tasks:", scheduler.filter_tasks(completed=True))

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print("\nWarnings:")
        for warning in conflicts:
            print(f"  {warning}")

    schedule = scheduler.generate_schedule()

    print(f"\nToday's Schedule for {owner.name}")
    print("=" * 40)
    for start, pet, task in schedule:
        print(f"{start.strftime('%H:%M')}  {pet.name:<6} {task.description} "
              f"({task.duration_minutes} min, {task.priority})")

    if scheduler.skipped_tasks:
        print("\nSkipped:")
        for pet, task, reason in scheduler.skipped_tasks:
            print(f"  {pet.name:<6} {task.description} - {reason}")


if __name__ == "__main__":
    main()
