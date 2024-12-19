<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Setup the Helsinki-Profile for internal use and for UI](#setup-the-helsinki-profile-for-internal-use-and-for-ui)
  - [Configure the internal service (for Helsinki-Profile-UI and internal Graphql-UI)](#configure-the-internal-service-for-helsinki-profile-ui-and-internal-graphql-ui)
  - [Configure the Culture kids service](#configure-the-culture-kids-service)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Setup the Helsinki-Profile for internal use and for UI

In order to get the Helsinki-Profile UI to work with API, The Helsinki-Profile services needs to be set so that they match with the Tunnistamo client ids. Also, the Helsinki-Profile API itself needs an internal service.

## Configure the internal service (for Helsinki-Profile-UI and internal Graphql-UI)

There should be a Helsinki-Profile service (`services.models.Service`) set for the Helsinki-profile itself. The own service of the Helsinki-profile is a bit special compared to other services, since it needs to have the `is_profile_service` -field set to `True`. **This service makes it possible to use the Graphene endpoint and it can also be used by the Helsinki-Profile UI client app.**

> WARNING: On this date (April of 2024) it seems like the Helsinki-profile application initialization scripts does not create that service and the Django-admin UI does not have the `is_profile_service` field editable, so the developers needs to add the service manually by theirselves by using the Django shell (python manage.py shell). While the Helsinki-Profile documentation does not tell about the internal client, the need for it can be seen from the source code

```
    def resolve_requires_service_connection(self, info, **kwargs):
        return not self.is_profile_service
```

Here are the most important fields of the Helsinki-profile service instance:

```python
{
    'service_type': None,
    'name': 'helsinki_profile',
    'idp': [],
    'gdpr_url': '',
    'gdpr_query_scope': '',
    'gdpr_delete_scope': '',
    'gdpr_audience': '',
    'is_profile_service': True
}
```

At first, a new service that acts as an internal service, can be added from the Django admin site, if one does not exist already. Name the service e.g. as `helsinki_profile`. The JWT azp-field (Authorized Party; the party this token was issued) contains the information about the client. The `services.service` must then be linked to the same client id. The definition is maintained with an env-variable in the Helsinki-Profile UI client app `REACT_APP_OIDC_CLIENT_ID="https://api.hel.fi/auth/helsinkiprofile-ui"`. **The service id must match with a client in the Tunnistamo.** It is important to **link the Helsinki-profile UI to the internal service**.

> INFO: If the client id that was set in the Helsinki-Profile (internal) service does not match with the one in the Tunnistamo when authorizing the user, a following error will be given in a response:
>
> > Client ID Error
> >
> > The client identifier (client_id) is missing or invalid.

> INFO: If a valid Tunnistamo auth token is in request Authorization-headers, but the client id does not match to any service, a following error will be given in a (GraphQL) response:

```json
{
  "errors": [
    {
      "message": "No service identified",
      "locations": [
        {
          "line": 173,
          "column": 3
        }
      ],
      "path": ["myProfile"],
      "extensions": {
        "code": "SERVICE_NOT_IDENTIFIED_ERROR"
      }
    }
  ],
  "data": {
    "myProfile": null
  }
}
```

To flag the service as Helsinki-Profile's own service, follow these steps in Django shell (`python manage.py shell`):

```python
In [1]: Service.objects.get(name="helsinki_profile")
Out[1]: <Service: Helsinki-Profile>

In [2]: s = Service.objects.get(name="helsinki_profile")

In [3]: s.is_profile_service=True

In [4]: s.save()
```

While in console, double check that the helsinki-profile UI is set as a client

```python
In [5]: [sid.client_id for sid in s.client_ids.all()]
Out[5]: ['https://api.hel.fi/auth/helsinkiprofile-ui']
```

After the service with a proper client is configured, then also the GraphQL-queries works from the profile-backend itself. [An example Helsinki-profile query to fetch my profile data used by the helsinki-Profile UI](http://profile-backend:8080/graphql/#query=fragment%20MyProfileQueryVerifiedPersonalInformationPermanentForeignAddress%20on%20VerifiedPersonalInformationForeignAddressNode%20%7B%0A%20%20streetAddress%0A%20%20additionalAddress%0A%20%20countryCode%0A%20%20**typename%0A%7D%0A%0Afragment%20MyProfileQueryVerifiedPersonalInformationPermanentAddress%20on%20VerifiedPersonalInformationAddressNode%20%7B%0A%20%20streetAddress%0A%20%20postalCode%0A%20%20postOffice%0A%20%20**typename%0A%7D%0A%0Afragment%20MyProfileQueryVerifiedPersonalInformation%20on%20VerifiedPersonalInformationNode%20%7B%0A%20%20firstName%0A%20%20lastName%0A%20%20givenName%0A%20%20nationalIdentificationNumber%0A%20%20municipalityOfResidence%0A%20%20municipalityOfResidenceNumber%0A%20%20permanentAddress%20%7B%0A%20%20%20%20...MyProfileQueryVerifiedPersonalInformationPermanentAddress%0A%20%20%20%20**typename%0A%20%20%7D%0A%20%20permanentForeignAddress%20%7B%0A%20%20%20%20...MyProfileQueryVerifiedPersonalInformationPermanentForeignAddress%0A%20%20%20%20**typename%0A%20%20%7D%0A%20%20**typename%0A%7D%0A%0Afragment%20MyProfileQueryPrimaryAddress%20on%20AddressNode%20%7B%0A%20%20id%0A%20%20primary%0A%20%20address%0A%20%20postalCode%0A%20%20city%0A%20%20countryCode%0A%20%20addressType%0A%20%20**typename%0A%7D%0A%0Afragment%20MyProfileQueryPrimaryEmail%20on%20EmailNode%20%7B%0A%20%20id%0A%20%20email%0A%20%20primary%0A%20%20emailType%0A%20%20**typename%0A%7D%0A%0Afragment%20MyProfileQueryPrimaryPhone%20on%20PhoneNode%20%7B%0A%20%20id%0A%20%20phone%0A%20%20primary%0A%20%20phoneType%0A%20%20**typename%0A%7D%0A%0Afragment%20MyProfileQueryAddressesEdgesNode%20on%20AddressNode%20%7B%0A%20%20primary%0A%20%20id%0A%20%20address%0A%20%20postalCode%0A%20%20city%0A%20%20countryCode%0A%20%20addressType%0A%20%20**typename%0A%7D%0A%0Afragment%20MyProfileQueryEmailsEdgesNode%20on%20EmailNode%20%7B%0A%20%20primary%0A%20%20id%0A%20%20email%0A%20%20emailType%0A%20%20**typename%0A%7D%0A%0Afragment%20MyProfileQueryPhonesEdgesNode%20on%20PhoneNode%20%7B%0A%20%20primary%0A%20%20id%0A%20%20phone%0A%20%20phoneType%0A%20%20**typename%0A%7D%0A%0Afragment%20MyProfileQueryAddressesEdges%20on%20AddressNodeEdge%20%7B%0A%20%20node%20%7B%0A%20%20%20%20...MyProfileQueryAddressesEdgesNode%0A%20%20%20%20**typename%0A%20%20%7D%0A%20%20**typename%0A%7D%0A%0Afragment%20MyProfileQueryEmailsEdges%20on%20EmailNodeEdge%20%7B%0A%20%20node%20%7B%0A%20%20%20%20...MyProfileQueryEmailsEdgesNode%0A%20%20%20%20**typename%0A%20%20%7D%0A%20%20**typename%0A%7D%0A%0Afragment%20MyProfileQueryPhonesEdges%20on%20PhoneNodeEdge%20%7B%0A%20%20node%20%7B%0A%20%20%20%20...MyProfileQueryPhonesEdgesNode%0A%20%20%20%20**typename%0A%20%20%7D%0A%20%20**typename%0A%7D%0A%0Afragment%20MyProfileQueryAddresses%20on%20AddressNodeConnection%20%7B%0A%20%20edges%20%7B%0A%20%20%20%20...MyProfileQueryAddressesEdges%0A%20%20%20%20**typename%0A%20%20%7D%0A%20%20**typename%0A%7D%0A%0Afragment%20MyProfileQueryEmails%20on%20EmailNodeConnection%20%7B%0A%20%20edges%20%7B%0A%20%20%20%20...MyProfileQueryEmailsEdges%0A%20%20%20%20**typename%0A%20%20%7D%0A%20%20**typename%0A%7D%0A%0Afragment%20MyProfileQueryPhones%20on%20PhoneNodeConnection%20%7B%0A%20%20edges%20%7B%0A%20%20%20%20...MyProfileQueryPhonesEdges%0A%20%20%20%20**typename%0A%20%20%7D%0A%20%20**typename%0A%7D%0A%0Afragment%20MyProfileQuery%20on%20ProfileNode%20%7B%0A%20%20id%0A%20%20firstName%0A%20%20lastName%0A%20%20nickname%0A%20%20language%0A%20%20primaryAddress%20%7B%0A%20%20%20%20...MyProfileQueryPrimaryAddress%0A%20%20%20%20**typename%0A%20%20%7D%0A%20%20addresses%20%7B%0A%20%20%20%20...MyProfileQueryAddresses%0A%20%20%20%20**typename%0A%20%20%7D%0A%20%20primaryEmail%20%7B%0A%20%20%20%20...MyProfileQueryPrimaryEmail%0A%20%20%20%20**typename%0A%20%20%7D%0A%20%20emails%20%7B%0A%20%20%20%20...MyProfileQueryEmails%0A%20%20%20%20**typename%0A%20%20%7D%0A%20%20primaryPhone%20%7B%0A%20%20%20%20...MyProfileQueryPrimaryPhone%0A%20%20%20%20**typename%0A%20%20%7D%0A%20%20phones%20%7B%0A%20%20%20%20...MyProfileQueryPhones%0A%20%20%20%20**typename%0A%20%20%7D%0A%20%20verifiedPersonalInformation%20%7B%0A%20%20%20%20...MyProfileQueryVerifiedPersonalInformation%0A%20%20%20%20**typename%0A%20%20%7D%0A%20%20**typename%0A%7D%0A%0Aquery%20MyProfile%20%7B%0A%20%20myProfile%20%7B%0A%20%20%20%20...MyProfileQuery%0A%20%20%20%20**typename%0A%20%20%7D%0A%7D%0A&operationName=MyProfile&variables=%7B%7D) (remember to use the authorization header with a bearer token issued by the Tunnistamo).

## Configure the Culture kids service

The Helsinki-Profile needs to be connected to the Culture Kids services. To do that, the Helsinki-Profile needs a new Helsinki-Profile service (`services.models.Service`) for Culture Kids, which can be added from the Django admin site.

The most important fields of the service:

```python
{
  'service_type': None,
  'name': 'godchildren_of_culture',
  'idp': [<ServiceIdp.TUNNISTAMO: 'tunnistamo'>],
  'gdpr_url': 'http://host.docker.internal:8081/gdpr-api/v1/user/$user_uuid',
  'gdpr_query_scope': 'https://api.hel.fi/auth/kukkuu.gdprquery',
  'gdpr_delete_scope': 'https://api.hel.fi/auth/kukkuu.gdprdelete',
  'gdpr_audience': 'https://api.hel.fi/auth/kukkuu',
  'is_profile_service': False
}
```

The `gdpr_query_scope` and the `gdpr_delete_scope` needs to match to the ones that are listed in the Tunnistamo in the API scopes.
While the Tunnistamo is in use (instead of the Keycloak -- in future), the IDP must be set to Tunnistamo. The audience should match with the Tunnistamo configuration too. The GDPR URL field is used to define the proper pathname in the Culture Kids service to find the GDPR API endpoint.
