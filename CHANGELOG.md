<!-- REMINDER: While updating changelog, also remember to update
the version in kukkuu/__init.py__ -->


## [0.3.0] - 30 Mar 2020
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




[Unreleased]: https://github.com/City-of-Helsinki/kukkuu/compare/v0.3.0...HEAD
[0.2.0]: https://github.com/City-of-Helsinki/kukkuu/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/City-of-Helsinki/kukkuu/compare/v0.1.0...v0.2.0

