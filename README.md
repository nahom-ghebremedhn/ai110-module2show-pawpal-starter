# 🐾 PawPal+

PawPal+ is a pet care planner built with Python and Streamlit. A busy pet owner enters their pets, the care tasks each pet needs, and how much time they have today. PawPal+ then builds a daily schedule: it picks the most important tasks that fit, orders them by time, warns about double-booked times, and explains every decision.

## ✨ Features

- **Priority planning:** fits high → low priority tasks into your available minutes; skipped tasks get a reason.
- **Sorting by time:** orders tasks by preferred `HH:MM` across all pets, with "anytime" tasks last.
- **Smart time slots:** each task starts at its preferred time or right after the previous one, from 08:00 to midnight.
- **Filtering:** view tasks by pet, completion status, or both.
- **Conflict warnings:** flags overlapping times with the overlap length and a suggested new time; invalid times are caught, not crashed on.
- **Daily/weekly recurrence:** completing a recurring task adds its next occurrence; only tasks due today are planned.
- **Plan explanations:** a plain-text reason for every task scheduled or skipped.

## 🚀 Getting started

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

Run the command-line demo:

```bash
python main.py
```

## 📸 Demo Walkthrough

### What you can do in the app

| Section | Actions |
|---------|---------|
| **Owner** | Enter your name and how many minutes you have for pet care today. |
| **Pets** | Add pets by name and species (dog, cat, other). Each pet shows its task count. |
| **Tasks** | Add a task for a chosen pet with a duration, priority, optional preferred time (`HH:MM`), and how often it repeats (daily, weekly, once). |
| **Today at a glance** | See how many tasks are due, the minutes they need compared with the time you have, and how many time conflicts there are. |
| **Needs your attention** | Read conflict warnings, each with a suggested fix, and errors for invalid times. A green message confirms when there are no conflicts. |
| **All tasks** | Browse every task in time order, filtered by pet and by status (all, pending, completed). Mark a task complete; recurring tasks get their next occurrence automatically. |
| **Today's schedule** | Generate the plan: a summary of minutes used, a progress bar, a timetable with start and end times, notes on tasks that were pushed back, skipped tasks with reasons, and a "Why this plan?" explanation. |

### Example workflow

1. **Set up the owner.** Enter "Jordan" and set the available time to **60** minutes.
2. **Add two pets.** Add **Mochi** (dog) and **Luna** (cat). Both appear in the pet list with "0 task(s)".
3. **Add tasks.**
   - Mochi: **Morning walk**, 30 min, high priority, at **08:00**, daily.
   - Luna: **Breakfast**, 10 min, high priority, at **08:15**, daily.
   - Luna: **Brush fur**, 20 min, low priority, no time, weekly.
4. **Check today at a glance.** The metrics show 3 tasks due, 60 minutes needed, and 1 time conflict.
5. **Read the conflict warning.** The walk (08:00–08:30) and breakfast (08:15–08:25) overlap:
   > **Morning walk** (08:00–08:30) and **Breakfast** (08:15–08:25) overlap by 10 min. They're for **Mochi** and **Luna**, and you can't care for both at once.
   > 💡 Move **Breakfast** to **08:30** or later, or shorten one of the tasks.
6. **Browse the task list.** Tasks appear in time order (08:00, 08:15, then "Anytime"). Set the pet filter to Luna to see only her two tasks.
7. **Generate the schedule.** PawPal+ reports "Scheduled 3 task(s) using 60 of 60 available minutes" and shows:

   | Start | End | Pet | Task | Priority | Note |
   |-------|-----|-----|------|----------|------|
   | 08:00 | 08:30 | Mochi | Morning walk | 🔴 High | |
   | 08:30 | 08:40 | Luna | Breakfast | 🔴 High | Pushed back from preferred 08:15 |
   | 08:40 | 09:00 | Luna | Brush fur | 🟢 Low | |

8. **Complete a task.** Mark Luna's "Brush fur" complete. Because it's weekly, PawPal+ confirms the next one is due in 7 days, and it won't appear in today's plan.

### Scheduler behaviors shown

- **Sorting:** tasks are listed and scheduled by preferred time, with untimed tasks last.
- **Conflict warnings:** overlapping times are flagged before you plan, with the overlap length and a suggested fix.
- **Conflict resolution:** the schedule still builds; the later task is pushed back and the timetable notes it.
- **Priority within a time budget:** with less time available, low-priority tasks are skipped first, and each skipped task is listed with its reason.
- **Recurrence:** completing a daily or weekly task creates its next occurrence on the right date.
- **Day boundaries:** the plan starts at 08:00, so a task preferred for 07:30 is placed at 08:00.

### Sample CLI output

`python main.py` builds an owner with two pets and six tasks (added out of order), then shows sorting, filtering, recurrence, conflict detection, and the final plan:

```
Tasks as added:
  18:00  Mochi  Evening walk (todo, due 2026-10-27)
  07:30  Mochi  Morning walk (todo, due 2026-10-27)
  08:00  Mochi  Medication (todo, due 2026-10-27)
  --:--  Luna   Brush fur (todo, due 2026-10-27)
  12:30  Luna   Clean litter box (todo, due 2026-10-27)
  08:00  Luna   Breakfast (todo, due 2026-10-27)

Sorted by time:
  07:30  Mochi  Morning walk (todo, due 2026-10-27)
  08:00  Mochi  Medication (todo, due 2026-10-27)
  08:00  Luna   Breakfast (todo, due 2026-10-27)
  12:30  Luna   Clean litter box (todo, due 2026-10-27)
  18:00  Mochi  Evening walk (todo, due 2026-10-27)
  --:--  Luna   Brush fur (todo, due 2026-10-27)

Luna's tasks:
  --:--  Luna   Brush fur (done, due 2026-10-27)
  12:30  Luna   Clean litter box (todo, due 2026-10-27)
  08:00  Luna   Breakfast (todo, due 2026-10-27)
  --:--  Luna   Brush fur (todo, due 2026-11-03)

Completed tasks:
  --:--  Luna   Brush fur (done, due 2026-10-27)

Warnings:
  Conflict (different pets): Mochi's Medication at 08:00 overlaps Luna's Breakfast at 08:00

Today's Schedule for Jordan
========================================
08:00  Mochi  Morning walk (30 min, high)
08:30  Mochi  Medication (5 min, high)
08:35  Luna   Breakfast (10 min, high)
12:30  Luna   Clean litter box (15 min, medium)
18:00  Mochi  Evening walk (30 min, medium)
```

Things to notice: the "Sorted by time" list puts "Brush fur" (no time) last; completing the weekly "Brush fur" created a new copy due 7 days later, which is why it isn't in today's schedule; Medication and Breakfast are both at 08:00, so they're flagged and then scheduled one after the other; and the 07:30 walk starts at 08:00, when the day begins.

## 🛠️ Implementation Summary

- **`Task`:** one care activity with a preferred time, duration, priority, frequency, due date, and completed flag.
- **`Pet`:** a pet's name, species, and list of tasks.
- **`Owner`:** the owner's pets and available minutes; `get_all_tasks()` returns every `(pet, task)` pair.
- **`Scheduler`:** picks tasks by priority within the time budget, lays them out by time, and explains each decision.
- **`Conflict`:** two overlapping tasks, with the overlap length and a suggested new start time.

Full class diagram: [`diagrams/uml_final.mmd`](diagrams/uml_final.mmd).

## 📐 Smarter Scheduling

Four features build on the basic scheduler. All of them are in `pawpal_system.py`, demonstrated in `main.py` and covered by tests in `tests/test_pawpal.py`.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | By preferred `"HH:MM"` time; tasks with no time go last |
| Filtering | `Scheduler.filter_tasks()` | By pet name, completion status or both |
| Conflict handling | `Scheduler.find_conflicts()`, `detect_conflicts()` | Warns about overlapping times instead of crashing |
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

### Conflict detection: `Scheduler.find_conflicts()` and `detect_conflicts()`

A lightweight check that reports problems instead of raising an error, so one double-booked task never stops the app:

1. Takes unfinished tasks due today that have a preferred time.
2. Converts each time to minutes since midnight. A time that isn't valid `"HH:MM"` (like `"7:30"` or `"25:00"`) is reported as invalid and skipped.
3. Sorts by start time. Two tasks conflict when the later one starts before the earlier one ends (start + duration). Because the list is sorted, the check stops early for each task, so it stays fast.

`find_conflicts()` returns structured `Conflict` objects (used by the Streamlit UI to show overlap length and a suggested time). `detect_conflicts()` turns them into plain-text warnings, each saying whether the overlap is for the same pet or different pets:

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
