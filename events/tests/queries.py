EVENTS_QUERY = """
query Events {
  events {
    edges {
      node {
        translations{
          name
          description
          shortDescription
          imageAltText
          languageCode
        }
        project{
          year
        }
        name
        description
        shortDescription
        duration
        image
        imageAltText
        participantsPerInvite
        capacityPerOccurrence
        publishedAt
        createdAt
        updatedAt
        ticketSystem {
          type
        }
        occurrences {
          edges {
            node {
              remainingCapacity
              enrolmentCount
              time
              venue {
                translations{
                  name
                  description
                  languageCode
                }
              }
              ticketSystem {
                type
                ... on TicketmasterOccurrenceTicketSystem {
                  url
                }
                ... on LippupisteOccurrenceTicketSystem {
                  url
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

EVENT_QUERY = """
query Event($id: ID!) {
  event(id: $id) {
    translations{
      name
      shortDescription
      description
      imageAltText
      languageCode
    }
    project{
      year
    }
    name
    description
    shortDescription
    image
    imageAltText
    participantsPerInvite
    capacityPerOccurrence
    publishedAt
    createdAt
    updatedAt
    duration
    ticketSystem {
      type
    }
    occurrences{
      edges{
        node{
          time
          remainingCapacity
          enrolmentCount
          venue{
            translations{
              name
              description
              languageCode
            }
          }
          ticketSystem {
            type
            ... on TicketmasterOccurrenceTicketSystem {
              url
            }
            ... on LippupisteOccurrenceTicketSystem {
              url
            }
          }
        }
      }
    }
  }
}
"""

EVENTS_FILTER_QUERY = """
query Events($projectId: ID, $upcoming: Boolean) {
  events(projectId: $projectId, upcoming: $upcoming) {
    edges {
      node {
        name
      }
    }
  }
}
"""

OCCURRENCES_QUERY = """
query Occurrences {
  occurrences {
    edges {
      node {
        time
        remainingCapacity
        enrolmentCount
        event {
          translations {
            name
            shortDescription
            description
            languageCode
          }
          image
          participantsPerInvite
          capacityPerOccurrence
          publishedAt
          duration
        }
        venue{
          translations{
            name
            description
            address
            accessibilityInfo
            arrivalInstructions
            additionalInfo
            wwwUrl
            languageCode
          }
        }
        ticketSystem {
          type
          ... on TicketmasterOccurrenceTicketSystem {
            url
          }
          ... on LippupisteOccurrenceTicketSystem {
            url
          }
        }
      }
    }
  }
}
"""

OCCURRENCES_FILTER_QUERY = """
query Occurrences($date: Date, $time: Time, $upcoming: Boolean, $venueId: String,
                  $eventId: String, $occurrenceLanguage: String, $projectId: String,
                  $upcomingWithLeeway: Boolean, $upcomingWithOngoing: Boolean) {
  occurrences(date: $date, time: $time, upcoming: $upcoming, venueId: $venueId,
              eventId: $eventId, occurrenceLanguage: $occurrenceLanguage,
              projectId: $projectId, upcomingWithLeeway: $upcomingWithLeeway,
              upcomingWithOngoing: $upcomingWithOngoing) {
    edges {
      node {
        time
      }
    }
  }
}
"""

OCCURRENCE_QUERY = """
query Occurrence($id: ID!) {
  occurrence(id: $id){
    enrolments{
        edges{
          node{
            child{
              name
            }
          }
        }
    }
    time
    remainingCapacity
    enrolmentCount
    occurrenceLanguage
    event {
      translations {
        name
        shortDescription
        description
        languageCode
      }
      image
      participantsPerInvite
      capacityPerOccurrence
      publishedAt
      duration
    }
    venue{
      translations{
        name
        description
        address
        accessibilityInfo
        arrivalInstructions
        additionalInfo
        wwwUrl
        languageCode
      }
    }
    ticketSystem {
      type
      ... on TicketmasterOccurrenceTicketSystem {
        url
      }
      ... on LippupisteOccurrenceTicketSystem {
        url
      }
    }
  }
}
"""

CAN_CHILD_ENROLL_EVENT_QUERY = """
query Event($id: ID!, $childId: ID!) {
  event(id: $id) {
    name
    canChildEnroll(childId: $childId)
  }
}
"""

OCCURRENCES_COUNTS_QUERY_TEMPLATE = """
query Occurrences {
  occurrences {
    edges {
      node {
        enrolmentCount
        %(occurrence_fields)s
      }
    }
  }
}
"""

EVENT_GROUP_QUERY = """
query EventGroup($id: ID!) {
  eventGroup(id: $id) {
    translations{
      name
      shortDescription
      description
      imageAltText
      languageCode
    }
    project {
      year
    }
    name
    description
    shortDescription
    image
    imageAltText
    publishedAt
    createdAt
    updatedAt
    events {
      edges {
        node {
          __typename
          name
        }
      }
    }
  }
}
"""

EVENTS_AND_EVENT_GROUPS_SIMPLE_QUERY = """
query EventsAndEventGroups($projectId: ID, $upcoming: Boolean) {
  eventsAndEventGroups(projectId: $projectId, upcoming: $upcoming) {
    edges {
      node {
        ... on EventNode {
          __typename
          name
        }
        ... on EventGroupNode {
          __typename
          name
        }
      }
    }
  }
}
"""

EVENT_GROUP_EVENTS_FILTER_QUERY = """
query EventGroup($id: ID!, $availableForChild: String) {
  eventGroup(id: $id) {
    events(availableForChild: $availableForChild) {
      edges {
        node {
          name
        }
      }
    }
  }
}
"""


OCCURRENCE_TICKET_SYSTEM_QUERY = """
query Occurrence($id: ID!) {
  occurrence(id: $id) {
    ticketSystem {
      type
      ... on TicketmasterOccurrenceTicketSystem {
        url
      }
    }
  }
}
"""


EVENT_TICKET_SYSTEM_PASSWORD_QUERY = """
query TicketSystemChildPassword($eventId: ID!, $childId: ID!) {
  event(id: $eventId) {
    ticketSystem {
      type
      ... on TicketmasterEventTicketSystem {
        childPassword(childId: $childId)
      }
    }
  }
}
"""


EVENT_TICKET_SYSTEM_PASSWORD_COUNTS_QUERY = """
query TicketSystemPasswordCounts($eventId: ID!) {
  event(id: $eventId) {
    ticketSystem {
      ... on TicketmasterEventTicketSystem {
        freePasswordCount
        usedPasswordCount
      }
    }
  }
}
"""


VERIFY_TICKET_QUERY = """
  query VerifyTicket($referenceId: String!){
    verifyTicket(referenceId:$referenceId){
      occurrenceTime
      eventName
      venueName
      validity
      attended
    }
  }
"""


GET_ENROLMENT_REFERENCE_ID_QUERY = """
  query getChildEnrolments($id: ID!) {
    child(id: $id){
      enrolments {
        edges {
          node {
            referenceId
          }
        }
      }
    }
  }
"""
