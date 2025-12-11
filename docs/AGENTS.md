# Docs Agent Notes (Sphinx)

## Scope

This file applies to **`docs/` only**.

## High-level map

- Sphinx config and sources: `sources/`
- Output build directory: `_build/` (generated)
- How-to content: `how-to/`

## Default workflow (follow this)

1. **Explore**: identify where the page lives in `sources/` and how it’s referenced in toctrees.
2. **Plan**: change the smallest number of pages; keep navigation consistent.
3. **Implement**:
   - Keep documentation **in English** (project rule).
   - Prefer short sections, clear headings, and actionable steps.
4. **Verify**: build docs locally and fix warnings.

## Commands

- **Build HTML docs**: `make build-docs`
  - Runs: `uv run sphinx-build -b html -c sources sources _build`

## Writing & structure guidelines

- Prefer **task-oriented** docs:
  - What you’re trying to do
  - Preconditions
  - Steps
  - Expected result
  - Troubleshooting
- When referencing code paths, use backticks.
- Keep examples copy/paste friendly.

## Repo hygiene

- Do not commit generated output in `_build/`.
- Avoid adding secrets or environment-specific values to docs.
