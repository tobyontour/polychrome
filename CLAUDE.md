# CLAUDE.md

This file gives guidance to Claude (and other coding agents) when working in this repository.

## Project Overview

- Name: `polychrome`
- Stack: Python 3.11, FastAPI backend, Textual CLI frontend
- Package/dependency manager: `uv`
- Tests: `pytest`
- Linting: `ruff`

## Repository Layout

- `api/` - FastAPI application and tests
  - `api/app/` - app code (models, repositories, routes)
  - `api/tests/` - backend tests
- `cli/` - Textual client application
- `data/` - local data files (including menus)
- `docs/` - project documentation

## Setup and Local Development

Install dependencies:

```bash
make install-dev
```

Run backend API:

```bash
make run
```

Run Textual CLI:

```bash
make cli
```

## Quality Checks

Run linting:

```bash
make lint
```

Run auto-fix lint issues:

```bash
make fix
```

Run tests:

```bash
make test
```

Run coverage for API tests:

```bash
make coverage
```

## Coding Guidelines

- Prefer small, focused changes.
- Match existing style and patterns in nearby files.
- Add or update tests for behavior changes.
- Avoid unrelated refactors in feature/fix PRs.
- Keep file paths and module imports consistent with current structure.

## Testing Notes

- Use `tmp_path` for filesystem repository tests.
- Keep tests deterministic and isolated from external services.
- If updating repository behavior, validate both in-memory and filesystem-backed variants when applicable.

## Agent Behavior Notes

- Do not modify git configuration.
- Do not run destructive git commands.
- Do not commit or push unless explicitly requested.
- If existing working tree has unrelated changes, do not revert them.
