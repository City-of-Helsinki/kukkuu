<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Setup Keycloak](#setup-keycloak)
  - [Use the public test Keycloak](#use-the-public-test-keycloak)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Setup Keycloak

## Use the public test Keycloak

The needed environment variables:

```
TOKEN_AUTH_AUTHSERVER_URL=https://tunnistus.test.hel.ninja/auth/realms/helsinki-tunnistus
TOKEN_AUTH_ACCEPTED_AUDIENCE=kukkuu-api-dev,profile-api-test
TOKEN_AUTH_ACCEPTED_SCOPE_PREFIX=
TOKEN_AUTH_REQUIRE_SCOPE_PREFIX=False
GDPR_API_QUERY_SCOPE=gdprquery
GDPR_API_DELETE_SCOPE=gdprdelete
HELUSERS_BACK_CHANNEL_LOGOUT_ENABLED=True
```
