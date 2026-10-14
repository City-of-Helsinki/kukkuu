<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Organisations](#organisations)
  - [Purpose](#purpose)
  - [Default System Organisation](#default-system-organisation)
  - [Models](#models)
  - [Permissions](#permissions)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Organisations

The `organisations` app manages the organizational scoping of events in Kukkuu.

## Purpose

By default, an event organiser's access and capabilities are restricted to events that belong to their designated organisation. This prevents cross-organisation administrative access and restricts access to sensitive relational data (like enrolment or attendee lists).

## Default System Organisation

A configurable default "system organisation" (configurable via `KUKKUU_DEFAULT_ORGANISATION_NAME` in Django settings) is automatically created (designated by `is_system=True`).
- It designates the default municipal organisation representing the City of Helsinki.
- Membership in the system organisation does **not** grant system administrator rights. System administrator privileges are granted exclusively via `is_staff` or `is_superuser` on the user account.
- For a comprehensive breakdown of roles and permissions, see [Admin UI Privileges & Permissions](../docs/admin-ui-privileges.md).

## Models
- `Organisation`: A very simple model representing an organisation (e.g. name). It is linked to multiple `User` instances (via `users.User.organisations`) and to multiple `Event` instances (via `events.Event.organisation`).

## Permissions

Users with no assigned organisations are implicitly restricted and cannot log into the Admin UI or administer any events (unless they are system administrators). Normal event organisers can only administer their own organisation's events within their administered projects. See [Admin UI Privileges & Permissions](../docs/admin-ui-privileges.md) for full details.
