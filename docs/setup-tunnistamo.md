<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Setup Tunnistamo](#setup-tunnistamo)
  - [Use a local Tunnistamo](#use-a-local-tunnistamo)
  - [Use the public test Tunnistamo](#use-the-public-test-tunnistamo)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Setup Tunnistamo

## Use a local Tunnistamo

The needed environment variables:

```
TOKEN_AUTH_AUTHSERVER_URL=http://tunnistamo-backend:8000/openid
TOKEN_AUTH_ACCEPTED_AUDIENCE=https://api.hel.fi/auth/kukkuu
TOKEN_AUTH_ACCEPTED_SCOPE_PREFIX=kukkuu
TOKEN_AUTH_REQUIRE_SCOPE_PREFIX=True
GDPR_API_QUERY_SCOPE=kukkuu.gdprquery
GDPR_API_DELETE_SCOPE=kukkuu.gdprdelete
HELUSERS_BACK_CHANNEL_LOGOUT_ENABLED=False
```

## Use the public test Tunnistamo

The needed environment variables:

```
TOKEN_AUTH_AUTHSERVER_URL=https://tunnistamo.test.hel.ninja/openid
TOKEN_AUTH_ACCEPTED_AUDIENCE=https://api.hel.fi/auth/kukkuu
TOKEN_AUTH_ACCEPTED_SCOPE_PREFIX=kukkuu
TOKEN_AUTH_REQUIRE_SCOPE_PREFIX=True
GDPR_API_QUERY_SCOPE=kukkuu.gdprquery
GDPR_API_DELETE_SCOPE=kukkuu.gdprdelete
HELUSERS_BACK_CHANNEL_LOGOUT_ENABLED=False
```
