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

A configurable default "system organisation" (configurable via `KUKKUU_DEFAULT_ORGANISATION_NAME` in Django settings) is automatically created.
- Users mapped to this system organisation act as "system administrators".
- They bypass standard organization restrictions and have global access to manage events from *any* organisation.
- They can also view attendee and enrolment information for all events.

## Models
- `Organisation`: A very simple model representing an organisation (e.g. name). It is linked to multiple `User` instances (via `users.User.organisations`) and to multiple `Event` instances (via `events.Event.organisation`).

## Permissions

Users with no assigned organisations are implicitly restricted and cannot administer any events. Normal event organisers can only administer their own organisation's events.
