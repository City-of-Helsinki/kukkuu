<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Events](#events)
  - [Domain Logic & Visibility Rules](#domain-logic--visibility-rules)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Events

The `events` app manages events, their occurrences, and user enrolments within Kukkuu.

## Domain Logic & Visibility Rules

Events and enrolments have strict visibility rules based on the user's role and the event's organisation.

* **Published Events:**
  Published events (and their occurrences) remain globally visible. This is necessary so the public UI and other event organizers can view them.

* **Unpublished Events:**
  Unpublished events and occurrences are strictly isolated. Only system administrators and users who are members of the event's designated organisation can view or administer them.

* **Enrolments & Attendee Data:**
  Enrolment and attendee data are **never** globally visible, regardless of the event's publish state. Only system administrators and members of the event's organisation can access this sensitive information.
