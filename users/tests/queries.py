GUARDIANS_QUERY = """
query Guardians {
  guardians {
    edges {
      node {
        firstName
        lastName
        phoneNumber
        email
        relationships {
          edges {
            node {
              type
              child {
                name
                birthyear
                project {
                  year
                }
              }
            }
          }
        }
      }
    }
  }
}
"""

MY_PROFILE_QUERY = """
query MyProfile {
  myProfile {
    firstName
    lastName
    phoneNumber
    email
    relationships {
      edges {
        node {
          type
          child {
            name
            birthyear
            postalCode
          }
        }
      }
    }
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
"""

MY_ADMIN_PROFILE_QUERY = """
query MyAdminProfile{
  myAdminProfile{
    projects {
      edges {
        node {
          name
          myPermissions {
            publish
            manageEventGroups
            canSendToAllInProject
          }
        }
      }
    }
  }
}
"""

MY_COMMUNICATION_SUBSCRIPTIONS_QUERY = """
query MyCommunicationSubscriptions($authToken: String){
  myCommunicationSubscriptions(authToken: $authToken){
    firstName
    lastName
    language
    hasAcceptedCommunication
  }
}
"""
