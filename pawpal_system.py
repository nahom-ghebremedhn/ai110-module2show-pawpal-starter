"""PawPal+ system skeleton, generated from diagrams/diagrams.mmd."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time
from enum import Enum


class Priority(Enum):
    """Allowed priority levels; the value is the numeric score used for sorting."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class CareTask:
    title: str
    duration_minutes: int
    priority: Priority = Priority.MEDIUM

    def __post_init__(self) -> None:
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        if not isinstance(self.priority, Priority):
            raise TypeError("priority must be a Priority enum value")

    def update_task(self, title: str, duration_minutes: int, priority: Priority) -> None:
        """Update the task's details."""
        pass

    def calculate_priority(self) -> int:
        """Return the numeric priority score used for sorting."""
        return self.priority.value


@dataclass
class Pet:
    name: str
    species: str
    tasks: list[CareTask] = field(default_factory=list)

    def update_info(self, name: str, species: str) -> None:
        """Update the pet's name and species."""
        pass

    def add_task(self, task: CareTask) -> None:
        """Attach a care task to this pet."""
        pass

    def remove_task(self, title: str) -> None:
        """Remove a care task from this pet by title."""
        pass

    def get_pet_info(self) -> str:
        """Return a readable summary of the pet."""
        pass


@dataclass
class Owner:
    name: str
    preferences: dict = field(default_factory=dict)
    available_time: int = 0  # minutes per day; the single source of truth
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.available_time < 0:
            raise ValueError("available_time cannot be negative")

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def set_preferences(self, preferences: dict) -> None:
        """Replace the owner's scheduling preferences."""
        pass

    def set_available_time(self, minutes: int) -> None:
        """Set how many minutes the owner has available today."""
        pass

    def get_all_tasks(self) -> list[tuple[Pet, CareTask]]:
        """Return every (pet, task) pair across all of this owner's pets."""
        pass


@dataclass
class ScheduledTask:
    """A task placed in the daily plan, tied to its pet and a start time."""

    pet: Pet
    task: CareTask
    start_time: time


@dataclass
class SkippedTask:
    """A task left out of the plan, with the reason it was skipped."""

    pet: Pet
    task: CareTask
    reason: str


class Scheduler:
    """Builds a daily plan from the owner's pets, tasks, time, and preferences.

    The plan is recomputed from the owner on every generate_schedule() call,
    so it never goes stale when tasks or available time change.
    """

    def __init__(self, owner: Owner, day_start: time = time(8, 0)) -> None:
        self.owner: Owner = owner
        self.day_start: time = day_start
        self.daily_schedule: list[ScheduledTask] = []
        self.skipped_tasks: list[SkippedTask] = []

    def prioritize_tasks(self) -> list[tuple[Pet, CareTask]]:
        """Return all tasks sorted by priority (highest first), shorter tasks first on ties."""
        pass

    def generate_schedule(self) -> list[ScheduledTask]:
        """Clear the old plan, then fit prioritized tasks into owner.available_time,
        recording anything that doesn't fit in skipped_tasks."""
        pass

    def explain_schedule(self) -> str:
        """Explain why each task was scheduled or skipped."""
        pass
