---
name: algorithm-review
description: Guidelines for reviewing, debugging, and improving Python algorithmic and solver code. Apply to timetable solvers, constraint satisfaction problems, optimization scripts, and any complex logic-heavy Python files.
---

# Python Algorithm Review — Guidelines

## When to Use This Skill
- Reviewing or debugging any Python solver, scheduler, or constraint-based algorithm
- Profiling slow scripts or optimizing time complexity
- Adding new constraints or variables to an existing solver
- Generating visual output (terminal tables, HTML) from solver results

## Review Checklist

### 1. Correctness First
- [ ] Does the algorithm produce valid output for all known test cases?
- [ ] Are edge cases handled: empty input, single item, all constraints violated?
- [ ] Are there any silent failures (bare `except:` clauses, missing returns)?
- [ ] Do all loops have clear termination conditions?

### 2. Constraint Satisfaction Problems (CSP)
- Identify: **Variables**, **Domains**, and **Constraints** before touching any code.
- Validate that constraints are checked in the right order (hard constraints before soft).
- Watch for **constraint propagation** issues — a change to one variable must propagate its impact to all affected variables.
- If using backtracking, confirm that the **restore state** on backtrack is complete (no partial assignments left behind).

### 3. Time Complexity
- Identify loops and flag any O(n²) or worse patterns nested inside each other.
- Prefer dict lookups over list `.index()` calls inside hot loops.
- If generating permutations/combinations, confirm the search space is bounded.

### 4. Data Structures
- Use `defaultdict` or `Counter` from `collections` for frequency/grouping work.
- Use `heapq` for priority queues instead of sorting on every iteration.
- Use sets for membership tests instead of lists when order doesn't matter.

### 5. Output Validation
- For a timetable/schedule solver: verify no two items share the same time slot + room.
- For an optimizer: confirm the objective function value is actually decreasing (or increasing) each iteration.
- Print/log intermediate states during debugging, not just final output.

## Timetable Solver — Specific Rules (timetsolver project)
- **Fixed subjects** = subjects with pre-assigned slots that cannot be moved.
- **Variable subjects** = subjects the solver is free to place, subject to constraints.
- Never place a lab subject (2-hour block) in the last slot of the day.
- No teacher should appear in two rooms at the same time slot.
- Lunch slots must remain empty.
- When adding a new constraint, update **both** the forward-checking logic and the final validation step.

## Debugging Approach
```
1. Reproduce the issue with the smallest possible input.
2. Add print statements at each major decision point (selecting a variable, assigning a value, backtracking).
3. Check if the issue is a logic bug (wrong constraint) or a state bug (stale data).
4. Fix one thing at a time and re-run the full test suite after each change.
```

## Visual Output Rules
- **Terminal output**: use `tabulate` or manually format columns with `str.ljust(n)` for alignment.
- **HTML output**: generate a proper `<table>` with `colspan` for multi-hour lab blocks. Auto-open with `webbrowser.open()`.
- **Color coding**: use a subject-to-color mapping dict. Assign colors consistently across both terminal and HTML output.
- Always write HTML output to a temp file (`/tmp/timetable.html`) and open it with the default browser.

## Code Quality Rules
- Every function must have a docstring describing its purpose, parameters, and return value.
- Avoid global mutable state — pass the schedule/state object explicitly as a parameter.
- Use type hints on function signatures for any solver that will be edited frequently.
- Name solver variables descriptively: `unassigned_subjects` not `remaining`, `slot_assignments` not `result`.
