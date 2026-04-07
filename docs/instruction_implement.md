# Implementation Instructions

1. **Execute tasks in order.** Implement the tasks in the `design/` folder sequentially by their numeric prefix (e.g., `task_0_1` before `task_1_1`, `task_1_1` before `task_1_2`, etc.).

2. **Delegate each task to a sub-agent.** Each task must be implemented by a dedicated sub-agent to keep the major agent's context clean and focused.

3. **Review before building.** For every task, the sub-agent must first review the design document and critically evaluate it. If the sub-agent identifies a better approach, it should implement that approach instead and update the design document to reflect what was actually built.

4. **Handle failures explicitly.** If a task cannot be implemented (no viable solution exists), the sub-agent must:
   - Append a clear description of the failure cause to the task's design document.
   - Report the failure back to the major agent so that a human can review and resolve the issue.

5. **Block on failures.** If any task fails, the major agent must **not** proceed to the next task. Execution pauses until the failed task is resolved.

6. **Create a git commit for each task.** If task suceeded, create a git commit for the implementation and doc updates. Keep the commit clean, e.g. only include the necessary files and exclude intermediate files.