# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**doomdive** — repository is in early initialization. No source code, build system, or tooling has been added yet.

Update this file as the project takes shape with build commands, architecture notes, and development workflow.

## Git Workflow

Commit and push changes to GitHub regularly. After completing any meaningful unit of work, stage the relevant files, commit with a descriptive message, and push to `origin/master`.

Before every commit and push, run the test suite and ensure all tests pass:

```bash
pytest tests/ -v
```

Do not commit or push if any tests are failing.
