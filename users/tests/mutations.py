UPDATE_MY_PROFILE_MUTATION = """
mutation UpdateMyProfile($input: UpdateMyProfileMutationInput!) {
  updateMyProfile(input: $input) {
    myProfile {
      firstName
      lastName
      phoneNumber
      language
      languagesSpokenAtHome {
        edges {
          node {
            alpha3Code
          }
        }
      }
      hasAcceptedCommunication
    }
  }
}
"""

UPDATE_MY_EMAIL_MUTATION = """
mutation UpdateMyEmail($input: UpdateMyEmailMutationInput!) {
  updateMyEmail(input: $input) {
    myProfile {
      email
    }
  }
}
"""

REQUEST_EMAIL_CHANGE_TOKEN_MUTATION = """
mutation RequestEmailUpdateToken($input: RequestEmailUpdateTokenMutationInput!) {
    requestEmailUpdateToken(input: $input) {
        email
        emailUpdateTokenRequested
    }
}
"""


UPDATE_MY_COMMUNICATION_SUBSCRIPTIONS_MUTATION = """
mutation UpdateMyCommunicationSubscriptions(
  $input: UpdateMyCommunicationSubscriptionsMutationInput!
) {
  updateMyCommunicationSubscriptions(input: $input) {
    guardian {
      firstName,
      lastName
      language,
      hasAcceptedCommunication
    }
  }
}
"""
