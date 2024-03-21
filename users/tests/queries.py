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
          }
        }
      }
    }
  }
}
"""

MY_MARKETING_SUBSCRIPTIONS_QUERY = """
query MyMarketingSubscriptions($authToken: String){
  myMarketingSubscriptions(authToken: $authToken){
    firstName
    lastName
    language
    hasAcceptedMarketing
  }
}
"""
