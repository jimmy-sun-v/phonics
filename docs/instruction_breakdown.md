### Objective

Based on the project overview, generate a **granular, ordered, and testable task breakdown** suitable for incremental development of a responsive web application.

---

### 1. Source of Truth

- Use the **[App_Overview.md](requirements/App_Overview.md) document as the authoritative reference**.
- Extract **functional and non‑functional requirements** from it.
- Translate these requirements into **concrete technical specifications** and **implementable tasks**.

---

### 2. Task Granularity & Structure

- Decompose the system into **small, well‑scoped tasks**.
- Each task must:
  - Have a **single clear responsibility**
  - Be **implementable independently**
  - Avoid tight coupling with multiple other tasks
- Prefer **vertical slices** (end‑to‑end, minimal scope) where possible.

---

### 3. Testability (Mandatory)

- **Every task must be testable**.
- Each task must define at least one of the following:
  - Unit test criteria
  - Integration test criteria
  - Manual verification steps (only if automated tests are not feasible)
- Tasks without a clear test strategy should be **refactored into smaller tasks**.

---

### 4. Progressive Ordering & Dependencies

- Tasks must be **ordered logically** based on dependencies.
- Follow this progression:
  1.  Foundations and configuration
  2.  Data models and core services
  3.  APIs and business logic
  4.  UI components and frontend integrations
  5.  AI/advanced features
- **Lower‑level dependencies must be completed and testable before higher‑level tasks** that consume them.

✅ Example:

> Database models → Service layer → API endpoints → UI components

---

### 5. Folder & Project Structure

- Define a **clear and meaningful folder structure** early.
- Folder structure must:
  - Reflect domain boundaries (e.g. phonics, speech, AI, UI)
  - Align with Django best practices
  - Support scalability and maintainability
- Tasks that introduce new components must specify:
  - Target folder
  - Naming conventions
  - Ownership (app/module)

---

### 6. Responsiveness & Device Support

- The web application must be **responsive by design**, supporting:
  - Desktop
  - Tablet
  - Mobile
- Tasks that touch UI must explicitly state:
  - Responsive requirements
  - Target breakpoints
  - Input method assumptions (touch vs mouse)

---

### 7. Independence & Decoupling

- Tasks should be **as independent as possible**.
- A task should depend on:
  - **At most one or two prerequisite tasks**
- Avoid tasks that:
  - Require large portions of the system to be completed
  - Span multiple unrelated domains
- If a task becomes too broad, **split it**.

---

### 8. Task Definition Template (Recommended)

Each task should be defined using a consistent structure:

```text
Task Title
Description
Dependencies
Inputs / Outputs
Acceptance Criteria
Test Strategy
Target Folder(s)
```

---

### 9. Quality Bar

- Prefer **more small tasks** over fewer large ones.
- Tasks must be:
  - Understandable without external context
  - Runnable in isolation once dependencies are met
  - Clearly verifiable as “done”

---

### Summary Statement (Optional for AI Prompting)

> Generate a dependency‑ordered list of small, independent, testable tasks derived from [App_Overview.md](requirements/App_Overview.md), ensuring responsive web design, clear folder structure, and progressive build‑up from foundational components to user‑facing features.
