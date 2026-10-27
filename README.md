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

In short: `Owner` → has many `Pet`s → each has many `Task`s, and `Scheduler` reads from the `Owner` to build the day's plan. Task `frequency` drives recurring tasks (see Smarter Scheduling); owner `preferences` are stored but not yet used by the scheduler.

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
python -m pytest
```

The 31 tests in `tests/test_pawpal.py` cover:

- **Sorting:** tasks come back in time order, with untimed tasks last.
- **Recurrence:** completing a daily or weekly task adds a copy due 1 or 7 days later; one-off tasks don't repeat.
- **Conflict detection:** overlapping or same-time tasks are flagged, for the same pet or across pets.
- **Scheduling limits:** higher priority wins when time is short, and tasks that don't fit are skipped with a reason.
- **Edge cases:** no pets or tasks, invalid times, completing a task twice, and plans that would run past midnight.

Sample test output:

```
========================================================== test session starts ==========================================================
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\bibia\ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 31 items                                                                                                                       

tests\test_pawpal.py ...............................                                                                               [100%]

========================================================== 31 passed in 0.09s ===========================================================
```

## 📐 Smarter Scheduling

Four features build on the basic scheduler. All of them are in `pawpal_system.py`, demonstrated in `main.py` and covered by tests in `tests/test_pawpal.py`.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | By preferred `"HH:MM"` time; tasks with no time go last |
| Filtering | `Scheduler.filter_tasks()` | By pet name, completion status or both |
| Conflict handling | `Scheduler.detect_conflicts()` | Warns about overlapping times instead of crashing |
| Recurring tasks | `Scheduler.mark_task_complete()`, `Task.next_occurrence()` | Daily tasks repeat the next day, weekly tasks 7 days later |

### Sorting: `Scheduler.sort_by_time(tasks)`

Returns `(pet, task)` pairs in order of preferred time, across all pets. It uses `sorted()` with a lambda key, `(task.time is None, task.time or "")`:

- The first part puts tasks that have a time before tasks that don't.
- The second part orders the timed tasks by their `"HH:MM"` string. Zero-padded times sort correctly as plain text (`"07:30"` < `"12:30"`).

It returns a new list and leaves the input unchanged. `generate_schedule()` uses it to lay out the day.

### Filtering: `Scheduler.filter_tasks(pet_name=None, completed=None)`

Returns the `(pet, task)` pairs that match the filters you pass. A filter left as `None` is ignored.

```python
scheduler.filter_tasks(pet_name="Luna")                   # all of Luna's tasks
scheduler.filter_tasks(completed=False)                   # unfinished tasks for every pet
scheduler.filter_tasks(pet_name="Luna", completed=False)  # Luna's unfinished tasks
```

The result can be passed to `sort_by_time()`. Pet names must match exactly, including case.

### Conflict detection: `Scheduler.detect_conflicts()`

A lightweight check that returns a list of warning messages instead of raising an error, so one double-booked task never stops the app:

1. Takes unfinished tasks due today that have a preferred time.
2. Converts each time to minutes since midnight. A time that isn't valid `"HH:MM"` (like `"7:30"` or `"25:00"`) gets an "Invalid time" warning and is skipped.
3. Sorts by start time. Two tasks conflict when the later one starts before the earlier one ends (start + duration). Because the list is sorted, the check stops early for each task, so it stays fast.

Each warning says whether the overlap is for the same pet or different pets:

```
Conflict (different pets): Mochi's Medication at 08:00 overlaps Luna's Breakfast at 08:00
```

Back-to-back tasks (07:30 for 30 minutes, then 08:00) are not conflicts. The check uses the times the owner asked for; `generate_schedule()` still builds a plan by moving the later task back.

### Recurring tasks: `Scheduler.mark_task_complete(pet, task)` and `Task.next_occurrence()`

Each task has a `due_date` (today by default). Completing a task through `mark_task_complete()` marks it done and adds a new copy to the pet for its next occurrence:

| Frequency | Next due date |
|-----------|---------------|
| `daily` | due date + `timedelta(days=1)` |
| `weekly` | due date + `timedelta(days=7)` |
| `once` | no new copy |

`timedelta` handles month ends and leap years correctly. If the task was overdue, the next date counts from today, so finishing a late task never creates a copy that's already due.

`generate_schedule()` only includes tasks due today or earlier, so tomorrow's copy of a daily task doesn't appear in today's plan, and weekly tasks don't show up every day.

Use `mark_task_complete()` rather than `task.mark_complete()`; only the scheduler method creates the next occurrence.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
