### Users app

#### Models

##### User

The User model is the one that the Kukkuu app uses as a [default User model](https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#referencing-the-user-model). It extends the AbstractUser model class provided by the _Helusers app_.

> The User model is the one that the Django framework, Helsinki's authentication systems and all the plugins are using for the authentication and authorization.

##### Guardian

The Guardian model is using a 1-to-1 foreignkey to the User-model. It's purpose is to extend the user model so that the Kukkuu's child specific data is separated to another data model, so the User stays more close to the Django's own abstract implementation. Like that, the guardian-user -relationship is more detachable and extendable.

#### GraphQL Schema

[The Users GraphQL schema](./schema.py) contains query fields to read data and mutation fields to update data.

##### Guardians

The `guardians` query gives a list of guardians, but the viweing is limited so that current user can see only himself and only the admin users can see all the guardians.

##### My profile

The `myProfile`-query returns the guardian's data for the current logged in user. The contact information and also the user and the children data are available through the GuardianNode. The data is sensible in that sense.

There is a mutation field `UpdateMyProfileMutation` to update the data that the my profile query provides.

> NOTE: The email field value is not updetable through the `UpdateMyProfileMutation`. There is `UpdateMyEmailMutation` field for that.

###### Update the email

The guardian email field can be updated with the `UpdateMyEmailMutation`. The email field is specia, because we want to verify that the guardian user really has an access to the email box that he updates to their profile.

The `UpdateMyEmailMutation` usage always requires an email verification token. The token can be requested with the `RequestEmailUpdateTokenMutation`. A successful request to the `RequestEmailUpdateTokenMutation` should send an email to the email box that the user is updating the field value to. A request to the `UpdateMyEmailMutation` can only be successful with that provided token as an input.

###### Manage communication subscriptions

The guardian model also has (some or at least one) fields that are used to allow or disallow sending of some notifications to the user. The user can accept or reject the permissions to receive those notifications through the `UpdateMyCommunicationSubscriptionsMutation`.

The communication subscriptions management is a bit special feature in sense that it is something that relates to a user (or to my profile), but is also something that needs to be accessible also when the user is not able to login. In some cases, a guardian user may receive some notifications in their inbox because they have at some point allowed notifications to be sent to them, but at some point they would still like to unsubscribe from those notifications. However, user may no longer be able to access his account, so user needs another way to get authorization for his information. The Verification tokens app provides a [verification token model](../verification_tokens/models.py) with specific types for just that.

The `VerificationToken` with a type `VERIFICATION_TYPE_SUBSCRIPTIONS_AUTH` can be linked to a guardian user and that token key can be included in the unsubscribe link provided in each mail that are sent to the user's email box.

> Because that authorization token compromises the security of the system a bit, the token should be used only with actions that are carefully planned and with endpoints that does not offer very sensible data.

If the user has not authenticated to the Kulttuurin kummilapset, the user could still pass the "has logged in" test by using that authorization token as an input (in endpoints where the input is defined to be available). There is a [decorator](../verification_tokens/decorators.py) to help with the user authorization process.

##### My admin profile

The `MyAdminProfile` -query returns an `AdminNode` for the users who are logged in and has the admin privileges. From the `AdminNode` the user has access to all the projects and their events and enrolments data.
