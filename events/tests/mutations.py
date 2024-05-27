ADD_EVENT_MUTATION = """
mutation AddEvent($input: AddEventMutationInput!) {
  addEvent(input: $input) {
    event {
      translations{
        languageCode
        name
        description
        imageAltText
        shortDescription
      }
      project{
        year
      }
      duration
      image
      imageAltText
      participantsPerInvite
      capacityPerOccurrence
      publishedAt
      readyForEventGroupPublishing
      ticketSystem {
        type
      }
    }
  }
}
"""

ADD_TICKETMASTER_EVENT_MUTATION = """
mutation AddTicketmasterEvent($input: AddEventMutationInput!) {
  addEvent(input: $input) {
    event {
      ticketSystem {
        type
      }
    }
  }
}
"""

UPDATE_EVENT_MUTATION = """
mutation UpdateEvent($input: UpdateEventMutationInput!) {
  updateEvent(input: $input) {
    event {
      translations{
        name
        shortDescription
        description
        imageAltText
        languageCode
      }
      image
      imageAltText
      participantsPerInvite
      capacityPerOccurrence
      duration
      ticketSystem {
        type
      }
      occurrences{
        edges{
          node{
            time
          }
        }
      }
      readyForEventGroupPublishing
    }
  }
}
"""

UPDATE_TICKETMASTER_EVENT_MUTATION = """
mutation UpdateTicketmasterEvent($input: UpdateEventMutationInput!) {
  updateEvent(input: $input) {
    event {
      ticketSystem {
        type
      }
    }
  }
}
"""

PUBLISH_EVENT_MUTATION = """
mutation PublishEvent($input: PublishEventMutationInput!) {
  publishEvent(input: $input) {
    event {
      publishedAt
    }
  }
}
"""

DELETE_EVENT_MUTATION = """
mutation DeleteEvent($input: DeleteEventMutationInput!) {
  deleteEvent(input: $input) {
    __typename
  }
}
"""

ADD_OCCURRENCE_MUTATION = """
mutation AddOccurrence($input: AddOccurrenceMutationInput!) {
  addOccurrence(input: $input) {
    occurrence{
      event{
        createdAt
      }
      venue {
        createdAt
      }
      time
      occurrenceLanguage
      capacity
      capacityOverride
      ticketSystem {
        type
        ... on TicketmasterOccurrenceTicketSystem {
          url
        }
      }
    }
  }
}

"""

UPDATE_OCCURRENCE_MUTATION = """
mutation UpdateOccurrence($input: UpdateOccurrenceMutationInput!) {
  updateOccurrence(input: $input) {
    occurrence{
      event{
        createdAt
      }
      venue {
        createdAt
      }
      time
      occurrenceLanguage
      enrolmentCount
      remainingCapacity
      capacity
      capacityOverride
      ticketSystem {
        type
        ... on TicketmasterOccurrenceTicketSystem {
          url
        }
      }
    }
  }
}

"""

DELETE_OCCURRENCE_MUTATION = """
mutation DeleteOccurrence($input: DeleteOccurrenceMutationInput!) {
  deleteOccurrence(input: $input) {
    __typename
  }
}

"""

ENROL_OCCURRENCE_MUTATION = """
mutation EnrolOccurrence($input: EnrolOccurrenceMutationInput!) {
  enrolOccurrence(input: $input) {
    enrolment{
      child{
        name
      }
      occurrence {
        time
      }
      createdAt
    }
  }
}

"""


UNENROL_OCCURRENCE_MUTATION = """
mutation UnenrolOccurrence($input: UnenrolOccurrenceMutationInput!) {
  unenrolOccurrence(input: $input) {
    occurrence{
        time
    }
    child{
        name
    }
  }
}

"""

SET_ENROLMENT_ATTENDANCE_MUTATION = """
mutation SetEnrolmentAttendance($input: SetEnrolmentAttendanceMutationInput!) {
  setEnrolmentAttendance(input: $input) {
    enrolment {
      attended
    }
  }
}

"""

ADD_EVENT_GROUP_MUTATION = """
mutation AddEventGroup($input: AddEventGroupMutationInput!) {
  addEventGroup(input: $input) {
    eventGroup {
      translations{
        languageCode
        name
        description
        imageAltText
        shortDescription
      }
      project{
        year
      }
      image
      imageAltText
      publishedAt
    }
  }
}
"""

UPDATE_EVENT_GROUP_MUTATION = """
mutation UpdateEventGroup($input: UpdateEventGroupMutationInput!) {
  updateEventGroup(input: $input) {
    eventGroup {
      translations{
        name
        shortDescription
        description
        imageAltText
        languageCode
      }
      image
    }
  }
}
"""

DELETE_EVENT_GROUP_MUTATION = """
mutation DeleteEventGroup($input: DeleteEventGroupMutationInput!) {
  deleteEventGroup(input: $input) {
    __typename
  }
}
"""


PUBLISH_EVENT_GROUP_MUTATION = """
mutation PublishEventGroup($input: PublishEventGroupMutationInput!) {
  publishEventGroup(input: $input) {
    eventGroup {
      publishedAt
      events {
        edges {
          node {
            publishedAt
          }
        }
      }
    }
  }
}
"""


IMPORT_TICKET_SYSTEM_PASSWORDS_MUTATION = """
mutation ImportTicketSystemPasswordsMutation(
    $input: ImportTicketSystemPasswordsMutationInput!
) {
  importTicketSystemPasswords(input: $input) {
    event {
      name
    }
    passwords
    errors {
        field
        message
        value
    }
  }
}
"""


ASSIGN_TICKET_SYSTEM_PASSWORD_MUTATION = """
mutation AssignTicketSystemPassword($input: AssignTicketSystemPasswordMutationInput!) {
  assignTicketSystemPassword(input: $input) {
    event {
      name
    }
    child {
      name
    }
    password
  }
}
"""
