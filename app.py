import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")
available_time = st.number_input(
    "Time available today (minutes)", min_value=0, max_value=1440, value=60
)

# Create the Owner once; reruns reuse the same object from the session "vault".
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)
owner = st.session_state.owner
owner.name = owner_name
owner.set_available_time(int(available_time))

st.markdown("### Pets")
col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    owner.add_pet(Pet(name=pet_name, species=species))

if owner.pets:
    for pet in owner.pets:
        st.write(f"- {pet.get_pet_info()}")
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Tasks are attached to a pet and feed into the scheduler.")

if owner.pets:
    pet_index = st.selectbox(
        "Pet", range(len(owner.pets)), format_func=lambda i: owner.pets[i].name
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        owner.pets[pet_index].add_task(
            Task(description=task_title, duration_minutes=int(duration), priority=priority)
        )
else:
    st.caption("Add a pet before adding tasks.")

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "pet": pet.name,
                "task": task.description,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
            }
            for pet, task in all_tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Plans the highest-priority tasks that fit in today's available time.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    schedule = scheduler.generate_schedule()
    if schedule:
        st.table(
            [
                {
                    "start": start.strftime("%H:%M"),
                    "pet": pet.name,
                    "task": task.description,
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority,
                }
                for start, pet, task in schedule
            ]
        )
    else:
        st.warning("Nothing fits in today's available time.")
    st.markdown("**Why:**")
    st.text(scheduler.explain_schedule())
