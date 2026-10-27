"""PawPal+ system skeleton, generated from diagrams/uml.mmd."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, datetime, time, timedelta

# Allowed priority levels; the value is the numeric score used for sorting.
PRIORITY_SCORES = {"low": 1, "medium": 2, "high": 3}
FREQUENCIES = ("once", "daily", "weekly")
# Days until the next occurrence of a recurring task.
RECURRENCE_DAYS = {"daily": 1, "weekly": 7}


@dataclass
class Task:
    """A single care activity for a pet."""

    description: str
    time: str | None = None  # preferred start as "HH:MM"; None means any time
    frequency: str = "daily"
    completed: bool = False
    duration_minutes: int = 15
    priority: str = "medium"
    due_date: date = field(default_factory=date.today)

    def __post_init__(self) -> None:
        """Validate duration, priority, and frequency."""
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        if self.priority not in PRIORITY_SCORES:
            raise ValueError(f"priority must be one of {list(PRIORITY_SCORES)}")
        if self.frequency not in FREQUENCIES:
            raise ValueError(f"frequency must be one of {list(FREQUENCIES)}")

    def update_task(
        self,
        description: str,
        time: str | None,
        frequency: str,
        duration_minutes: int,
        priority: str,
    ) -> None:
        """Update the task's details."""
        self.description = description
        self.time = time
        self.frequency = frequency
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.__post_init__()

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self) -> Task | None:
        """Return a fresh copy due on the next occurrence, or None for one-off tasks.

        The new due date is computed with timedelta: +1 day for "daily" tasks and
        +7 days for "weekly" tasks (see RECURRENCE_DAYS). It counts from today if
        the task was overdue, so finishing a late task never creates a copy that
        is already due.

        Returns:
            A new, incomplete Task with the same details and the next due date,
            or None if the task's frequency is "once".
        """
        if self.frequency not in RECURRENCE_DAYS:
            return None
        base = max(self.due_date, date.today())
        return replace(
            self,
            completed=False,
            due_date=base + timedelta(days=RECURRENCE_DAYS[self.frequency]),
        )

    def calculate_priority(self) -> int:
        """Return the numeric priority score used for sorting."""
        return PRIORITY_SCORES[self.priority]


@dataclass
class Pet:
    """A pet's details and the care tasks it needs."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def update_info(self, name: str, species: str) -> None:
        """Update the pet's name and species."""
        self.name = name
        self.species = species

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, description: str) -> None:
        """Remove a care task from this pet by description."""
        self.tasks = [t for t in self.tasks if t.description != description]

    def get_pet_info(self) -> str:
        """Return a readable summary of the pet."""
        return f"{self.name} ({self.species}) - {len(self.tasks)} task(s)"


@dataclass
class Owner:
    """Manages multiple pets and gives access to all of their tasks."""

    name: str
    preferences: dict = field(default_factory=dict)
    available_time: int = 0  # minutes per day; the single source of truth
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate that available_time is not negative."""
        if self.available_time < 0:
            raise ValueError("available_time cannot be negative")

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def set_preferences(self, preferences: dict) -> None:
        """Replace the owner's scheduling preferences."""
        self.preferences = dict(preferences)

    def set_available_time(self, minutes: int) -> None:
        """Set how many minutes the owner has available today."""
        if minutes < 0:
            raise ValueError("available_time cannot be negative")
        self.available_time = minutes

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair across all of this owner's pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


@dataclass
class Conflict:
    """Two due tasks whose preferred time windows overlap."""

    first_pet: Pet
    first_task: Task  # the task that starts earlier
    second_pet: Pet
    second_task: Task
    first_end: int  # minutes since midnight when first_task ends
    overlap_minutes: int

    @property
    def same_pet(self) -> bool:
        """True when both tasks belong to the same pet."""
        return self.first_pet is self.second_pet

    def suggested_time(self) -> str | None:
        """Return the earliest "HH:MM" the second task could start without overlap."""
        if self.first_end >= 24 * 60:
            return None
        return f"{self.first_end // 60:02d}:{self.first_end % 60:02d}"


class Scheduler:
    """The "brain": retrieves, organizes, and manages tasks across all pets.

    Tasks are always read through owner.get_all_tasks(), never from a single
    pet, so every pet the owner has is included. The plan is recomputed on
    every generate_schedule() call, so it never goes stale.
    """

    def __init__(self, owner: Owner, day_start: time = time(8, 0)) -> None:
        """Create a scheduler for an owner, starting the day at day_start."""
        self.owner: Owner = owner
        self.day_start: time = day_start
        # Each entry is (start_time, pet, task).
        self.daily_schedule: list[tuple[time, Pet, Task]] = []
        # Each entry is (pet, task, reason it was skipped).
        self.skipped_tasks: list[tuple[Pet, Task, str]] = []

    def prioritize_tasks(self) -> list[tuple[Pet, Task]]:
        """Return incomplete tasks due by today, by priority, shortest first on ties."""
        today = date.today()
        pending = [
            (p, t)
            for p, t in self.owner.get_all_tasks()
            if not t.completed and t.due_date <= today
        ]
        return sorted(
            pending, key=lambda pt: (-pt[1].calculate_priority(), pt[1].duration_minutes)
        )

    def sort_by_time(self, tasks: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs in preferred-time order; untimed tasks go last.

        Uses sorted() with a lambda key of (time is None, time or ""). Python
        compares the tuples item by item: False sorts before True, so timed tasks
        come first, then zero-padded "HH:MM" strings sort correctly as text.

        Args:
            tasks: The (pet, task) pairs to sort. The list is not modified.

        Returns:
            A new list of the same pairs in time order.
        """
        return sorted(tasks, key=lambda pt: (pt[1].time is None, pt[1].time or ""))

    def filter_tasks(
        self, pet_name: str | None = None, completed: bool | None = None
    ) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs matching the given filters; None skips a filter.

        Args:
            pet_name: Only include tasks for the pet with this exact name.
            completed: True for finished tasks only, False for unfinished only.

        Returns:
            Matching pairs from every pet, in the order they were added. With no
            filters, every task is returned.
        """
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if (pet_name is None or pet.name == pet_name)
            and (completed is None or task.completed == completed)
        ]

    def find_conflicts(self) -> tuple[list[Conflict], list[tuple[Pet, Task]]]:
        """Return overlapping task pairs and tasks whose time is not valid "HH:MM".

        Only incomplete tasks due today that have a preferred time are checked.
        Times are converted to minutes since midnight and sorted by start. Two
        tasks overlap when the later one starts before the earlier one ends;
        because the list is sorted, the inner loop stops at the first task that
        starts after the current one ends.

        Returns:
            A (conflicts, invalid) pair: Conflict objects in start-time order,
            and the (pet, task) pairs whose time could not be parsed.
        """
        conflicts = []
        invalid = []
        timed = []
        for pet, task in self.prioritize_tasks():
            if task.time is None:
                continue
            try:
                start_time = time.fromisoformat(task.time)
            except ValueError:
                invalid.append((pet, task))
                continue
            start = start_time.hour * 60 + start_time.minute
            timed.append((start, start + task.duration_minutes, pet, task))
        timed.sort(key=lambda entry: entry[0])

        for i, (start, end, pet, task) in enumerate(timed):
            for other_start, other_end, other_pet, other_task in timed[i + 1:]:
                if other_start >= end:
                    break
                conflicts.append(
                    Conflict(
                        first_pet=pet,
                        first_task=task,
                        second_pet=other_pet,
                        second_task=other_task,
                        first_end=end,
                        overlap_minutes=min(end, other_end) - other_start,
                    )
                )
        return conflicts, invalid

    def detect_conflicts(self) -> list[str]:
        """Return a warning string for each conflict or invalid time.

        A lightweight check that warns instead of raising, so the schedule can
        still be built. See find_conflicts() for the structured version.

        Returns:
            Warning strings, each noting whether the overlap is for the same pet
            or different pets. An empty list means no conflicts.
        """
        conflicts, invalid = self.find_conflicts()
        warnings = [
            f"Invalid time: {pet.name}'s {task.description} has time "
            f"'{task.time}' (expected HH:MM); skipped"
            for pet, task in invalid
        ]
        for c in conflicts:
            scope = "same pet" if c.same_pet else "different pets"
            warnings.append(
                f"Conflict ({scope}): {c.first_pet.name}'s {c.first_task.description} "
                f"at {c.first_task.time} overlaps {c.second_pet.name}'s "
                f"{c.second_task.description} at {c.second_task.time}"
            )
        return warnings

    def mark_task_complete(self, pet: Pet, task: Task) -> Task | None:
        """Complete a pet's task and add its next occurrence if it recurs.

        Use this instead of task.mark_complete() so daily and weekly tasks
        repeat automatically.

        Args:
            pet: The pet the task belongs to; the next occurrence is added here.
            task: The task to mark complete.

        Returns:
            The newly created next occurrence, or None for a one-off task or a
            task that was already completed.
        """
        if task.completed:
            return None
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            pet.add_task(next_task)
        return next_task

    def generate_schedule(self) -> list[tuple[time, Pet, Task]]:
        """Rebuild today's plan within available_time, recording skipped tasks."""
        self.daily_schedule = []
        self.skipped_tasks = []

        # Pick tasks by priority until the owner's time budget runs out.
        chosen: list[tuple[Pet, Task]] = []
        remaining = self.owner.available_time
        for pet, task in self.prioritize_tasks():
            if task.time is not None:
                try:
                    time.fromisoformat(task.time)
                except ValueError:
                    self.skipped_tasks.append(
                        (pet, task, f"invalid time '{task.time}' (expected HH:MM)")
                    )
                    continue
            if task.duration_minutes <= remaining:
                chosen.append((pet, task))
                remaining -= task.duration_minutes
            else:
                self.skipped_tasks.append((pet, task, "not enough time left today"))

        # Lay chosen tasks out in time order; tasks without a preferred time go last.
        chosen = self.sort_by_time(chosen)
        today = datetime.today().date()
        cursor = datetime.combine(today, self.day_start)
        for pet, task in chosen:
            if task.time is not None:
                preferred = datetime.combine(today, time.fromisoformat(task.time))
                cursor = max(cursor, preferred)
            if cursor.date() > today:
                self.skipped_tasks.append((pet, task, "no time left before midnight"))
                continue
            self.daily_schedule.append((cursor.time(), pet, task))
            cursor += timedelta(minutes=task.duration_minutes)

        return self.daily_schedule

    def explain_schedule(self) -> str:
        """Explain why each task was scheduled or skipped."""
        lines = []
        for start, pet, task in self.daily_schedule:
            lines.append(
                f"{start.strftime('%H:%M')} {pet.name}: {task.description} "
                f"scheduled ({task.priority} priority, {task.duration_minutes} min)"
            )
        for pet, task, reason in self.skipped_tasks:
            lines.append(f"{pet.name}: {task.description} skipped - {reason}")
        return "\n".join(lines)
