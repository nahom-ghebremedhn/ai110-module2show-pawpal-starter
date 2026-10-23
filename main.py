"""Demo script: build an owner with pets and tasks, then print today's schedule."""

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner(name="Jordan", available_time=120)

    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Morning walk", time="07:30", duration_minutes=30, priority="high"))
    mochi.add_task(Task("Evening walk", time="18:00", duration_minutes=30, priority="medium"))
    luna.add_task(Task("Breakfast", time="08:00", duration_minutes=10, priority="high"))
    luna.add_task(Task("Clean litter box", time="12:30", duration_minutes=15, priority="medium"))
    luna.add_task(Task("Brush fur", duration_minutes=20, priority="low", frequency="weekly"))

    scheduler = Scheduler(owner)
    schedule = scheduler.generate_schedule()

    print(f"Today's Schedule for {owner.name}")
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
