<!-- REMINDER: While updating changelog, also remember to update
the version in kukkuu/__init.py__ -->

## [3.6.0](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.5.0...kukkuu-v3.6.0) (2024-07-05)


### Features

* Add search and autocomplete fields to user, group and ad groups admin ([e576fd0](https://github.com/City-of-Helsinki/kukkuu/commit/e576fd00ca068b78d4e66d46be5a731b85f53f61))
* Test auth change notifications command's query count ([14c1c7d](https://github.com/City-of-Helsinki/kukkuu/commit/14c1c7dfc8eb82686bc8ac93cdddf174c908605a))


### Bug Fixes

* Improve event and event group admins with safegetters and searches ([022ca8d](https://github.com/City-of-Helsinki/kukkuu/commit/022ca8d14f36551cedd093ffd60f19615725da3f))

## [3.5.0](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.4.0...kukkuu-v3.5.0) (2024-06-14)


### Features

* Batch user is_obsolete updating in auth change command ([7e89c1b](https://github.com/City-of-Helsinki/kukkuu/commit/7e89c1b237fd20e348b948175a44042cf52131d0))


### Bug Fixes

* Add missing success messages to user and guardian admin actions ([21f4e69](https://github.com/City-of-Helsinki/kukkuu/commit/21f4e6933dbe774dc17e762687f5e824aaa0c78e))

## [3.4.0](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.3.0...kukkuu-v3.4.0) (2024-06-13)


### Features

* Add --obsolete_handled_users & --batch_size to auth change command ([272ef3d](https://github.com/City-of-Helsinki/kukkuu/commit/272ef3dfdc025d3c44df67845faaa4e8e8a83983))
* Add links and filters from guardian to user and vice versa in admin site ([9f870f2](https://github.com/City-of-Helsinki/kukkuu/commit/9f870f2f9f69e8a709060f9c542d4c381f5d0458))
* Send auth service changing notifications from admin ([e37c0de](https://github.com/City-of-Helsinki/kukkuu/commit/e37c0de0ef0fcb205e29bd515015a62b71a6f2c8))


### Bug Fixes

* Children event history markdown line endings and indentations ([efd595d](https://github.com/City-of-Helsinki/kukkuu/commit/efd595d9194d232002155df2c109435a04382bd4))

## [3.3.0](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.2.0...kukkuu-v3.3.0) (2024-06-12)


### Features

* Add AuthServiceNotificationService to mass mail when auth service is changed ([1665cd9](https://github.com/City-of-Helsinki/kukkuu/commit/1665cd9ca40a25daa74b0dbdb212884461a78c0e))
* Add children event history markdown generator ([64f5c69](https://github.com/City-of-Helsinki/kukkuu/commit/64f5c699f1001c440ba3bca7dc35787c4127148d))
* Add for_auth_service_is_changing_notification in guardian queryset ([6dfcb37](https://github.com/City-of-Helsinki/kukkuu/commit/6dfcb37645be3111f03f79f84b3856452c3da96a))
* Add guardian admin actions to generate auth service changing email ([4609f9a](https://github.com/City-of-Helsinki/kukkuu/commit/4609f9aeb329d1e508ab3112a660635470ae6240))
* Add management command to send auth service changing notifications ([4d786aa](https://github.com/City-of-Helsinki/kukkuu/commit/4d786aa9128de13bb59d7095a6e7485dd1a67e88))
* Use a list of emails to filter recipients on auth service notification ([9fd0746](https://github.com/City-of-Helsinki/kukkuu/commit/9fd0746e1461902177f26962d3553635e5f0bbdd))


### Bug Fixes

* Add apps.py for Kukkuu mailer app ([8ff158c](https://github.com/City-of-Helsinki/kukkuu/commit/8ff158c43b297483ba4e06e2f5029b53da49861b))
* Improve the django_mailer admin list display view ([2cf4be0](https://github.com/City-of-Helsinki/kukkuu/commit/2cf4be0c852700a3a87927f64716f27c480d79cf))
* Remove children_event_history_markdown from notification dummy context ([40c4c11](https://github.com/City-of-Helsinki/kukkuu/commit/40c4c11d711dadedfcecadf5f52aa40f07d896e1))
* Rename kukkuu_mailer to kukkuu_mailer_admin ([8722395](https://github.com/City-of-Helsinki/kukkuu/commit/8722395d1bbfde7b996419d1e798ec88af438303))

## [3.2.0](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.1.0...kukkuu-v3.2.0) (2024-06-04)


### Features

* Add back channel logout support ([0d10bf3](https://github.com/City-of-Helsinki/kukkuu/commit/0d10bf33721ba82d785012ba3a25ac472eb9a804))
* Add Child.notes TextField, ChildNotes query and update mutation ([4476961](https://github.com/City-of-Helsinki/kukkuu/commit/44769612849ea08fbd1b3b970a9b6e788ffa3f96))
* Add Child.notes TextField, ChildNotes query and update mutation ([4ff79c4](https://github.com/City-of-Helsinki/kukkuu/commit/4ff79c4555c69a2cdaead3b0b993da54b98314fe))
* Add obsoleted props and features to User and Child ([cf473de](https://github.com/City-of-Helsinki/kukkuu/commit/cf473de282507f85ff8593f1ba0c0ced259704c0))
* Always use user's email in SubmitChildrenAndGuardianMutation ([df89bf9](https://github.com/City-of-Helsinki/kukkuu/commit/df89bf9bde50f399086baba019440267c1c3278d))
* Do not send event invitations to those who have rejected them ([75c12c1](https://github.com/City-of-Helsinki/kukkuu/commit/75c12c10bb8e9ff90ef2d3371b541205f1567fa6))
* Replace has_accepted_marketing with has_accepted_communication ([d6bfa17](https://github.com/City-of-Helsinki/kukkuu/commit/d6bfa1737764da714715498225ca56402c9fb78c))
* Send event and event group publish notification in a thread ([5510465](https://github.com/City-of-Helsinki/kukkuu/commit/55104659cd7f051318e598d2a8288a351f36dc02))
* Serialize the models used by the GDPR API ([9dc697b](https://github.com/City-of-Helsinki/kukkuu/commit/9dc697ba2f10efcb36a8baea9f9e05134c4c176f))
* The GDPR service to clear sensitive fields of user and guardian ([6ba1260](https://github.com/City-of-Helsinki/kukkuu/commit/6ba1260dc55680f4d2004ee33bfc69dbad5c39e4))


### Bug Fixes

* Add env-variable for GDPR API authorization field ([8ac6f45](https://github.com/City-of-Helsinki/kukkuu/commit/8ac6f459a57bfc3e60773b7ea858334e0772d31f))
* Api authorization field ([f0c0528](https://github.com/City-of-Helsinki/kukkuu/commit/f0c052811ef914b7c335ce9ca93b68895f27377e))
* Api authorization field ([4ebfe1c](https://github.com/City-of-Helsinki/kukkuu/commit/4ebfe1c42467a803c0ae15ef6abf88632eae8290))
* Move api authorization field to oidc config ([56be176](https://github.com/City-of-Helsinki/kukkuu/commit/56be176c3b82a522df8aed2ef42287e016b1568c))
* Projects model objects manager ([8958aff](https://github.com/City-of-Helsinki/kukkuu/commit/8958affda6a81e55d50715117b8b8912d8d9d7e9))
* Upgrade the django-helusers to fix issues with GDPR API auth ([56b58dd](https://github.com/City-of-Helsinki/kukkuu/commit/56b58dd6cebba638c5cdef45096440e9d8092006))


### Documentation

* Add some gdpr api tester app instructions ([9dc697b](https://github.com/City-of-Helsinki/kukkuu/commit/9dc697ba2f10efcb36a8baea9f9e05134c4c176f))
* Env-variables for the Tunnistamo and the Keycloak ([a7f1109](https://github.com/City-of-Helsinki/kukkuu/commit/a7f1109cb98e328c9df8d9db618d2e9002ad9067))
* How to integrate with Helsinki-Profile through Tunnistamo ([469256f](https://github.com/City-of-Helsinki/kukkuu/commit/469256f80c882273d8dba779519ce1eddb679693))
* Improvements ([2348c1c](https://github.com/City-of-Helsinki/kukkuu/commit/2348c1c5c997e8a64e19b5cf1461c4271d5d2577))

## [3.1.0](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.0.0...kukkuu-v3.1.0) (2024-03-27)


### Features

* Add "has accepted marketing" -field to the guardian model ([90cc46c](https://github.com/City-of-Helsinki/kukkuu/commit/90cc46c62cf7a02f9b8df883ef1303e54008d21d))
* Add "has accepted marketing" field to the GuadianInput ([46fe887](https://github.com/City-of-Helsinki/kukkuu/commit/46fe887c2d824bec6a21e9e58b1c6cde21e852e9))
* Add accept marketing field to my profile mutation with auth token decoration ([826f254](https://github.com/City-of-Helsinki/kukkuu/commit/826f254b1ca82e37c4ccd8cf5b0fa0d3585c3ea8))
* Add query and mutation for guardian marketing subscriptions ([45a50be](https://github.com/City-of-Helsinki/kukkuu/commit/45a50be4b24adfa8b521a0234640e72782857582))
* Add unsubscribe links to the sendings of the notifications ([7d54dfb](https://github.com/City-of-Helsinki/kukkuu/commit/7d54dfba61fdbae0b40620ab5a87fdaeda7d437c))
* Auth verification token ([2ea2635](https://github.com/City-of-Helsinki/kukkuu/commit/2ea263507fe2feb43243ae9d0cfd5ea91aef4550))
* Decorator that populates context's user from auth token given as an input ([242cff0](https://github.com/City-of-Helsinki/kukkuu/commit/242cff04eb0885f92b1742696084d81b78b9de10))
* Graphql api for user to unsubscribe from all notifications ([7a44a4a](https://github.com/City-of-Helsinki/kukkuu/commit/7a44a4a394eeac828e019f7703f209740f668913))
* User can unsubscribe from all the notifications at once ([26ebc3e](https://github.com/City-of-Helsinki/kukkuu/commit/26ebc3efee15e79286b5738c4ab38107c4dacbf0))
* Username and email available from AdminNode ([6b8f90f](https://github.com/City-of-Helsinki/kukkuu/commit/6b8f90f2fdcb481beb3b8ef017700a3e88e74de2))


### Bug Fixes

* **admin:** Search and filter guardians with guardian and user emails ([e218f09](https://github.com/City-of-Helsinki/kukkuu/commit/e218f090ddd0b86614699379692c7ab7d7655e28))
* Build in CI fails because of factory usage during build time ([e64fb28](https://github.com/City-of-Helsinki/kukkuu/commit/e64fb281c767795d4fca41d08f9b373c827e8f83))


### Documentation

* Subscriptions ([222eaea](https://github.com/City-of-Helsinki/kukkuu/commit/222eaeac0803ada3f5910bf92218b65ba1732491))
* Users schema ([04f8448](https://github.com/City-of-Helsinki/kukkuu/commit/04f8448da37fbbd3c3d4344eab5c41d746264410))

## [3.0.0](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v2.0.0...kukkuu-v3.0.0) (2024-02-14)


### ⚠ BREAKING CHANGES

* prevented email changing with the update my profile mutation

### Features

* Get active verification tokens for user ([8205b26](https://github.com/City-of-Helsinki/kukkuu/commit/8205b263adddbbc8043c997604d14a2c8227b2d3))
* Prevented email changing with the update my profile mutation ([e545b06](https://github.com/City-of-Helsinki/kukkuu/commit/e545b068416adee1a681be8215a7d7fb3b9a464c))
* Request email change token from the graphql-api ([dc81c71](https://github.com/City-of-Helsinki/kukkuu/commit/dc81c71b6e89c08b9eca86c580e64f349d24316c))
* Send the email change verification token to the new email ([bfa37cf](https://github.com/City-of-Helsinki/kukkuu/commit/bfa37cf5be16558f9e332b47189e512f880fc1b1))
* Update my email mutation ([af91c7f](https://github.com/City-of-Helsinki/kukkuu/commit/af91c7f93de6d496744b49ad108d74efa5928503))
* Verification tokens for user email verification ([e806cf6](https://github.com/City-of-Helsinki/kukkuu/commit/e806cf6db19fee751f60f47da2640e8d29b5c175))


### Bug Fixes

* Admin site user-group-relationship shouldn't be filtered for admins only ([141d308](https://github.com/City-of-Helsinki/kukkuu/commit/141d30849767cfb55d60d0cee0b56e0e47ed7cbe))
* Build issues in CI environment ([93c3a32](https://github.com/City-of-Helsinki/kukkuu/commit/93c3a32854b418c217abb768e3c00ed460df0b7e))

## [2.0.0](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v1.17.2...kukkuu-v2.0.0) (2024-01-22)


### ⚠ BREAKING CHANGES

* child update mutation input should not have birthdate field
* reporter API's birth_year renamed to birthyear
* change birthyear type from date to integer
* rename the birthdate field of the child model to be birthyear
* rename the  first name field of the child model to "name"
* remove the last name field from the Child model

### Features

* Change birthyear type from date to integer ([e1b6fc2](https://github.com/City-of-Helsinki/kukkuu/commit/e1b6fc28f66cf8e8a1ca643a641d9caf6b5bf8ba))
* Child update mutation input should not have birthdate field ([2005529](https://github.com/City-of-Helsinki/kukkuu/commit/20055297510ec123a39da61ee47080ecc179f2cc))
* Remove the last name field from the Child model ([aca4664](https://github.com/City-of-Helsinki/kukkuu/commit/aca4664869705922d4a782597cba81c7c3bfbdda))
* Rename the  first name field of the child model to "name" ([1b5c7ed](https://github.com/City-of-Helsinki/kukkuu/commit/1b5c7edd482eb5af85fbddabbe69b0c789fecc8f))
* Rename the birthdate field of the child model to be birthyear ([d9f5b17](https://github.com/City-of-Helsinki/kukkuu/commit/d9f5b17ffcd3d87056baa3b81b641523b1f566f3))
* Reporter API's birth_year renamed to birthyear ([b712e73](https://github.com/City-of-Helsinki/kukkuu/commit/b712e733dc03e0cf23d23f5ad866f72d61fb6056))


### Bug Fixes

* Make more consistent querysets and test for children reports API ([c771380](https://github.com/City-of-Helsinki/kukkuu/commit/c771380e1e5a5bda84f7df9606935aa0664375a1))

## [1.17.2](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v1.17.1...kukkuu-v1.17.2) (2023-12-15)


### Bug Fixes

* Dockerfile base on ubi image DEVOPS-560 ([#329](https://github.com/City-of-Helsinki/kukkuu/issues/329)) ([6c788ee](https://github.com/City-of-Helsinki/kukkuu/commit/6c788ee42e381eb10e5a359a73cc597e09634495))
* Pagination of the DjangoFilterAndOffsetConnectionField and the Children-query ([526055d](https://github.com/City-of-Helsinki/kukkuu/commit/526055decaffa646784a1a3813d6c58d56236ebd))

## [1.17.1](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v1.17.0...kukkuu-v1.17.1) (2023-06-29)


### Bug Fixes

* Netcat package update DEVOPS-541 ([#324](https://github.com/City-of-Helsinki/kukkuu/issues/324)) ([ffa68b9](https://github.com/City-of-Helsinki/kukkuu/commit/ffa68b9d3fb58652fb1fd0da0c76ca3bb05e19de))

## [1.17.0] - 10 May 2023

### Added

- Add Lippupiste as an external ticket system

## [1.16.2] - 17 Apr 2023

### Changed

- Sastoken is used for Azure storage autentication

## [1.16.1] - 9 Mar 2023

### Fixed

- Process notifications sending outside the atomic transaction of saving of events

## [1.16.0] - 8 Dec 2022

### Added

- Add horizontal pod autoscaler
- Add Platta related configurations
- Count ticket system passwords toward yearly enrolment limit
- Add `assignTicketSystemPasswordMutation` & tests
- Add GraphQL query for fetching a child's all internal and external enrolments
- Add import ticket system passwords mutation
- Add ticket system password counts to event API
- Add external ticket system event URL
- Implement end time handling for external ticket system events

### Fixed

- Fix child enrolment counting related to Ticketmaster events
- Fix `canChildEnroll` query related to Ticketmaster events
- Fix free ticket system password detection

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

[unreleased]: https://github.com/City-of-Helsinki/kukkuu/compare/release-1.16.0...HEAD
[1.16.0]: https://github.com/City-of-Helsinki/kukkuu/compare/release-1.15.1...release-1.16.0
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
