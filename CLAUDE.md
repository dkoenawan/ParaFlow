## AGENTIC INSTRUCTIONS

### Planning Mode
1. Take the latest open issue from GitHub `gh issue list`
2. Read the requirements
3. Read the documentations following this priority README.md, docs folder, codebase
4. Construct a plan to execute the requirements. Within the plan it should contains
4.1 Approach (what changes you are going to make, how it will work)
4.2 Rationale (why it will work)
4.3 Potential Impact on existing adjacent feature
Note: Always follow a hexagonal code architecture (Ports & Adapters) and SOLID principle.
5. Respond directly to the issue in GitHub. Wait for further response from the GitHub

### Execution Mode
1. Create a new branch from develop, follow trunk-based branching methods
2. Execute the command from the plan, step by step.
3. (If Applicable) Run Unit Tests using: `source venv/bin/activate && python -m pytest [test_path] -v`
4. Report your outcome back to the Github issue 
5. Commit, push and create PR to develop
6. Wait for further comments or response from GitHub issue.

### Testing Commands
- **Run specific test file**: `source venv/bin/activate && python -m pytest packages/domain/tests/test_[module].py -v`
- **Run all domain tests**: `source venv/bin/activate && python -m pytest packages/domain/tests/ -v`
- **Run with coverage**: `source venv/bin/activate && python -m pytest packages/domain/tests/ --cov=packages --cov-report=term-missing -v`
- **IMPORTANT**: Always activate the virtual environment first with `source venv/bin/activate` before running pytest
- **AVOID**: Using `python` or `python3` directly without virtual environment activation

### Clean Up Mode
1. Update all documentation (README.md)
2. Expand the documentation in the docs folder
3. Commit, push, and create PR to develop

## PROJECT OVERVIEW
