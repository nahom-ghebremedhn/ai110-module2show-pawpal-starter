# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

1. Users should be able to add their pet's information, such as its name and type.
2. Users should be able to create and manage pet care tasks, such as feeding, walking, and grooming.
3. Users should be able to generate and view a daily care schedule based on task priorities and the time available.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

I linked the classes so the design matches how the app will actually be used. Each Pet now holds its own care tasks, and Scheduler reads the time, preferences and pets straight from Owner, so there's only one copy of each value to keep in sync. I made priority a fixed set of levels (low, medium, high) and added checks that reject bad input like zero-minute tasks, so typos can't quietly mess up the order. The scheduler now also records which tasks it skipped and why, and gives each scheduled task a pet and a start time, so it can explain its choices and show a readable daily plan.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler uses a greedy approach, choosing the highest-priority tasks first, if two tasks have the same priority, it chooses the shorter one first. It adds tasks if they fit within the owner's available time. Sometimes, this leaves unused time because it doesn't try every possible combination.
This approach works well because important pet care, like feeding, medication and walks, should come first. It's simple to understand and effective for a small number of daily tasks.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

1. I used AI to brainstorm the class design and draft the UML diagram, then to turn the UML into class skeletons in pawpal_system.py. Later I used it to refactor the code, for example moving the skeletons out of the diagrams. I also had it help write the pytest tests and the main.py demo, and used it to debug errors when tests failed.

- What kinds of prompts or questions were most helpful?

1. "Given this UML, generate Python class skeletons with type hints."
2. "Why does this test fail?" with the error pasted in.
3. "Suggest edge cases to test for the scheduler."

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

1. When I asked the AI to turn my UML into class skeletons, it added extra methods and attributes my design didn't need, and it put scheduling logic inside the Pet class. I removed what I didn't need and moved the scheduling into the Scheduler class so each class kept one clear job. Then I updated the UML to match. 

- How did you evaluate or verify what the AI suggested?

I checked the changes that AI made and if I thoughts AI's suggestion was not the best way, I ask AI "What if I do this instead of this?" Also test it before proceeding to the next step.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested sorting by time, daily/weekly recurrence, conflict detection (same pet and across pets), priority within the time budget, and edge cases like invalid times and plans running past midnight.
These matter because they're the scheduler's core decisions, so a bug there would silently give an owner a wrong or missing care plan.

**b. Confidence**

- How confident are you that your scheduler works correctly? 
- What edge cases would you test next if you had more time?

Fairly confident (4/5): all 31 tests pass and I checked the CLI and Streamlit output by hand.
Next I'd test the new `Conflict.suggested_time()` directly, three-way overlaps where one suggestion still clashes, tasks preferred before 08:00, and the Streamlit UI itself.

---

## 5. Reflection

**a. What went well**

The assistant read the actual code and ran things (pytest, main.py, a headless Streamlit test) so suggestions were checked against real output, not guessed. Inline file edits, and git-aware context made small incremental changes easy to review.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would make some classes and methods less dependent on one another because if I plan to extend the progeam later it would be much easier to add classes and methods than modify existing ones. 

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

I leared that AI can be the perfect collaborator in a project because you can interact with it the way you want and learn a lot from its suggestion though you should not be dependent on it. 

