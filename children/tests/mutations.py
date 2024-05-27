SUBMIT_CHILDREN_AND_GUARDIAN_MUTATION = """
mutation SubmitChildrenAndGuardian($input: SubmitChildrenAndGuardianMutationInput!) {
  submitChildrenAndGuardian(input: $input) {
    children {
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
    guardian {
      firstName
      lastName
      phoneNumber
      email
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

ADD_CHILD_MUTATION = """
mutation AddChild($input: AddChildMutationInput!) {
  addChild(input: $input) {
    child {
      name
      birthyear
      postalCode
    }
  }
}
"""


UPDATE_CHILD_MUTATION = """
mutation UpdateChild($input: UpdateChildMutationInput!) {
  updateChild(input: $input) {
    child {
      name
      birthyear
      postalCode
    }
  }
}
"""

DELETE_CHILD_MUTATION = """
mutation DeleteChild($input: DeleteChildMutationInput!) {
  deleteChild(input: $input) {__typename}
}
"""

UPDATE_CHILD_NOTES_MUTATION_TEMPLATE = """
mutation UpdateChildNotes($input: UpdateChildNotesMutationInput!) {
  updateChildNotes(input: $input) {
    childNotes {
      childId
      notes
      %(extra_field_name)s
    }
  }
}
"""

UPDATE_CHILD_NOTES_MUTATION = UPDATE_CHILD_NOTES_MUTATION_TEMPLATE % {
    "extra_field_name": ""
}
