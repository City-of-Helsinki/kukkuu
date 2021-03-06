<!-- REMINDER: While updating changelog, also remember to update
the version in kukkuu/__init.py__ -->

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




[Unreleased]: https://github.com/City-of-Helsinki/kukkuu/compare/v1.8.0...HEAD
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

