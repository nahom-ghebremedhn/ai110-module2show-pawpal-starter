# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🛠️ Implementation Summary

The core logic lives in `pawpal_system.py` as four classes, with `main.py` as a CLI demo:

- **`Task`** — one care activity: description, preferred time (`"HH:MM"` or none), duration, priority (`low`/`medium`/`high`), frequency, and a completed flag. It validates its own fields and converts priority to a numeric score for sorting.
- **`Pet`** — a pet's name and species, plus the list of tasks it needs. Tasks are added and removed through the pet.
- **`Owner`** — holds the owner's pets and how many minutes they have free today. `get_all_tasks()` returns every `(pet, task)` pair across all pets, so nothing downstream has to loop over pets itself.
- **`Scheduler`** — the "brain." Given an owner, `generate_schedule()`:
  1. pulls all incomplete tasks via `owner.get_all_tasks()` and sorts them by priority (shorter tasks first on ties),
  2. keeps taking tasks until the owner's available time runs out, recording the rest in `skipped_tasks` with a reason,
  3. lays the chosen tasks out in order of preferred time, starting each at that time or right after the previous task finishes (tasks with no preferred time go last).

  `explain_schedule()` returns a plain-text reason for every task that was scheduled or skipped.

In short: `Owner` → has many `Pet`s → each has many `Task`s, and `Scheduler` reads from the `Owner` to build the day's plan. Task `frequency` and owner `preferences` are stored but not yet used by the scheduler.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Today's Schedule for Jordan
========================================
08:00  Mochi  Morning walk (30 min, high)
08:30  Luna   Breakfast (10 min, high)
12:30  Luna   Clean litter box (15 min, medium)
18:00  Mochi  Evening walk (30 min, medium)
18:30  Luna   Brush fur (20 min, low)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
