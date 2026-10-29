<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Enrolment and Capacity Decisions (Hekla Release)](#enrolment-and-capacity-decisions-hekla-release)
  - [1. Background & Context](#1-background--context)
  - [2. Core Decisions & Rules](#2-core-decisions--rules)
    - [Rule 1: Legacy-Safe Seat Accounting](#rule-1-legacy-safe-seat-accounting)
    - [Rule 2: Real Physical Headcount for New Enrolments](#rule-2-real-physical-headcount-for-new-enrolments)
    - [Rule 3: Event Types & Removal of `CHILD_AND_1_OR_2_GUARDIANS`](#rule-3-event-types--removal-of-child_and_1_or_2_guardians)
  - [3. Known Operational Consequences](#3-known-operational-consequences)
  - [4. Cross-Repository Alignment](#4-cross-repository-alignment)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Enrolment and Capacity Decisions (Hekla Release)

This document records the architectural and domain decisions regarding event capacity, enrolment participant counts, and seat calculations introduced in the **Hekla** release.

---

## 1. Background & Context

In pre-Hekla versions of Kukkuu:
- `Occurrence.capacity_per_occurrence` (and `Occurrence.capacity_override`) represented the number of child invitations (booking slots).
- Event organizers intentionally configured occurrence capacity to half of the physical venue capacity (e.g. 10 slots for a 20-seat room), knowing that every child must be accompanied by an adult.
- In the database, each enrolment record (`Enrolment`) represented 1 booking and was treated as consuming 1 unit of capacity.
- Reporting aggregates (`reports/serializers.py`) used a heuristic multiplier (e.g. `1.9`) to estimate total attendees.

With the introduction of dynamic enrolments and family events (allowing families with up to 4 children and 2 guardians to attend together), capacity must now track **real physical seats** rather than child invitations.

---

## 2. Core Decisions & Rules

### Rule 1: Legacy-Safe Seat Accounting
- **Legacy enrolments** in the database (`extra_children_count IS NULL` and `extra_guardians_count IS NULL`) continue to count as **1 seat taken**.
- **No data migration** backfills or rewrites historical enrolments or event capacities.
- This ensures historical reports, snapshots, and metrics remain consistent without corrupting past attendance data.

### Rule 2: Real Physical Headcount for New Enrolments
- Starting in the Hekla release, new enrolments store explicit extra participant counts (`extra_children_count` and `extra_guardians_count` $\ge 0$).
- Every new enrolment requires at least 1 child and 1 guardian:
  $$\text{Total Seats} = 2 + \text{extra\_children\_count} + \text{extra\_guardians\_count}$$
- The minimum seat consumption for any new enrolment is **2 seats**.
- An occurrence with `remaining_capacity < 2` is considered full (`OCCURRENCE_FULL`).
- In the public UI (`kukkuu-ui`), an occurrence with fewer than 2 remaining seats displays *"Täynnä"* (Full), disabling enrolment and allowing guardians to subscribe to free-spot notifications instead.

### Rule 3: Event Types & Removal of `CHILD_AND_1_OR_2_GUARDIANS`
- To simplify the domain model and user experience, `Event.CHILD_AND_1_OR_2_GUARDIANS` ("Child and 1–2 guardians") has been **removed** from `Event.PARTICIPANTS_PER_INVITE_CHOICES` and the GraphQL schema.
- All existing events with `participants_per_invite = "child_and_1_or_2_guardians"` are migrated to `Event.FAMILY` (`"family"`).
- Only two event audience types exist going forward:
  1. **`CHILD_AND_GUARDIAN` ("Child and guardian")**:
     - Fixed: 1 child + 1 guardian = **2 seats**.
     - UI: Static informational notice ("2 paikkaa varataan"); no steppers.
  2. **`FAMILY` ("Family")**:
     - 1–4 children (1 primary child + 0–3 extra children) and 1–2 guardians (1 primary guardian + 0–1 extra guardian) = **2 to 6 seats**.
     - UI: Two HDS `NumberInput` steppers:
       - Extra children: min 0, max 3.
       - Extra adults: min 0, max 1.
     - **Dynamic Capacity Capping**: Stepper increments and values are clamped so that $2 + \text{extra\_children} + \text{extra\_adults} \le \text{occurrence.remainingCapacity}$.

---

## 3. Known Operational Consequences

1. **Deploy-Day Effect**:
   - Legacy enrolments consume 1 seat, but any *new* enrolment requires at least 2 seats.
   - Any active occurrence that has exactly 1 remaining seat at the moment Hekla is deployed will immediately become full for new enrolments.
2. **Mixed Units in Reports for Cutover Events**:
   - For events or occurrences that span the pre-Hekla and post-Hekla timeframe, `capacity`, `enrolment_count`, and `reserved_seats` reflect mixed units (invitations for old enrolments, physical headcounts for new enrolments). Historical and post-Hekla raw numbers should not be directly compared without noting the cutover.
3. **Consistent Free-Spot Threshold ($\ge 2$)**:
   - Occurrence booking, notification subscriptions (`FreeSpotNotificationSubscription`), and automatic free-spot notification dispatching all use the threshold $\ge 2$ seats (`Occurrence.has_free_seats()`). If only 1 seat opens up (e.g. from a legacy cancellation), notifications are not sent because no new enrolment can take only 1 seat.

---

## 4. Cross-Repository Alignment

- **`kukkuu` (Backend)**:
  - Database schema adds `extra_children_count`, `extra_guardians_count`, and check constraint `enrolment_extra_counts_both_or_neither`.
  - Concurrency safety via `select_for_update()` during enrolment mutations.
  - Exposes `seat_count` on `OccurrenceNode` and `total_seats` on `EnrolmentNode`.
  - Exposes `reserved_seats` on `OccurrenceSerializer` in REST reports API.
- **`kukkuu-admin` (Admin UI)**:
  - Event and occurrence forms provide helper texts instructing organizers to set real physical seat capacity.
  - `EventShow` and `OccurrenceShow` display reserved seats (`seatCount`) alongside capacity, and `OccurrenceShow` displays per-enrolment reserved seats (`totalSeats`).
- **`kukkuu-ui` (Public UI)**:
  - Dynamic enrolment modal with yellow event card, clear child/guardian details, HDS `NumberInput` steppers for `FAMILY`, in-modal success view, and cancellation breakdown.
  - WCAG 2.2 AA compliant focus management, accessible labels, and minimum target sizes.
