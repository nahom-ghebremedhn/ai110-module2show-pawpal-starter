import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

PRIORITY_LABELS = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}


def minutes_to_hhmm(minutes: int) -> str:
    """Format minutes since midnight as "HH:MM"."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def time_window(task: Task) -> str:
    """Return a task's preferred window as "HH:MM–HH:MM"."""
    hours, mins = map(int, task.time.split(":"))
    start = hours * 60 + mins
    return f"{task.time}–{minutes_to_hhmm(start + task.duration_minutes)}"


st.title("🐾 PawPal+")
st.caption("Plan your pets' care around your day: by priority, time, and the minutes you have.")

# --- Owner ---------------------------------------------------------------

st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    available_time = st.number_input(
        "Time available today (minutes)", min_value=0, max_value=1440, value=60
    )

# Create the Owner once; reruns reuse the same object from the session "vault".
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)
owner = st.session_state.owner
owner.name = owner_name
owner.set_available_time(int(available_time))
scheduler = Scheduler(owner)

# --- Pets ----------------------------------------------------------------

st.subheader("Pets")
with st.form("add_pet", clear_on_submit=True, border=False):
    col1, col2, col3 = st.columns([3, 2, 1], vertical_alignment="bottom")
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        if st.form_submit_button("Add pet", width="stretch"):
            owner.add_pet(Pet(name=pet_name, species=species))
            st.toast(f"Added {pet_name} 🐾")

if owner.pets:
    st.markdown("  \n".join(f"- {pet.get_pet_info()}" for pet in owner.pets))
else:
    st.info("No pets yet. Add one above to get started.")

# --- Add a task ----------------------------------------------------------

st.subheader("Tasks")
if owner.pets:
    with st.form("add_task", clear_on_submit=True):
        pet_index = st.selectbox(
            "Pet", range(len(owner.pets)), format_func=lambda i: owner.pets[i].name
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task", value="Morning walk")
        with col2:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col3:
            priority = st.selectbox(
                "Priority", ["high", "medium", "low"], format_func=PRIORITY_LABELS.get
            )
        col1, col2 = st.columns(2)
        with col1:
            task_time = st.text_input("Preferred time (HH:MM)", placeholder="optional, e.g. 08:00")
        with col2:
            frequency = st.selectbox("Repeats", ["daily", "weekly", "once"])

        if st.form_submit_button("Add task", type="primary"):
            pet = owner.pets[pet_index]
            pet.add_task(
                Task(
                    description=task_title,
                    time=task_time.strip() or None,
                    frequency=frequency,
                    duration_minutes=int(duration),
                    priority=priority,
                )
            )
            st.toast(f"Added “{task_title}” for {pet.name}")
else:
    st.caption("Add a pet before adding tasks.")

# --- Today at a glance ---------------------------------------------------

conflicts, invalid_times = scheduler.find_conflicts()
due_today = scheduler.prioritize_tasks()

if owner.get_all_tasks():
    st.subheader("Today at a glance")
    minutes_due = sum(task.duration_minutes for _, task in due_today)
    col1, col2, col3 = st.columns(3)
    col1.metric("Tasks due today", len(due_today))
    col2.metric(
        "Minutes needed",
        minutes_due,
        delta=f"{owner.available_time - minutes_due} min to spare"
        if minutes_due <= owner.available_time
        else f"{minutes_due - owner.available_time} min over",
        delta_color="normal" if minutes_due <= owner.available_time else "inverse",
    )
    col3.metric("Time conflicts", len(conflicts) + len(invalid_times))

    # --- Conflicts: clear, specific, and actionable ----------------------
    if conflicts or invalid_times:
        st.markdown("#### ⚠️ Needs your attention")
        for pet, task in invalid_times:
            st.error(
                f"**{pet.name}: {task.description}** has the time “{task.time}”, "
                "which isn't a valid time.  \n"
                "💡 Use 24-hour HH:MM, like 08:00 or 17:30. "
                "This task won't be scheduled until it's fixed.",
                icon="🕒",
            )
        for c in conflicts:
            who = (
                f"both for **{c.first_pet.name}**"
                if c.same_pet
                else f"for **{c.first_pet.name}** and **{c.second_pet.name}**, "
                "and you can't care for both at once"
            )
            suggestion = c.suggested_time()
            tip = (
                f"💡 Move **{c.second_task.description}** to **{suggestion}** or later, "
                "or shorten one of the tasks."
                if suggestion
                else "💡 Shorten one of these tasks or move one to another day."
            )
            st.warning(
                f"**{c.first_task.description}** ({time_window(c.first_task)}) and "
                f"**{c.second_task.description}** ({time_window(c.second_task)}) "
                f"overlap by {c.overlap_minutes} min. They're {who}.  \n{tip}",
                icon="⏰",
            )
        st.caption(
            "You can still generate a schedule. PawPal+ will start overlapping "
            "tasks as soon as the earlier one ends."
        )
    elif any(task.time for _, task in due_today):
        st.success("No time conflicts. Every timed task has its own slot.", icon="✅")

    # --- Task list: filtered and sorted ----------------------------------
    st.markdown("#### All tasks")
    col1, col2 = st.columns(2)
    with col1:
        pet_filter = st.selectbox("Pet", ["All pets"] + [p.name for p in owner.pets])
    with col2:
        status_filter = st.segmented_control(
            "Status", ["All", "Pending", "Completed"], default="All"
        )

    filtered = scheduler.filter_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed={"All": None, "Pending": False, "Completed": True}.get(status_filter),
    )
    visible = scheduler.sort_by_time(filtered)
    if visible:
        st.dataframe(
            [
                {
                    "Time": task.time or "Anytime",
                    "Pet": pet.name,
                    "Task": task.description,
                    "Duration": task.duration_minutes,
                    "Priority": PRIORITY_LABELS[task.priority],
                    "Repeats": task.frequency.capitalize(),
                    "Due": task.due_date,
                    "Status": "✅ Done" if task.completed else "⏳ Pending",
                }
                for pet, task in visible
            ],
            hide_index=True,
            width="stretch",
            column_config={
                "Duration": st.column_config.NumberColumn(format="%d min"),
                "Due": st.column_config.DateColumn(format="ddd, MMM D"),
            },
        )
        st.caption(
            f"Showing {len(visible)} of {len(owner.get_all_tasks())} tasks, "
            "sorted by preferred time. Tasks without a time are listed last."
        )
    else:
        st.info("No tasks match these filters.")

    pending = scheduler.filter_tasks(completed=False)
    if pending:
        col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
        with col1:
            done_index = st.selectbox(
                "Mark a task complete",
                range(len(pending)),
                format_func=lambda i: f"{pending[i][0].name}: {pending[i][1].description}",
            )
        with col2:
            if st.button("Mark complete", width="stretch"):
                pet, task = pending[done_index]
                next_task = scheduler.mark_task_complete(pet, task)
                if next_task is not None:
                    st.session_state.flash = (
                        f"Done! Next {task.description} for {pet.name} is due "
                        f"{next_task.due_date.strftime('%a, %b %d')}."
                    )
                else:
                    st.session_state.flash = (
                        f"Done! {task.description} for {pet.name} is complete."
                    )
                st.rerun()
    if "flash" in st.session_state:
        st.success(st.session_state.pop("flash"), icon="🎉")
elif owner.pets:
    st.info("No tasks yet. Add one above.")

# --- Schedule ------------------------------------------------------------

st.divider()
st.subheader("Today's schedule")
st.caption("Picks the highest-priority tasks that fit your available time, then orders them by time.")

if st.button("Generate schedule", type="primary"):
    schedule = scheduler.generate_schedule()
    if schedule:
        used = sum(task.duration_minutes for _, _, task in schedule)
        st.success(
            f"Scheduled {len(schedule)} task(s) using {used} of "
            f"{owner.available_time} available minutes.",
            icon="📅",
        )
        st.progress(min(used / owner.available_time, 1.0) if owner.available_time else 1.0)

        rows = []
        for start, pet, task in schedule:
            start_minutes = start.hour * 60 + start.minute
            note = ""
            if task.time and task.time != start.strftime("%H:%M"):
                note = f"Pushed back from preferred {task.time}"
            rows.append(
                {
                    "Start": start.strftime("%H:%M"),
                    "End": minutes_to_hhmm(start_minutes + task.duration_minutes),
                    "Pet": pet.name,
                    "Task": task.description,
                    "Priority": PRIORITY_LABELS[task.priority],
                    "Note": note,
                }
            )
        st.dataframe(rows, hide_index=True, width="stretch")
    else:
        st.warning("Nothing fits in today's available time.", icon="⌛")

    if scheduler.skipped_tasks:
        st.markdown("**Not scheduled today**")
        for pet, task, reason in scheduler.skipped_tasks:
            st.warning(
                f"**{pet.name}: {task.description}** "
                f"({task.duration_minutes} min, {task.priority} priority): {reason}.",
                icon="⏭️",
            )

    with st.expander("Why this plan?"):
        st.text(scheduler.explain_schedule())
