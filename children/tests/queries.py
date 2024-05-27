CHILDREN_QUERY = """
query Children {
  children {
    edges {
      node {
        name
        birthyear
        postalCode
        relationships {
          edges {
            node {
              type
              guardian {
                firstName
                lastName
                phoneNumber
                email
              }
            }
          }
        }
      }
    }
  }
}
"""


CHILDREN_FILTER_QUERY = """
query Children($projectId: ID!) {
  children(projectId: $projectId) {
    edges {
      node {
        name
      }
    }
  }
}
"""


CHILD_QUERY = """
query Child($id: ID!) {
  child(id: $id) {
    name
    birthyear
    postalCode
    relationships {
      edges {
        node {
          type
          guardian {
            firstName
            lastName
            phoneNumber
            email
          }
        }
      }
    }
  }
}
"""

CHILD_EVENTS_QUERY = """
query Child($id: ID!) {
  child(id: $id) {
    availableEvents{
      edges{
        node{
          createdAt
          occurrences{
            edges{
              node{
                remainingCapacity
              }
            }
          }
        }
      }
    }
    pastEvents{
      edges{
        node{
          createdAt
          name
          occurrences{
            edges{
              node{
                remainingCapacity
              }
            }
          }
        }
      }
    }
    occurrences {
      edges {
        node {
          time
        }
      }
    }
  }
}
"""

CHILD_NOTES_QUERY_TEMPLATE = """
query ChildNotes($id: ID!) {
  childNotes(id: $id) {
    childId
    notes
    %(extra_field_name)s
  }
}
"""

CHILD_NOTES_QUERY = CHILD_NOTES_QUERY_TEMPLATE % {"extra_field_name": ""}

CHILD_NOTES_QUERY_WITHOUT_ID_PARAMETER = """
query ChildNotes {
  childNotes {
    childId
    notes
  }
}
"""

CHILD_ENROLMENT_COUNT_QUERY = """
query Child($id: ID!, $year: Int) {
  child(id: $id) {
    enrolmentCount(year: $year)
    pastEnrolmentCount
  }
}
"""


CHILD_PAST_EVENTS_QUERY = """
query Child($id: ID!) {
  child(id: $id) {
    pastEvents {
      edges {
        node {
          name
        }
      }
    }
  }
}
"""

CHILDREN_PAGINATION_QUERY = """
query Children($projectId: ID!, $limit: Int, $offset: Int, $after: String, $first: Int) {
  children(projectId: $projectId, limit: $limit, offset: $offset, after: $after, first: $first) {
    edges {
      node {
        name
      }
    }
  }
}
"""  # noqa: E501

CHILD_AVAILABLE_EVENTS_AND_EVENT_GROUPS_QUERY = """
query Child($id: ID!) {
  child(id: $id) {
    availableEventsAndEventGroups{
      edges {
        node {
          ... on EventNode {
            name
            __typename
          }
          ... on EventGroupNode {
            name
            __typename
          }
        }
      }
    }
  }
}
"""

CHILD_UPCOMING_EVENTS_AND_EVENT_GROUPS_QUERY = """
query Child($id: ID!) {
  child(id: $id) {
    upcomingEventsAndEventGroups{
      edges {
        node {
          ... on EventNode {
            name
            canChildEnroll(childId: $id)
            __typename
          }
          ... on EventGroupNode {
            name
            canChildEnroll(childId: $id)
            __typename
          }
        }
      }
    }
  }
}
"""

CHILD_ACTIVE_INTERNAL_AND_TICKETMASTER_ENROLMENTS_QUERY = """
query Child($id: ID!) {
  child(id: $id) {
    activeInternalAndTicketSystemEnrolments{
      edges {
        node {
          ... on EnrolmentNode {
            occurrence {
              event {
                name
              }
            }
            __typename
          }
          ... on TicketmasterEnrolmentNode {
            createdAt
            event {
              name
            }
            __typename
          }
        }
      }
    }
  }
}
"""
