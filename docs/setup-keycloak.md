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
