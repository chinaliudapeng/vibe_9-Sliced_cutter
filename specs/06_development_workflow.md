# Process Module: Development Workflow & Git Integration

## 1. AI Assistant Core Behavior
As an AI coding assistant (e.g., Claude Code), you are required to act as an autonomous developer. This means you must manage version control proactively. You have full permission to execute shell commands for Git operations.

## 2. Milestone-Driven Git Commits
You MUST automatically stage and commit changes to the Git repository whenever a "small milestone" is reached. Do NOT wait for the user to explicitly tell you to commit. 

**Definition of a "Small Milestone":**
- Initial project scaffolding and environment setup is complete.
- A single specification file (e.g., `02_core_image_logic.md`) is fully implemented and tested.
- A distinct UI component (e.g., the responsive canvas or the right-side control panel) is built and renders correctly.
- The two-way binding logic (Signal/Slot integration) between UI and data is successfully connected.
- A critical bug is identified and fixed.
- Refactoring of a specific module is completed without breaking existing tests.

## 3. Git Commit Standards
- **Command:** Use `git add .` followed by `git commit -m "<message>"`.
- **Commit Message Format:** Follow the Conventional Commits specification.
  - `feat:` for new features (e.g., `feat: implement Pillow center-cross removal logic`).
  - `fix:` for bug fixes (e.g., `fix: correct QSpinBox clamping limit`).
  - `refactor:` for code structural changes.
  - `chore:` for setup, dependencies, or configuration updates.
  - `test:` for adding or updating unit tests.
- **Granularity:** Keep commits atomic. If you implement the Image logic and the UI layout in one go, split them into two separate commits if possible.

## 4. Test-Driven & Iterative Approach
- Before moving to a new specification, verify that the current milestone works. 
- If a script or test fails, fix it and commit the fix (`fix: ...`) before proceeding to the next major feature.