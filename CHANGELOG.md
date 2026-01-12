<!-- DOCTOC SKIP -->
<!-- REMINDER: While updating changelog, also remember to update
the version in kukkuu/__init.py__ -->

## [3.17.1](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.17.0...kukkuu-v3.17.1) (2026-01-12)


### Bug Fixes

* Send manual emails only to active users ([4ba2cf6](https://github.com/City-of-Helsinki/kukkuu/commit/4ba2cf618c22ea5b73efea5f7f259007edc45257))


### Dependencies

* Bump authlib from 1.6.5 to 1.6.6 ([31763a4](https://github.com/City-of-Helsinki/kukkuu/commit/31763a4e64ec0e47a768be151b14f74fc6b68566))
* Bump django from 5.2.8 to 5.2.9 ([e843a13](https://github.com/City-of-Helsinki/kukkuu/commit/e843a130ba5faa8b7cce46bb8c706f2db6682f8d))

## [3.17.0](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.16.1...kukkuu-v3.17.0) (2025-11-26)


### Features

* Allow Sentry uWSGI-plugin to be optional ([0d94fc6](https://github.com/City-of-Helsinki/kukkuu/commit/0d94fc618af3dbef0b2b8d560d3b677bee65c0be))
* **sentry:** Update sentry configuration ([016a04a](https://github.com/City-of-Helsinki/kukkuu/commit/016a04ad71a8281519c74a225dbed3912dae19c2))
* Use separate AUDIT_LOG_ENV variable ([8e2e283](https://github.com/City-of-Helsinki/kukkuu/commit/8e2e28386b004d75c441ff5406eaa8284d16076e))

## [3.16.1](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.16.0...kukkuu-v3.16.1) (2025-11-12)


### Dependencies

* Bump django from 5.2.7 to 5.2.8 ([1861caf](https://github.com/City-of-Helsinki/kukkuu/commit/1861caf3f8cbce544815b5ba6c8f798a313aa3be))

## [3.16.0](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.15.3...kukkuu-v3.16.0) (2025-11-05)


### Features

* Add resilient_logger for audit log transport ([#522](https://github.com/City-of-Helsinki/kukkuu/issues/522)) ([8bafb61](https://github.com/City-of-Helsinki/kukkuu/commit/8bafb61dc5382e84e6902e9744c903396d088d27))
* Enable json logging for uwsgi ([#521](https://github.com/City-of-Helsinki/kukkuu/issues/521)) ([9612a4b](https://github.com/City-of-Helsinki/kukkuu/commit/9612a4b99e7242ec3b3089f0def0f4fe70832a70))
* Transition to structured (json) logging ([#508](https://github.com/City-of-Helsinki/kukkuu/issues/508)) ([2037da4](https://github.com/City-of-Helsinki/kukkuu/commit/2037da4b4134cc1d286bb8913e34a9517db78234))

## [3.15.3](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.15.2...kukkuu-v3.15.3) (2025-10-22)


### Bug Fixes

* Make admin descriptions django 5.2 compatible ([4b9a0f7](https://github.com/City-of-Helsinki/kukkuu/commit/4b9a0f7b8b832dfc1d81efa8195ce3fe1e45fc6d))


### Dependencies

* Upgrade django-csp to version 4 ([5f994d6](https://github.com/City-of-Helsinki/kukkuu/commit/5f994d627b80035c5ccd6204bfb0c87b5189a490))
* Upgrade to django 5.2 and all applicable deps ([95ecfa1](https://github.com/City-of-Helsinki/kukkuu/commit/95ecfa111885bd2b8d8d6b4c3ef1c04f5818c662))


### Documentation

* Adjust README about ruff ([5439eb5](https://github.com/City-of-Helsinki/kukkuu/commit/5439eb5be22f62de7a457ffac7108fbe5bf54aa7))

## [3.15.2](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.15.1...kukkuu-v3.15.2) (2025-10-15)


### Bug Fixes

* Switch to psycopg-c ([d380aac](https://github.com/City-of-Helsinki/kukkuu/commit/d380aac9265015cc86e107700456342b221bf6ae))


### Dependencies

* Use pre-commit ruff ([dcb31ac](https://github.com/City-of-Helsinki/kukkuu/commit/dcb31ac06044422eef6c06a082500bf42b6f9a6d))

## [3.15.1](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.15.0...kukkuu-v3.15.1) (2025-10-13)


### Dependencies

* Bump authlib from 1.6.4 to 1.6.5 ([b788634](https://github.com/City-of-Helsinki/kukkuu/commit/b788634ef0e2eecd1edd61ae5c5d0a75dd87486f))
* Bump django from 4.2.24 to 4.2.25 ([5ffd573](https://github.com/City-of-Helsinki/kukkuu/commit/5ffd573c3b22e4277ef531bfdee8ff62c691dba3))

## [3.15.0](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.14.2...kukkuu-v3.15.0) (2025-10-03)


### Features

* Use DATABASE_PASSWORD if present in env ([fe6daa0](https://github.com/City-of-Helsinki/kukkuu/commit/fe6daa0526a1dd75b94e6bd2c870b4c3af047cbf))

## [3.14.2](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.14.1...kukkuu-v3.14.2) (2025-09-23)


### Dependencies

* Bump authlib from 1.5.1 to 1.6.4 ([0e0c419](https://github.com/City-of-Helsinki/kukkuu/commit/0e0c419a43e747cab44de6d9563c097ba8c0f39e))

## [3.14.1](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.14.0...kukkuu-v3.14.1) (2025-09-10)


### Dependencies

* Bump django from 4.2.22 to 4.2.24 ([4dbb3a3](https://github.com/City-of-Helsinki/kukkuu/commit/4dbb3a33a3c7db66d92df0696a999133e4271893))

## [3.14.0](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.13.0...kukkuu-v3.14.0) (2025-08-05)


### Features

* Improve uWSGI options ([c47d5e2](https://github.com/City-of-Helsinki/kukkuu/commit/c47d5e24c7ad68357c9700dc646bdde0b718a173))
* Send reminder notifications earlier ([46c274b](https://github.com/City-of-Helsinki/kukkuu/commit/46c274b5d3482546609d30d60dbb0122ec5cdc1b))


### Bug Fixes

* Explicitly define Azure URL expiration time ([fc9ea43](https://github.com/City-of-Helsinki/kukkuu/commit/fc9ea4339f20bdf1104b72f863bef7030abceffa))
* Prevent SAS token exposure in client URLs ([89d2927](https://github.com/City-of-Helsinki/kukkuu/commit/89d2927b5483e3ee4ff93bf52d7d216e6e909074))
* Simplify Azure storage settings ([00d3720](https://github.com/City-of-Helsinki/kukkuu/commit/00d3720b4b4e6e6ec0a21715f594718e2a7b8d90))
* Update Azure storage settings ([0a74401](https://github.com/City-of-Helsinki/kukkuu/commit/0a744010c3f746ff9d5c3e47ad61aa02b686cf92))


### Dependencies

* Add uwsgitop ([8ac7809](https://github.com/City-of-Helsinki/kukkuu/commit/8ac78091c9fdba0707774e8b1090e310221cb54a))
* Bump requests from 2.32.3 to 2.32.4 ([92f2210](https://github.com/City-of-Helsinki/kukkuu/commit/92f22107cd51c85eef095ad36087588306346bd1))

## [3.13.0](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.12.4...kukkuu-v3.13.0) (2025-06-09)


### Features

* Reject unenrolments if less than 48h to the event occurrence ([f196eba](https://github.com/City-of-Helsinki/kukkuu/commit/f196eba56201557db8e13bf21fdc8c1ad90bcb11))
* Remove is_obsolete field from user model ([9f8e77d](https://github.com/City-of-Helsinki/kukkuu/commit/9f8e77d26b4363527aa7ae07a44bfcebdb14efc6))
* Send notification only to active and non-oboleted users ([3bb8df6](https://github.com/City-of-Helsinki/kukkuu/commit/3bb8df6bef0123612a3669345624e949918ceb6a))


### Dependencies

* Bump django from 4.2.21 to 4.2.22 ([f7f87c5](https://github.com/City-of-Helsinki/kukkuu/commit/f7f87c5ef8ec307bfdde226db11b3575431f9166))

## [3.12.4](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.12.3...kukkuu-v3.12.4) (2025-05-14)


### Bug Fixes

* **settings:** Add missing verification and subscription token settings ([c46ab2e](https://github.com/City-of-Helsinki/kukkuu/commit/c46ab2e6f509f5a6f010cc380e7c63c86027f3f0))


### Dependencies

* Bump django from 4.2.20 to 4.2.21 ([e58192e](https://github.com/City-of-Helsinki/kukkuu/commit/e58192e61a6c41d0facf9032ede4eef04d725eee))

## [3.12.3](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.12.2...kukkuu-v3.12.3) (2025-03-10)


### Bug Fixes

* Logout by upgrading deps to latest, incl. django-helusers v0.13.3 ([cf4cd41](https://github.com/City-of-Helsinki/kukkuu/commit/cf4cd41a04fcfe16510abae84d2b6ff8d6374566))

## [3.12.2](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.12.1...kukkuu-v3.12.2) (2025-03-07)


### Bug Fixes

* Disable browser tests by default in .env.example ([3e7ef79](https://github.com/City-of-Helsinki/kukkuu/commit/3e7ef791e8c44cc0f3b653f6e498dd89cd5b8230))
* **security:** Update dependencies to latest ([69e42ba](https://github.com/City-of-Helsinki/kukkuu/commit/69e42ba067874cfcd5107a29fbeb461ed505a048))

## [3.12.1](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.12.0...kukkuu-v3.12.1) (2025-03-05)


### Bug Fixes

* **keycloak:** Use helusers.defaults.SOCIAL_AUTH_PIPELINE ([53dde11](https://github.com/City-of-Helsinki/kukkuu/commit/53dde1146834c96395c603fe03bd5973b4ead8f1))
* **security:** Upgrade all dependencies, incl. python-jose v3.3 → v3.4 ([6effbf6](https://github.com/City-of-Helsinki/kukkuu/commit/6effbf64326fb1eb58a1e2faf5b3fa452c64c68c))
* **sonarcloud:** Dockerfile docker:S6504 security hotspots ([b7d1645](https://github.com/City-of-Helsinki/kukkuu/commit/b7d1645114190138d86504eee6e826021b6e41c1))
* **sonarcloud:** Don't hardcode debug mode SECRET_KEY, update README ([1431d6b](https://github.com/City-of-Helsinki/kukkuu/commit/1431d6b3dc71375d8ad482a14fd4b624362350ad))
* **sonarcloud:** Generate PEM key pair in tests instead of hardcoding it ([bb127eb](https://github.com/City-of-Helsinki/kukkuu/commit/bb127ebade1bb712637c9617d3c32ed1230a914e))
* **sonarcloud:** Ignore ul-wrapping of li with //NOSONAR, django does it ([82b09d2](https://github.com/City-of-Helsinki/kukkuu/commit/82b09d2a5962b0d29098b347573626e6df0623d2))
* **sonarcloud:** Move DATABASE_URL default to .env.example ([0461678](https://github.com/City-of-Helsinki/kukkuu/commit/04616781f075d3f4da32dff2ef74459b1b0679dc))
* **sonarcloud:** Only allow safe methods for readiness endpoint ([085336c](https://github.com/City-of-Helsinki/kukkuu/commit/085336ce0663d171cb5489a452e1e5b8d5c7fb49))
* **sonarcloud:** Use faker's random_element, not random.choice ([c4f7f0a](https://github.com/City-of-Helsinki/kukkuu/commit/c4f7f0a39a25919ca2c39c6b82fd7d3b0a17b1fe))
* **sonarcloud:** Use None for verification_token_user_full_name w/o user ([35932bd](https://github.com/City-of-Helsinki/kukkuu/commit/35932bd635dafc22a32d0a594ec9a121d02c9ef6))
* **sonarcloud:** Use tempfile for creating MAILER_LOCK_PATH default ([2b4e89f](https://github.com/City-of-Helsinki/kukkuu/commit/2b4e89fde5316cf04adc81ab2e889873ed382228))
* **sonarcloud:** Use zoneinfo.ZoneInfo instead of pytz.timezone ([d2937b8](https://github.com/City-of-Helsinki/kukkuu/commit/d2937b81877b6495cfb8812fb4dd2b459ffa08bb))


### Documentation

* Add mention to set secret from the keyvault ([e8f3537](https://github.com/City-of-Helsinki/kukkuu/commit/e8f3537d87771a69899312db4475335543376ae6))

## [3.12.0](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.11.0...kukkuu-v3.12.0) (2025-02-17)


### Features

* Enable Helsinki city employees' django-admin Keycloak login ([e83b768](https://github.com/City-of-Helsinki/kukkuu/commit/e83b7685b4740734883b7b3760ef0eaab6df1923))


### Bug Fixes

* Django-admin logout by not importing helusers SOCIAL_AUTH_PIPELINE ([2d14cbe](https://github.com/City-of-Helsinki/kukkuu/commit/2d14cbe34119a8fbce8216ea8f838724ae9a92b1))
* Updating requirements by moving non-PyPI packages to own .txt file ([afb0d4f](https://github.com/City-of-Helsinki/kukkuu/commit/afb0d4f20e7fe3c84d99d730adc853121941ef93))


### Dependencies

* Bump cryptography from 44.0.0 to 44.0.1 ([6ee4a51](https://github.com/City-of-Helsinki/kukkuu/commit/6ee4a5190ed93eb799303c5cfaf25f01bf9145ae))

## [3.11.0](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.10.0...kukkuu-v3.11.0) (2025-02-06)


### Features

* Add view families permission, restrict child/guardian info with it ([e89195b](https://github.com/City-of-Helsinki/kukkuu/commit/e89195b9ff2decee4086ba47de61df8f585d20b4))
* **auditlog-extra:** Add request path to additional data in LogEntry ([59c3d46](https://github.com/City-of-Helsinki/kukkuu/commit/59c3d4685e65808a399d7b58d85280d7e35145de))
* **auditlog-extra:** Admin mixin ([8f4e56a](https://github.com/City-of-Helsinki/kukkuu/commit/8f4e56a4f394769741f6d61607c1e5a36bd8d550))
* **auditlog-extra:** Configuration helper ([00165e6](https://github.com/City-of-Helsinki/kukkuu/commit/00165e6ad89bf0a1bca6f83b55d65597808c0cde))
* **auditlog-extra:** Decorator ([e7b9257](https://github.com/City-of-Helsinki/kukkuu/commit/e7b92579e3fc08e5ac6ea7b851bb144a8e3b6bad))
* **auditlog-extra:** Middleware ([0e63451](https://github.com/City-of-Helsinki/kukkuu/commit/0e63451fc9771c7c39d81bb5b6e658e9e353407b))
* **auditlog:** Installed django-auditlog ([e0f2f04](https://github.com/City-of-Helsinki/kukkuu/commit/e0f2f04b837d9561576659b67304fe043db7dbd7))
* **auditlog:** Write access log of restricted graphene nodes ([9ba8fad](https://github.com/City-of-Helsinki/kukkuu/commit/9ba8fad2c93d1454500d1d3eb2864c2739aa6786))
* **auditlog:** Write access logs of restricted admin models ([e4fa72d](https://github.com/City-of-Helsinki/kukkuu/commit/e4fa72daa683d73dc7f1a4c29bbb8c2a39765385))
* **csp:** Install and configure django-csp ([8c6bb7d](https://github.com/City-of-Helsinki/kukkuu/commit/8c6bb7d5f8b251da5cd048630f273a709e9950dc))
* **devops:** Liveness probe to test the database connection ([1dcc0ff](https://github.com/City-of-Helsinki/kukkuu/commit/1dcc0ff2ba76819fd3e8235da0a07e622a573c1b))
* **devops:** Readiness probe to give build and release info ([f8db348](https://github.com/City-of-Helsinki/kukkuu/commit/f8db34822e3d94ef85f0ca112354982d48abc3a8))
* **sentry:** Ignore authentication expired errors in Sentry ([f232111](https://github.com/City-of-Helsinki/kukkuu/commit/f2321118d2d691b95a7ca268e1d03d2bb18a5269))


### Bug Fixes

* "The USE_L10N setting is deprecated" deprecation warning ([9f0abc1](https://github.com/City-of-Helsinki/kukkuu/commit/9f0abc17873af8d26657c7abf64a7628701ce328))
* /graphql/ GraphiQL interface by changing CSP rules ([0a01103](https://github.com/City-of-Helsinki/kukkuu/commit/0a011035749834e0b9bcf7dd48a0790064889b79))
* Add validation to AssignTicketSystemPasswordMutation ([b0aa5e2](https://github.com/City-of-Helsinki/kukkuu/commit/b0aa5e2b8439489017d107384873b0bb1ff7c03e))
* **auditlog-extra:** Admin mixin should use get_changelist_instance ([7d71f4c](https://github.com/City-of-Helsinki/kukkuu/commit/7d71f4c94ce7ee829880c726c5caf19c4d41d870))
* **auditlog-extra:** Duplicated log creation prevention in admin mixin ([a427992](https://github.com/City-of-Helsinki/kukkuu/commit/a427992e21f969825f520badd426a646e84b320f))
* **auditlog-extra:** Explicitly define app_label for DummyTestModel ([551eb46](https://github.com/City-of-Helsinki/kukkuu/commit/551eb4616c65d3b426317bffa4f3b20f337bd89b))
* **auditlog:** Exclude mailer models from auditlog ([3f06c0b](https://github.com/City-of-Helsinki/kukkuu/commit/3f06c0bb503854d582b80d9b535393f236f288fc))
* **config:** Admin ui url ([f5e0d24](https://github.com/City-of-Helsinki/kukkuu/commit/f5e0d2418516e9745d06c9c1992af7f6a502ff71))
* **csp:** Circular import in settings ([38ff1b5](https://github.com/City-of-Helsinki/kukkuu/commit/38ff1b5e6a60154cb8b7b82b9cf98f4e23bf81af))
* **csp:** Spectacular redoc view ([f6ee5b6](https://github.com/City-of-Helsinki/kukkuu/commit/f6ee5b62eebc3a698e21c293b667f4c5c3f0cde5))
* DEFAULT_FILE_STORAGE deprecation warning by using STORAGES instead ([808d500](https://github.com/City-of-Helsinki/kukkuu/commit/808d500b0a3f30e79d20e19e7adaffc24346e068))
* Docker-compose.env.example & README.md to work out of the box ([444bd2f](https://github.com/City-of-Helsinki/kukkuu/commit/444bd2f131b36b82a495726f7b78d0168c4de986))
* Docker-compose.env.yaml* → docker-compose.env*, it's not YAML ([9167b06](https://github.com/City-of-Helsinki/kukkuu/commit/9167b06f74ffbff6bb21b581d780ef85bb336253))
* **docker:** Docker compose should use expose 8000 port for prod target ([ee8dfae](https://github.com/City-of-Helsinki/kukkuu/commit/ee8dfaed023f252e2520f4216a4e6f820999d4be))
* Graphene-django warning that DjangoObjectType needs fields/exclude ([8be20af](https://github.com/City-of-Helsinki/kukkuu/commit/8be20afc9b63898f4fe3c890e0b0a00c4a0bcbd4))
* Remove ChildNode deprecation warnings and document fields' behavior ([00846ec](https://github.com/City-of-Helsinki/kukkuu/commit/00846ecc65240fd7b58ee4c8ca171687dd842ee7))
* Report event serializer type hint warning ([ebf0b8a](https://github.com/City-of-Helsinki/kukkuu/commit/ebf0b8a5b4f6494667304ad5e45b8ebcb4a96c9c))
* Sentry_sdk deprecation warning by using current scope ([ebc5d65](https://github.com/City-of-Helsinki/kukkuu/commit/ebc5d6563aade650907139dd362390d82a8a0e9f))
* Update projects to db using migrations and management commands ([1ff44a0](https://github.com/City-of-Helsinki/kukkuu/commit/1ff44a08f9f49e193feb25c71730c711d8d35f7d))


### Dependencies

* Bump django from 4.2.17 to 4.2.18 ([2fa1cfb](https://github.com/City-of-Helsinki/kukkuu/commit/2fa1cfbbfd9d5444e22d0a70c71964cb09d9c1d5))


### Documentation

* "the Tunnistamo" → Tunnistamo, no need for the definite article ([f6b08d4](https://github.com/City-of-Helsinki/kukkuu/commit/f6b08d4daf38e796f63bcacf841d17f94ef063f5))
* Add kukkuu api link ([c745b14](https://github.com/City-of-Helsinki/kukkuu/commit/c745b14a2be15a280911fd74284e0728ddcdc071))
* Add Node.js to requirements because of pre-commit hook's doctoc ([3f3acc7](https://github.com/City-of-Helsinki/kukkuu/commit/3f3acc78cf1c6f8f6508e2dbbbfcb08b28253c01))
* Architecture and environments ([4a8002e](https://github.com/City-of-Helsinki/kukkuu/commit/4a8002ee89e6a6e7141ab8c227f69c11fffbf709))
* **auditlog-extra:** Add a note to test schema ([cfcc44b](https://github.com/City-of-Helsinki/kukkuu/commit/cfcc44bfc0e8b3c003903d2a1569a05b4e280f32))
* **auditlog-extra:** Add toc, refactor the api section, improve ([a5f4c81](https://github.com/City-of-Helsinki/kukkuu/commit/a5f4c81d4385d771b5688e1d211c7a111d33c942))
* **auditlog-extra:** Audit logging principles ([0398b3a](https://github.com/City-of-Helsinki/kukkuu/commit/0398b3a26fa479c65936b320e0019f547486c8b4))
* **auditlog-extra:** Readme and FAQ ([4804965](https://github.com/City-of-Helsinki/kukkuu/commit/480496504c12d6ea0328f59a48b7050e1ebcd31c))
* **auditlog:** Add audit logging to the project readme ([fefcfb5](https://github.com/City-of-Helsinki/kukkuu/commit/fefcfb5f979873e283fd96c2176edb2234055cc1))
* Browser testing jwt ([bade39f](https://github.com/City-of-Helsinki/kukkuu/commit/bade39f231c9c754cf5ddf972f0f059c5362d760))
* Clarify "Keeping Python requirements up to date" with Docker ([81001c0](https://github.com/City-of-Helsinki/kukkuu/commit/81001c0e898804d2ec319428a2af27a2f3c60f5b))
* Clarify adding coupon codes for external ticket system events ([465338b](https://github.com/City-of-Helsinki/kukkuu/commit/465338bdde78b696550018b8dfe8a47cfc43c5c5))
* Clarify how to create a superuser in backend ([411fc0e](https://github.com/City-of-Helsinki/kukkuu/commit/411fc0e7b7cacbfaff6abf52809482dad421239f))
* Clarify Keycloak/Tunnistamo use in GDPR/README.md ([cbc890c](https://github.com/City-of-Helsinki/kukkuu/commit/cbc890ccff66bc8807df5c2f94da6d626edff9af))
* Clarify pre-commit hook section ([764e122](https://github.com/City-of-Helsinki/kukkuu/commit/764e122bc5550f9ce8739f7f1e5e4a7cce311180))
* Correct the facts in readme ([caf2fbc](https://github.com/City-of-Helsinki/kukkuu/commit/caf2fbccef27943dd74ac39dfdb311bb61c9f384))
* Fix GDPR API export ER diagram relationships/cardinalities ([1ae9306](https://github.com/City-of-Helsinki/kukkuu/commit/1ae930642d929810e476c1cef8a297fcd46883f5))
* Fix JWT & Tunnistamo related texts & wordwrap them ([07568ee](https://github.com/City-of-Helsinki/kukkuu/commit/07568ee8b7152c7e632e52f9e2e14977c47192ba))
* Miscellaneous cleanup / clarifications to READMEs ([5fed8be](https://github.com/City-of-Helsinki/kukkuu/commit/5fed8bea6403a8985e49a292262592755f526d45))
* Move "Daily running, Debugging" under "Development without Docker" ([2109286](https://github.com/City-of-Helsinki/kukkuu/commit/210928623fc8c6cbf85483cae8c2b191cdf4f4e8))
* Move & expand requirements ([bb9163b](https://github.com/City-of-Helsinki/kukkuu/commit/bb9163bce32ddd8c4cfdc5d6d4418d233fd41591))
* Notification import source ([2c2e677](https://github.com/City-of-Helsinki/kukkuu/commit/2c2e677647693d96b6b8ded0056b863986dc2486))
* Refactor the content order ([c0eefa2](https://github.com/City-of-Helsinki/kukkuu/commit/c0eefa28ea2fc85c3b03dc59356c19e52411d61d))
* Releases, deployments and release-please ([ca8e46a](https://github.com/City-of-Helsinki/kukkuu/commit/ca8e46a1d34b1e7f71c0631ec502c24d0cc65abe))
* Remove redundancy from code linting & formatting section ([4645bc5](https://github.com/City-of-Helsinki/kukkuu/commit/4645bc5eaafbff847ab9737f3e349c9f9c9fd516))
* Remove unnecessary link wrappings, fix release-please action link ([64d52a5](https://github.com/City-of-Helsinki/kukkuu/commit/64d52a54080437981d0d615a691576d80471a2ab))
* Ticketing systems ([cc4c014](https://github.com/City-of-Helsinki/kukkuu/commit/cc4c014bbc0e2799c1617ad596fdb5f80725f8f4))
* Update headings and table of contents ([23b75fc](https://github.com/City-of-Helsinki/kukkuu/commit/23b75fccfc5a6699422139328a9630814ed7e531))

## [3.10.0](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.9.0...kukkuu-v3.10.0) (2024-11-25)


### Features

* Add hasAnyFreePasswords to ExternalEventTicketSystem ([915e85a](https://github.com/City-of-Helsinki/kukkuu/commit/915e85a46b74ffad40836a01827c57237baccfad))

## [3.9.0](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.8.0...kukkuu-v3.9.0) (2024-10-31)


### Features

* Add  canSendToAllInProject permission to myAdminProfile query ([462f72c](https://github.com/City-of-Helsinki/kukkuu/commit/462f72c415eb13770f2d0411d6c273c45f0a2848))
* Add ticket validity to enrolment admin ([623d553](https://github.com/City-of-Helsinki/kukkuu/commit/623d553b1701bb35968c687ecd287d2d257d122c))
* Add Ukrainian language to LANGUAGE_CHOICES ([1806127](https://github.com/City-of-Helsinki/kukkuu/commit/1806127a577f5fecc55f4a755b2f3a874c57cd0b))
* Admin view for enrolments ([7df154f](https://github.com/City-of-Helsinki/kukkuu/commit/7df154f601b155dd5831e9bbacebf1ac7122c5a0))
* Attendance information given in ticket verification ([8cf9bb1](https://github.com/City-of-Helsinki/kukkuu/commit/8cf9bb17c3b493c02061f23228f2f20cfc1c8d0b))
* **auth:** Authentication with graphene_jwt instead of custom implementation ([815cb27](https://github.com/City-of-Helsinki/kukkuu/commit/815cb27bcabada3443d72841860c819b37265ab9))
* Autocomplete feature to ticket system admin event field ([ff7e4e9](https://github.com/City-of-Helsinki/kukkuu/commit/ff7e4e9cd933e9c7a8207da9d51eb47cdebfa55e))
* Enrolment reference id is viewable from the enrolment admin ([616dca1](https://github.com/City-of-Helsinki/kukkuu/commit/616dca1123324f25426042fd640801659072215f))
* Event report API with event group and venue view sets as helpers ([b438915](https://github.com/City-of-Helsinki/kukkuu/commit/b43891583706d5a383541c1bff3a68ece325d595))
* Project message permissions for sending to all ([d15578b](https://github.com/City-of-Helsinki/kukkuu/commit/d15578b0e84acf078b414a96e45339f348c14024))
* Tixly ticket system ([2e0c9eb](https://github.com/City-of-Helsinki/kukkuu/commit/2e0c9eb417a481c16eaa73053fbe9243f3179a20))
* Update ticket attended status ([b9eefcb](https://github.com/City-of-Helsinki/kukkuu/commit/b9eefcb36f9d5160218551ed60cef7f60cd33af2))


### Bug Fixes

* **admin:** Performance and UX issue in messaging admin ([4acdc93](https://github.com/City-of-Helsinki/kukkuu/commit/4acdc93eac4ba80356f9496b1e7e31b4c58401a6))
* Browser test resources creation for pytests ([3de8cbb](https://github.com/City-of-Helsinki/kukkuu/commit/3de8cbbe1f42d1f5dafae61c8503ae7725e7023f))
* Get_translations_dict utility's database usage ([81e87d6](https://github.com/City-of-Helsinki/kukkuu/commit/81e87d650a352a5a7289bbee71a11e438d859de6))
* Upgrade django-ilmoitin to fix migration issues ([3c43107](https://github.com/City-of-Helsinki/kukkuu/commit/3c43107125fad31a741884904276eaf9ca8806e6))

## [3.8.0](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.7.1...kukkuu-v3.8.0) (2024-09-18)


### Features

* Add count field to messages connection ([c9a4415](https://github.com/City-of-Helsinki/kukkuu/commit/c9a441508aba1fc5a4d41a1b5d42651b6d8eef79))
* Add order_by field to messages query ([0cb3bfb](https://github.com/City-of-Helsinki/kukkuu/commit/0cb3bfb4abac4cd63298fea81eeed0ad51ae38a3))
* Use DjangoFilterAndOffsetConnectionField with messages query ([1c38e39](https://github.com/City-of-Helsinki/kukkuu/commit/1c38e39a3635f6695e8f053e1b5999a16bee081b))


### Bug Fixes

* Link and subject field in the messaging admin list display ([e584d75](https://github.com/City-of-Helsinki/kukkuu/commit/e584d7583096e438d53cd8a34e17ed1ed351f7e1))

## [3.7.1](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.7.0...kukkuu-v3.7.1) (2024-09-05)


### Bug Fixes

* Logging level default value ([42c91a1](https://github.com/City-of-Helsinki/kukkuu/commit/42c91a144392745fab8f142a1ac8c4b77d71aa9c))

## [3.7.0](https://github.com/City-of-Helsinki/kukkuu/compare/kukkuu-v3.6.0...kukkuu-v3.7.0) (2024-09-05)


### Features

* Add more fields and filters to messaging admin view ([d70dfe9](https://github.com/City-of-Helsinki/kukkuu/commit/d70dfe909eab6cbac5badbf125664f0c60ab6df9))
* Authenticate symmetrically signed JWT with shared secret for browser tests ([718d92c](https://github.com/City-of-Helsinki/kukkuu/commit/718d92cbf35dca7ad14c9b8e99c63174b9318bc8))
* Provide initial browser test data automatically ([7250605](https://github.com/City-of-Helsinki/kukkuu/commit/72506053f941f48f74521c5808e27f9d33b6c410))
* Switch setup.cfg -&gt; pyproject.toml, black/isort/flake8 -> ruff ([4d8e834](https://github.com/City-of-Helsinki/kukkuu/commit/4d8e834747470f1134fa316186c935467dada974))
* Upgrade Django to 4.2 & upgrade all packages to latest ([e5b12aa](https://github.com/City-of-Helsinki/kukkuu/commit/e5b12aae778db6270d57de67bc0dd3d5870efa28))
* Upgrade to Python 3.11 ([553b964](https://github.com/City-of-Helsinki/kukkuu/commit/553b964b2902c5352700fc4c0f46a36c785158eb))


### Bug Fixes

* Allow schema introspection for unauthenticated users ([e8879aa](https://github.com/City-of-Helsinki/kukkuu/commit/e8879aa5a6c6cd29e7b88cd909281108a3fea08b))
* Default test project creation ([ab76ba7](https://github.com/City-of-Helsinki/kukkuu/commit/ab76ba7b4efa6b752cb40668f14e929de72f08d7))
* Event group creation bug in admin ([8ff4042](https://github.com/City-of-Helsinki/kukkuu/commit/8ff4042de598c76a68f91e60f565606d64540028))
* Making event groups events publishable should not clear event group ([e00f931](https://github.com/City-of-Helsinki/kukkuu/commit/e00f93168a837dcdda67f56187b666370b6c8416))
* Message api filters for protocol and occurrences ([9277462](https://github.com/City-of-Helsinki/kukkuu/commit/9277462ea0c7e5379b08e5b08672ffe1ebe187c9))
* Oidc debug extra usage ([a9a3d46](https://github.com/City-of-Helsinki/kukkuu/commit/a9a3d4611a1e57ea5e4ad0a8f1f613dbb005125c))
* Oidc debug extra usage ([f1265a1](https://github.com/City-of-Helsinki/kukkuu/commit/f1265a14a6ecdfb1b661c78ba8410bab2a91b53e))

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
