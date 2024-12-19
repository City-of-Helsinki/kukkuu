<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Culture Kids with Helsinki-Profile GDPR API through Tunnistamo](#culture-kids-with-helsinki-profile-gdpr-api-through-tunnistamo)
  - [OIDC API scopes](#oidc-api-scopes)
    - [Kukkuu GDPR Query API Scope Specifier](#kukkuu-gdpr-query-api-scope-specifier)
    - [Kukkuu GDPR Delete API Scope Specifier](#kukkuu-gdpr-delete-api-scope-specifier)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Culture Kids with Helsinki-Profile GDPR API through Tunnistamo

## OIDC API scopes

Model: `oidc_apis.models.ApiScope`

### Kukkuu GDPR Query API Scope Specifier

Important fields with their values:

```python
{
    "identifier": "https://api.hel.fi/auth/kukkuu.gdprquery",
    "specifier": "gdprquery",
    "api": <Api: https://api.hel.fi/auth/kukkuu>,
    "_allowed_apps": [<Client: helsinki-profile>,]
}
```

### Kukkuu GDPR Delete API Scope Specifier

Important fields with their values:

```python
{
    "identifier": "https://api.hel.fi/auth/kukkuu.gdprdelete",
    "specifier": "gdprdelete",
    "api": <Api: https://api.hel.fi/auth/kukkuu>,
    "_allowed_apps": [<Client: helsinki-profile>,]
}
```
