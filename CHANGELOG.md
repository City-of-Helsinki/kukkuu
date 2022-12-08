<!-- REMINDER: While updating changelog, also remember to update
the version in kukkuu/__init.py__ -->

## [1.15.1] - 27 May 2022

### Fixed

- Child can only enroll into published events. Rather small extra check, since unpublished events were not visible.

## [1.15.0] - 6 Apr 2022

### Added

- Republish an event group
- Events occurrences have to be on the same year
- Query for child's upcoming events and event groups

### Changed

- Ticket is show until 1 hour after the event has ended.

## [1.14.0] - 9 Mar 2022

### Added

- QR-codes used as tickets and sent with emails
- The messaging API supports SMS-messages

## [1.13.0] - 10 Jan 2022

### Added

- Add initial reporting API
- Add feedback notification

## Changed

- Ignore authentication expired error from Sentry
- Change reminder notification "days in advance" to 1

## Fixed

- Validate that event and occurrences are not given when message is for INVITED
- Fix manual messages directed to INVITED to work with event groups
- Ignore extra cruft coming from graphql-python from Sentry

## [1.12.0] - 14 Dec 2021

### Changed

- Renewed authentication implementation

## Fixed

- Fixed projects admin UI language tabs

## [1.11.1] - 13 Oct 2021

### Fixed

- Fix free spot subscription handling in event group

## [1.11.0] - 13 Sep 2021

### Added

- Add initial external ticket system event support
- Validate that one cannot enrol to multiple events of the same event group

## [1.10.5] - 10 Jun 2021

### Changed

- Send free text email messages in an atomic transaction
- Default to sending queued emails
- Increase production CPU and RAM limits

## [1.10.4] - 26 May 2021

### Changed

- Send event/event group publish notifications in an atomic transaction
- Increase email sending cronjobs' timeouts to 1h

### Fixed

- Fix a notification context language issue which caused some parts of notifications being sometimes in wrong language

## [1.10.3] - 23 Mar 2021

### Changed

- Increase production cpu limit

## [1.10.2] - 10 Mar 2021

### Fixed

- Fix Mailgun API credentials

## [1.10.1] - 2 Mar 2021

### Fixed

- Fix GHA production config
- Fix handling of a child's project in admin UI

## [1.10.0] - 2 Mar 2021

### Added

- Add "single events allowed" flag to Project model
- Add permission for managing event groups
- Allow granting publish permission to all projects
- Add GHA production config

### Changed

- Do not log readiness and healthz endpoints

### Fixed

- Temporary auth fix required by the latest Tunnistamo

## [1.9.0] - 11 Feb 2021

### Added

- Add new permission system
- Multiple minor admin UI enhancements
- Add notification importer that imports email notifications' texts from Google Spreadsheets

### Changed

- Do not delete past enrolments when child is deleted
- Forbid unenrolling from occurrences in the past
- Delete children when their only guardian is deleted
- Migrate periodic tasks to K8s cronjobs

### Fixed

- Fix UserManager
- Fix notifications' dummy contexts

## [1.8.0] - 17 Dec 2020

### Added

- Add event group functionality
- Add `availableForChild(childId)` filter to `EventNode`

### Changed

- Disable django-parler caching
- Migrate CI/CD to GitHub actions
- Exclude unenrolled events from `ChildNode.pastEvents()`
- Add ordering for API's `translations` fields

## [1.7.0] - 12 Nov 2020

### Added

- Add manual message functionality

## [1.6.0] - 16 Oct 2020

### Added

- Add Free spot notification functionality
- Add languages spoken at home for guardians
- Add `get_global_id()` to event notifications' contexts
- Add occurrence enrol URL to event notifications' contexts
- Add special language "Other language"

### Changed

- Update default languages

### Fixed

- Fix API version string when running `manage.py` outside the app directory
- Fix occurrence remaining capacity when capacity override is 0

## [1.5.1] - 30 Sep 2020

### Added

- Add localtime function to event notification templates

## [1.5.0] - 30 Sep 2020

### Added

- Add upcoming occurrence reminder notification
- Add `upcoming_with_leeway` occurrence filter
- Add enrolled events past enough (default 30 mins from the start) to a child's past events
- Add initial API for subscribing and viewing free spot subscriptions (N.B. the functionality itself has NOT been implemented yet, just the API)

### Changed

- Do not purge email logs by default in CI/CD config

## [1.4.0] - 15 Sep 2020

### Added

- Add nullable field `capacityOverride` and API for it which allows setting capacity per occurrence
- Add ability to search children and guardians in admin UI

## [1.3.0] - 2 Sep 2020

### Added

- Add occurrence url to event notifications' contexts
- Add general support for database stored languages and an API for fetching those
- Add languages spoken at home for children and an API for handling those
- Add new choice "1 child and 1 or 2 adults" to participants per invite choices

## [1.2.0] - 17 Aug 2020

### Added

- Add project filter to children, venues, events and occurrences queries
- Add nullable boolean field `attended` to `Enrolment` model and mutation `SetEnrolmentStatus` for updating it
- Add logging of mutations
- Add "occurrence cancelled" notification
- Add limit/offset pagination to children query

### Changed

- Change guardians, children, events, occurrences and enrolments viewing and administrative mutations to be allowed only for project admins of the corresponding project. Previously `User` model's `is_staff` field was used to give permissions for all projects.
- Order venues by Finnish name in API queries
- Change default logging level to INFO
- Hide unpublished events in `ChildNode` `past_events` and `available_events` fields for project admins as well

### Fixed

- Fix a bug in `OccurrenceNode` `remainingCapacity` field
- Fix a bug in `OccurrenceNode` `enrolmentCount` field

## [1.1.0] - 29 May 2020

### Added

- Add occurrence language
- Return occurrence & child from unenrolment mutation
- Add null field validation when updating objects
- Add setting to enable graphiql in staging
- Add custom depth limit backend
- Add event filter to occurrences query
- Add `enrolmentCount` to `OccurrenceNode`
- Add `name` to project model
- Make event UI URL available to event published notification
- Add `projects` to `MyAdminProfileNode`
- Allow a guardian to change her email when registering and when modifying her profile. A new notification is sent when the latter happens.

### Changed

- Change mutations' `translations` field behaviour: from now on, translations for languages that are not sent are deleted
- Change event publish notification to be sent to every child of the project

### Removed

- Remove `translationsToDelete` from all mutations that had it
- Remove `users` from `ProjectNode`
- Remove `isProjectAdmin` from `MyAdminProfileNode`

### Fixed

- Fix required fields in occurrence mutations
- Use `ParticipantsPerInvite` enum in event mutation inputs

## [1.0.0] - 30 Mar 2020

### Added

- Add availableEvents and pastEvents to child query
- Add translation fields as normal fields into Venue and Event
- Add occurrence filters (date/time/venue)
- Add remaining capacity to occurrence node
- Add CDN for image storage
- Add MyAdminProfile API query
- Add version/revision number to admin interface
- Add translation validations
- Add better GraphQL error code

### Updated

- Update Django to 2.2.10
- Update README.md

### Fixed

- Fix API queries to use RelationshipTypeEnum like mutations do
- Better UWSGI cron job to handle email sending
- Make LanguageEnum required in some queries
- Email goes to spam in some strict filter
- Minor gitlab config fixes

## [0.2.0] - 17 Feb 2020

### Added

- Add enrolment API for child to enrol event occurrences
- Add support to update event image
- Add event capacity validation to event
- Add publish events API
- Add Django Admin publish event action
- Send notifications to guardians when an event published

### Updated

- Update API to support nested fields update/delete

### Fixed

- Fix API queries to use RelationshipTypeEnum like mutations do

## 0.1.0 - 29 Jan 2020

### Added

- API for signup/login and query my profile
- Send notifications when signed up successfully
- API to query, add, update and remove children
- API to query, add, update and remove events
- API to query, add, update and remove occurrences
- API to query, add, update and remove venues

[unreleased]: https://github.com/City-of-Helsinki/kukkuu/compare/release-1.15.1...HEAD
[1.15.1]: https://github.com/City-of-Helsinki/kukkuu/compare/release-1.15.0...release-1.15.1
[1.15.0]: https://github.com/City-of-Helsinki/kukkuu/compare/release-1.14.0...release-1.15.0
[1.14.0]: https://github.com/City-of-Helsinki/kukkuu/compare/release-1.13.0...release-1.14.0
[1.13.0]: https://github.com/City-of-Helsinki/kukkuu/compare/release-1.12.0...release-1.13.0
[1.12.0]: https://github.com/City-of-Helsinki/kukkuu/compare/release-1.11.1...release-1.12.0
[1.11.1]: https://github.com/City-of-Helsinki/kukkuu/compare/release-1.11.0...release-1.11.1
[1.11.0]: https://github.com/City-of-Helsinki/kukkuu/compare/release-1.10.5...release-1.11.0
[1.10.5]: https://github.com/City-of-Helsinki/kukkuu/compare/release-1.10.4...release-1.10.5
[1.10.4]: https://github.com/City-of-Helsinki/kukkuu/compare/release-1.10.3...release-1.10.4
[1.10.3]: https://github.com/City-of-Helsinki/kukkuu/compare/release-1.10.2...release-1.10.3
[1.10.2]: https://github.com/City-of-Helsinki/kukkuu/compare/release-1.10.1...release-1.10.2
[1.10.1]: https://github.com/City-of-Helsinki/kukkuu/compare/release-1.10.0...release-1.10.1
[1.10.0]: https://github.com/City-of-Helsinki/kukkuu/compare/v1.9.0...release-1.10.0
[1.9.0]: https://github.com/City-of-Helsinki/kukkuu/compare/v1.8.0...v1.9.0
[1.8.0]: https://github.com/City-of-Helsinki/kukkuu/compare/v1.7.0...v1.8.0
[1.7.0]: https://github.com/City-of-Helsinki/kukkuu/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/City-of-Helsinki/kukkuu/compare/v1.5.1...v1.6.0
[1.5.1]: https://github.com/City-of-Helsinki/kukkuu/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/City-of-Helsinki/kukkuu/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/City-of-Helsinki/kukkuu/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/City-of-Helsinki/kukkuu/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/City-of-Helsinki/kukkuu/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/City-of-Helsinki/kukkuu/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/City-of-Helsinki/kukkuu/compare/v0.2.0...v1.0.0
[0.2.0]: https://github.com/City-of-Helsinki/kukkuu/compare/v0.1.0...v0.2.0
