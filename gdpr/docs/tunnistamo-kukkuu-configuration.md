<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Culture Kids with Tunnistamo](#culture-kids-with-tunnistamo)
  - [OIDC provider clients](#oidc-provider-clients)
    - [Kukkuu API](#kukkuu-api)
    - [Kukkuu UI](#kukkuu-ui)
    - [Kukkuu Admin UI](#kukkuu-admin-ui)
  - [OIDC API](#oidc-api)
    - [Kukkuu API](#kukkuu-api-1)
  - [OIDC API scopes](#oidc-api-scopes)
    - [Kukkuu API Scope](#kukkuu-api-scope)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Culture Kids with Tunnistamo

## OIDC provider clients

Model: `oidc_provider.models.Client`

### Kukkuu API

Important fields with their values:

```python
{
  "name": "kukkuu-api",
  "response_types": [<ResponseType: code (Authorization Code Flow)>]>,
  "client_type": "public",
  "client_id": "https://api.hel.fi/auth/kukkuu",
  "client_secret": "",
  "jwt_alg": "RS256",
  "reuse_consent": True,
  "require_consent": True,
  "_redirect_uris": "http://localhost:8081/return http://localhost:3000/callback",
  "_scope": "openid kukkuu.gdprquery kukkuu.delete https://api.hel.fi/auth/kukkuu"
}
```

The following command can be used to create the client in Tunnistamo:

```shell
./manage.py add_oidc_client \
  --name "kukkuu-api" \
  --response_types "code" \
  --redirect_uris "http://localhost:8081/return http://localhost:3000/callback" \
  --client_id https://api.hel.fi/auth/kukkuu \
  --scopes "openid kukkuu.gdprquery kukkuu.delete https://api.hel.fi/auth/kukkuu" \
  --site_type dev \
  --login_methods "github"
```

> NOTE: this command does not set the consent setting.

### Kukkuu UI

Important fields with their values:

```python
{
  "name": "kukkuu-ui",
  "response_types": [<ResponseType: id_token token (Implicit Flow)>]>,
  "client_type": "public",
  "client_id": "https://api.hel.fi/auth/kukkuu-ui",
  "client_secret": "",
  "jwt_alg": "RS256",
  "reuse_consent": True,
  "require_consent": True,
  "_redirect_uris": "http://localhost:3000/callback http://localhost:3000/silent_renew.html http://localhost:3001/callback http://localhost:3001/silent_renew.html http://localhost:3002/callback http://localhost:3002/silent_renew.html",
  "_scope": "openid profile https://api.hel.fi/auth/kukkuu kukkuu.query kukkuu.delete https://api.hel.fi/auth/helsinkiprofile"
}
```

> NOTE: The Kukkuu UI has been using the implicit flow, but it probably needs to be changed when the Keycloak is taken in use.

The following command can be used to create the client in Tunnistamo:

```shell
./manage.py add_oidc_client \
  --name "kukkuu-ui" \
  --response_types "id_token token" \
  --redirect_uris "http://localhost:3000/callback http://localhost:3000/silent_renew.html http://localhost:3001/callback http://localhost:3001/silent_renew.html http://localhost:3002/callback http://localhost:3002/silent_renew.html" \
  --client_id https://api.hel.fi/auth/kukkuu-ui \
  --site_type dev \
  --login_methods "github"
```

> NOTE: this command does not set the scopes nor the consent setting.

### Kukkuu Admin UI

Important fields with their values:

```python
{
  "name": "kukkuu-admin-ui",
  "response_types": [<ResponseType: id_token token (Implicit Flow)>]>,
  "client_type": "public",
  "client_id": "https://api.hel.fi/auth/kukkuu-admin-ui",
  "client_secret": "",
  "jwt_alg": "RS256",
  "reuse_consent": True,
  "require_consent": True,
  "_redirect_uris": "http://localhost:3001/callback",
  "_scope": ""
}
```

> NOTE: The Kukkuu Admin UI has been using the implicit flow, but it probably needs to be changed when the Keycloak is taken in use.

The following command can be used to create the client in Tunnistamo:

```shell
./manage.py add_oidc_client \
  --name "kukkuu-admin-ui" \
  --response_types "id_token token" \
  --redirect_uris "http://localhost:3001/callback" \
  --client_id https://api.hel.fi/auth/kukkuu-admin-ui \
  --site_type dev \
  --login_methods "github"
```

> NOTE: this command does not set the scopes nor the consent setting.

## OIDC API

Model: `oidc_apis.models.Api`

### Kukkuu API

Important fields with their values:

```python
{
  'name': 'kukkuu',
  'required_scopes': ['email', 'profile'],
  'oidc_client': <Client: kukkuu-api>,
}
```

The following command can be used to create the API in Tunnistamo:

```shell
./manage.py add_oidc_api \
  --name kukkuu \
  --domain https://api.hel.fi/auth \
  --scopes profile email \
  --client_id https://api.hel.fi/auth/kukkuu
```

## OIDC API scopes

Model: `oidc_apis.models.ApiScope`

### Kukkuu API Scope

Important fields with their values:

```python
{
    "name": "kukkuu",
    "required_scopes": ["email", "profile"],
    "oidc_client": <Client: kukkuu-api>,
    "backchannel_logout_url": None
    "_allowed_apps": [<Client: kukkuu-admin-ui>, <Client: kukkuu-ui>]
    "scopes": [<ApiScope: https://api.hel.fi/auth/kukkuu.gdprdelete>, <ApiScope: https://api.hel.fi/auth/kukkuu.gdprquery>, <ApiScope: https://api.hel.fi/auth/kukkuu>]
}
```

The following command can be used to create the API scope in Tunnistamo:

```shell
./manage.py add_oidc_api_scope \
  --name "kukkuu" \
  --description "kukkuu" \
  --api_name kukkuu \
  --client_ids "https://api.hel.fi/auth/kukkuu"
```

The following command can be used to add the related clients to the created API scope:

```shell
./manage.py add_oidc_client_to_api_scope \
  -asi https://api.hel.fi/auth/kukkuu \
  -c https://api.hel.fi/auth/kukkuu-ui
./manage.py add_oidc_client_to_api_scope \
  -asi https://api.hel.fi/auth/kukkuu \
  -c https://api.hel.fi/auth/kukkuu-admin-ui
```
