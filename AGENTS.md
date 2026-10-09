<!-- DOCTOC SKIP -->

# Kukkuu Backend Agent Instructions

## Role
You are working on `kukkuu`, the Django/GraphQL backend that acts as the primary API provider and the sole owner of the system database.

## Ecosystem
- **`kukkuu-ui`**: The public UI for guardians.
- **`kukkuu-admin`**: The staff UI for organizers, admins, and the product owner.
- **External Dependencies**: `react-helsinki-headless-cms` (used by the public UI), Headless CMS (WordPress), Notification Service API (SMS), and Mailer.
For the full architectural picture, see [ARCHITECTURE.md](./ARCHITECTURE.md) and the [Service architecture](README.md#service-architecture) in the README.

## Commands
- **Install dependencies:** `uv sync --locked`. To add/update, edit `pyproject.toml` then run `uv lock`.
- **Run server:** `python manage.py runserver localhost:8081` (after running `python manage.py migrate`).
- **Containers:** This repo ships a `compose.yaml`. Use any Compose-compatible container engine (e.g., Docker Compose or Podman Compose). The README uses `docker compose up` as an example.
- **Test:** Run `pytest`. Note: Tests require a PostgreSQL user with `CREATEDB` privileges (see the Database section in the README).
- **Lint & Format:** `pre-commit run -a ruff`, `pre-commit run -a ruff-format`.

## Architecture Map
Key top-level Django apps and their purposes:
- `children`: Manage children and their guardians.
- `events`: Manage events, occurrences, and enrolments.
- `venues`: Manage event venues.
- `projects`: Manage year projects (grouping children and events by birth year).
- `users`: User extensions and custom models.
- `messaging`: Handle messages and notifications to users.
- `subscriptions`: Manage user subscriptions to notifications.
- `reports`: REST endpoints for data reporting.
- `gdpr`: GDPR compliance and data export/deletion API.
- `verification_tokens`: Handling email/SMS verification tokens.
- `common`: Shared utilities and base models.
- `importers`: Import scripts for events and venues.

## Domain Logic
- **Projects & Privileges**: A project groups children and events. In the Admin UI, the project selector in the top right corner lists projects based on user privileges. If a user lacks privileges, the project is not listed. Privileges can be partial (e.g., an organizer can create events but not publish them).
- **Events & Event Groups**: Event organizers create events and event groups. One event group contains multiple events. Both an event group and an event always belong to a single project.
- **Enrollment Limits**:
  - A project configures how many times a child can enrol per year (usually twice).
  - A child can participate in only **one** event within a single event group. For example, if only one event group is published for a spring season, a child can only participate once during that spring.
- **Visibility Rules (Events vs Enrolments)**:
  - Published events and occurrences remain globally visible so the public UI and other event organizers can view them.
  - Unpublished events and occurrences are strictly isolated. Only system administrators and users who are members of the event's designated organisation can view or administer them.
  - Enrolment and attendee data are **never** globally visible, regardless of the event's publish state. Only system administrators and members of the event's organisation can access them.

## Rules and Guardrails
- **Commits:** Must follow Conventional Commits, with a max of 72 characters per line in the body.
- **Secrets:** Never read, print, or commit `.env` files or secrets.
- **Release Management:** Do not hand-edit `CHANGELOG.md`, `.release-please-manifest.json`, or the `version` in `pyproject.toml`. These are owned by `release-please`.
- **Migrations:** Do not edit existing database migrations. Always add new ones.
- **Snapshot Tests:** Snapshot tests (`syrupy`) should be updated deliberately, never blindly.
- **Supply Chain:** `uv.lock` uses `exclude-newer = "P3D"`. Do not remove it.
- **Code Style:** No `print` statements (Ruff rule `T20`).
- **Audit Logging:** Audit-logged models are configured in `kukkuu/auditlog_settings.py`.
- **Destructive Operations:** Ask for confirmation before dropping/resetting the database, deleting volumes (e.g. `compose down -v`), or force-pushing.

## Cross-Repo Impact
Any changes to the GraphQL schema or authentication flow will affect `kukkuu-ui` and `kukkuu-admin`. Always name the consumer repos in the PR description if they are impacted.

*If a command or rule here no longer matches the repo, fix this file in the same change.*
