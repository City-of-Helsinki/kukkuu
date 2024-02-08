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
