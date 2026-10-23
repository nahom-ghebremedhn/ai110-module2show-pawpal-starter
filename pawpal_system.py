"""PawPal+ system skeleton, generated from diagrams/diagrams.mmd."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Pet:
    name: str
    species: str

    def update_info(self, name: str, species: str) -> None:
        """Update the pet's name and species."""
        pass

    def get_pet_info(self) -> str:
        """Return a readable summary of the pet."""
        pass


@dataclass
class CareTask:
    title: str
    duration_minutes: int
    priority: str  # e.g. "low", "medium", "high"

    def update_task(self, title: str, duration_minutes: int, priority: str) -> None:
        """Update the task's details."""
        pass

    def calculate_priority(self) -> int:
        """Convert the priority label into a numeric score for sorting."""
        pass


@dataclass
class Owner:
    name: str
    preferences: dict = field(default_factory=dict)
    available_time: int = 0  # minutes per day
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def set_preferences(self, preferences: dict) -> None:
        """Replace the owner's scheduling preferences."""
        pass

    def set_available_time(self, minutes: int) -> None:
        """Set how many minutes the owner has available today."""
        pass


class Scheduler:
    def __init__(self, tasks: list[CareTask] | None = None, available_time: int = 0) -> None:
        self.tasks: list[CareTask] = tasks if tasks is not None else []
        self.daily_schedule: list[CareTask] = []
        self.available_time: int = available_time

    def generate_schedule(self) -> list[CareTask]:
        """Build the daily schedule from tasks that fit in the available time."""
        pass

    def prioritize_tasks(self) -> list[CareTask]:
        """Return tasks sorted by priority (highest first)."""
        pass

    def explain_schedule(self) -> str:
        """Explain why tasks were included or left out of the schedule."""
        pass
