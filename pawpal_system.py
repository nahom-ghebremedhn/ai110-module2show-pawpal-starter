"""PawPal+ system skeleton, generated from diagrams/uml.mmd."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta

# Allowed priority levels; the value is the numeric score used for sorting.
PRIORITY_SCORES = {"low": 1, "medium": 2, "high": 3}
FREQUENCIES = ("once", "daily", "weekly")


@dataclass
class Task:
    """A single care activity for a pet."""

    description: str
    time: str | None = None  # preferred start as "HH:MM"; None means any time
    frequency: str = "daily"
    completed: bool = False
    duration_minutes: int = 15
    priority: str = "medium"

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
        """Return incomplete tasks sorted by priority, shortest first on ties."""
        pending = [(p, t) for p, t in self.owner.get_all_tasks() if not t.completed]
        return sorted(
            pending, key=lambda pt: (-pt[1].calculate_priority(), pt[1].duration_minutes)
        )

    def generate_schedule(self) -> list[tuple[time, Pet, Task]]:
        """Rebuild today's plan within available_time, recording skipped tasks."""
        self.daily_schedule = []
        self.skipped_tasks = []

        # Pick tasks by priority until the owner's time budget runs out.
        chosen: list[tuple[Pet, Task]] = []
        remaining = self.owner.available_time
        for pet, task in self.prioritize_tasks():
            if task.duration_minutes <= remaining:
                chosen.append((pet, task))
                remaining -= task.duration_minutes
            else:
                self.skipped_tasks.append((pet, task, "not enough time left today"))

        # Lay chosen tasks out in time order; tasks without a preferred time go last.
        chosen.sort(key=lambda pt: (pt[1].time is None, pt[1].time or ""))
        today = datetime.today().date()
        cursor = datetime.combine(today, self.day_start)
        for pet, task in chosen:
            if task.time is not None:
                preferred = datetime.combine(today, time.fromisoformat(task.time))
                cursor = max(cursor, preferred)
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
