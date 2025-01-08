<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Helsinki-Profile with Tunnistamo](#helsinki-profile-with-tunnistamo)
  - [OIDC provider clients](#oidc-provider-clients)
    - [Helsinki-Profile API](#helsinki-profile-api)
    - [Helsinki-Profile UI](#helsinki-profile-ui)
  - [OIDC API](#oidc-api)
    - [Helsinki-profile API](#helsinki-profile-api)
  - [OIDC API scopes](#oidc-api-scopes)
    - [Helsinki-profile API Scope](#helsinki-profile-api-scope)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Helsinki-Profile with Tunnistamo

## OIDC provider clients

Model: `oidc_provider.models.Client`

### Helsinki-Profile API

Important fields with their values:

```python
{
    "name": "Helsinkiprofile",
    "response_types": [<ResponseType: code (Authorization Code Flow)>]>,
    "client_type": "confidential",
    "client_id": "https://api.hel.fi/auth/helsinkiprofile",
    "client_secret": "52625d8d2661df1710076956808725588deabb2d9902b06003d78764",
    "jwt_alg": "RS256",
    "reuse_consent": True,
    "require_consent": True,
    "_redirect_uris": "https://oidcdebugger.com/debug http://open-city-profile-ui:3000/callback http://localhost:3000/callback http://open-city-profile-ui:3000/gdpr-callback http://localhost:3000/gdpr-callback",
    "_scope": ""
}
```

> NOTE: The `client_secret` will be automatically generated when the client type is set to `confidential`.

The following command can be used to create the client in Tunnistamo:

```shell
./manage.py add_oidc_client \
  --confidential \
  --name "Helsinkiprofile" \
  --response_types "code" \
  --redirect_uris "https://oidcdebugger.com/debug http://open-city-profile-ui:3000/callback http://localhost:3000/callback http://open-city-profile-ui:3000/gdpr-callback http://localhost:3000/gdpr-callback" \
  --client_id https://api.hel.fi/auth/helsinkiprofile \
  --site_type dev \
  --login_methods "github"
```

### Helsinki-Profile UI

```python
{
 "name": "Helsinkiprofile-ui",
 "response_types": [<ResponseType: code (Authorization Code Flow)>]>,
 "client_type": "public",
 "client_id": "https://api.hel.fi/auth/helsinkiprofile-ui",
 "client_secret": "",
 "jwt_alg": "RS256",
 "reuse_consent": True,
 "require_consent": True,
 "_redirect_uris": "http://open-city-profile-ui:3000/callback http://open-city-profile-ui:3000/silent_renew http://localhost:3000/callback http://localhost:3000/silent_renew",
 "_scope": "openid profile https://api.hel.fi/auth/helsinkiprofile"}
```

The following command can be used to create the client in Tunnistamo:

```shell
./manage.py add_oidc_client \
  --name "Helsinkiprofile-ui" \
  --response_types "code" \
  --redirect_uris "http://localhost:3000/callback" "http://localhost:3000/silent_renew" \
  --client_id "helsinkiprofile-ui" \
  --site_type dev \
  --login_methods "github"
```

## OIDC API

Model: `oidc_apis.models.Api`

### Helsinki-profile API

Important fields with their values:

```python
{
  'name': 'helsinkiprofile',
  'required_scopes': ['email', 'profile'],
  'oidc_client': <Client: Helsinkiprofile>,
}
```

The following command can be used to create the API in Tunnistamo:

```shell
./manage.py add_oidc_api \
  --name helsinkiprofile \
  --domain https://api.hel.fi/auth \
  --scopes profile email \
  --client_id https://api.hel.fi/auth/helsinkiprofile
```

## OIDC API scopes

Model: `oidc_apis.models.ApiScope`

### Helsinki-profile API Scope

```python
{
    'identifier': 'https://api.hel.fi/auth/helsinkiprofile',
    'api': <Api: https://api.hel.fi/auth/helsinkiprofile>,
    'specifier': '',
    "_allowed_apps": [<Client: helsinki-profile>, <Client: helsinki-profile-ui>, <Client: kukkuu-api>, <Client: kukkuu-ui>, <Client: kukkuu-admin-ui>]
}
```

The following command can be used to create the API scope in Tunnistamo:

```shell
./manage.py add_oidc_api_scope \
  --name "helsinkiprofiletest" \
  --description "Profile backend" \
  --api_name helsinkiprofile \
  --client_ids "https://api.hel.fi/auth/helsinkiprofile-ui"
```

> NOTE: Other apps may need to be allowed as well, like shown in the "important fields".
