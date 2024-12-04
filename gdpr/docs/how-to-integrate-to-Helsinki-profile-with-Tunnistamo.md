<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Integrate the Culture Kids service to the Helsinki-Profile](#integrate-the-culture-kids-service-to-the-helsinki-profile)
  - [1. Download and install all the needed services](#1-download-and-install-all-the-needed-services)
  - [2. Setup the clients and their scopes in Tunnistamo](#2-setup-the-clients-and-their-scopes-in-tunnistamo)
    - [Communication between the Culture kids apps and the Tunnistamo](#communication-between-the-culture-kids-apps-and-the-tunnistamo)
    - [Communication between the Helsinki-profile and the Tunnistamo](#communication-between-the-helsinki-profile-and-the-tunnistamo)
    - [Communication from Helsinki-profile to the Culture Kids through Tunnistamo](#communication-from-helsinki-profile-to-the-culture-kids-through-tunnistamo)
  - [3. Setup the Helsinki-Profile](#3-setup-the-helsinki-profile)
  - [4. Test that all the communication works](#4-test-that-all-the-communication-works)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Integrate the Culture Kids service to the Helsinki-Profile

## 1. Download and install all the needed services

The Culture Kids is a service environment where there is

- [Kukkuu API (Django)](https://github.com/City-of-Helsinki/kukkuu)
- [Kukkuu public UI (React)](https://github.com/City-of-Helsinki/kukkuu-ui)
- [Kukkuu admin UI (React)](https://github.com/City-of-Helsinki/kukkuu-admin)

The [Tunnistamo](https://github.com/City-of-Helsinki/tunnistamo) is used for authentication process.

The Helsinki-Profile is used maintain the user profile and its information from one place:

- [Helsinki-profile API (Django)](https://github.com/City-of-Helsinki/open-city-profile)
- [Helsinki-profile UI (React)](https://github.com/City-of-Helsinki/open-city-profile-ui)

## 2. Setup the clients and their scopes in Tunnistamo

### Communication between the Culture kids apps and the Tunnistamo

> The Culture Kids apps are already communicating with the Tunnistamo: The user authenticates from the public UI or from the admin UI and then the user's profile is read from the Kukkuu API. The JWT token is read by the django-helusers which is installed in the Kukkuu API and it will take care of updating the user information to the Kukkuu API database.

The most important Tunnistamo configurations for the Culture kids services are described in [Culture Kids with Tunnistamo](tunnistamo-kukkuu-configuration.md).

### Communication between the Helsinki-profile and the Tunnistamo

> "The Helsinki-profile is the service being integrated to the Culture Kids service, so at this point there are no configurations between the Helsinki-profile API or Helsinki-Profile UI and the Tunnistamo. Also the Helsinki-Profile UI needs to communicate properly with the API."

The most important Tunnistamo configuration for The Helsinki-Profile services are described in [Helsinki-Profile with Tunnistamo](tunnistamo-profile-configuration.md).

### Communication from Helsinki-profile to the Culture Kids through Tunnistamo

> "When the Culture Kids and the Helsinki-Profile are already communicating with Tunnistamo (the user can successfully login from the UI clients), the only part missing in order to take advantage of the GDPR API, is to add the GDPR API scope configurations to the Tunnistamo."

> NOTE: To configure the actual UI clients and the API servers to use the Helsinki-profile, see the [Setup the Helsinki-Profile](#3-setup-the-helsinki-profile) and the README files of the [application repositories](#1-download-and-install-all-the-needed-services).

To configure the Helsinki-Profile GDPR API client scopes in Tunnistamo, see the [Culture Kids with Helsinki-Profile GDPR API through Tunnistamo](tunnistamo-kukkuu-configuration.md).

## 3. Setup the Helsinki-Profile

In order to get the Helsinki-Profile UI to work with API, The Helsinki-Profile services needs to be set so that they match with the Tunnistamo client ids. Also, the Helsinki-Profile API itself needs an internal service.

To setup the Helsinki-Profile for internal use and for the Helsinki-Profile UI, see the [Setup the Helsinki-Profile for internal use and for UI](setup-helsinki-profile.md#configure-the-internal-service-for-helsinki-profile-ui-and-internal-graphql-ui).

To setup the Helsinki-Profile for Culture Kids use, see the [Setup the Helsinki-Profile for internal use and for UI](setup-helsinki-profile.md#configure-the-culture-kids-service).

## 4. Test that all the communication works

Dependencies for the user test cases:

1. The profile needs to have some connected services. A user profile can add more services to the list of the connected service from the Helsinki-Profile UI.
2. In order to test the GDPR API, the profile needs to be found from the Culture Kids API with the same UUID as it is found from the Helsinki-Profile.

When the Culture Kids UI and the API, the Tunnistamo, the Helsinki-Profile API and the Helsinki-Profile UI are all up and running...

1. As a Culture kids guardian, I can login from the Culture kids public UI to see my profile.
2. As a Helsinki-profile user, I can login from the Helsinki-profile UI to see my profile.
3. As a Helsinki-profile user, without any app connections, I can export the profile GDPR data from the Helsinki-profile UI.
4. As a Helsinki-profile user, without any app connections, I can delete the profile from the Helsinki-profile UI.
5. As a Helsinki-profile user, with a service connection to the Culture kids service, I can export the profile GDPR data from the Helsinki-profile UI and it includes the data from the Culture kids API.
6. As a Helsinki-profile user, with a service connection to the Culture kids service, I can delete / clear the profile's GDPR data from the Helsinki-profile UI and it also clears the data from the Culture kids API.
