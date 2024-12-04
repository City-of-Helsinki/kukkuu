<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Subscriptions app](#subscriptions-app)
  - [Free spot notifications](#free-spot-notifications)
    - [Authenticated users](#authenticated-users)
    - [Authorization with a token](#authorization-with-a-token)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

### Subscriptions app

#### Free spot notifications

Model: FreeSpotNotification

Both, the subsription and the unsubscription mutations have the same inputs.

In order to use the API, the user needs to be authorized -- Needs a logged in user or a token that represents the authorized user and his permissions.

##### Authenticated users

For authenticated users, the input takes only the child id and the occurrence id:

```
    class Input:
        occurrence_id = graphene.GlobalID()
        child_id = graphene.GlobalID()
```

The user, the child and the occurrence instances can be get from the context populated by the given input:

```
    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **kwargs):
        user = info.context.user
        child, occurrence = _get_child_and_occurrence(info, **kwargs)
```

##### Authorization with a token

To manage the subscriptions without logging in, for example clicking a link from an email, the user's subscriptions could be also handled with some tokens that are linked to the subscription.

> NOTE: This is very much needed when the user cannot log in to his own account anymore, which could be due to the fact that Tunnistamo does not support any duplicated accounts (multiple accounts for the same email) nor Facebook authentication (anymore).

The [VerificationToken model from the Verification tokens app](../verification_tokens/models.py) can be used to create tokens and link them to the subscription object.

There is also a [`user_from_auth_verification_token` -decorator](../verification_tokens/decorators.py) that sets the user linked to the authorization verification token to the request context and it can also be used along side with the `@login_required` decorator.
