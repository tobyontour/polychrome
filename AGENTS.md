# AGENTS.md

## Purpose

A terminal based BBS with a REST API backend.

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

## Architecture
- Follow the repository pattern

