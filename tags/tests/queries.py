THEME_PATHS_QUERY = """
query ThemePaths {
  themePaths {
    edges {
      node {
        slug
        name
        description
        sortOrder
        translations {
          languageCode
          name
          description
        }
      }
    }
  }
}
"""

THEME_PATH_QUERY = """
query ThemePath($id: ID!) {
  themePath(id: $id) {
    slug
    name
    description
    sortOrder
    translations {
      languageCode
      name
      description
    }
  }
}
"""

ACCESSIBILITIES_QUERY = """
query Accessibilities {
  accessibilities {
    edges {
      node {
        slug
        name
        description
        sortOrder
        translations {
          languageCode
          name
          description
        }
      }
    }
  }
}
"""

ACCESSIBILITY_QUERY = """
query Accessibility($id: ID!) {
  accessibility(id: $id) {
    slug
    name
    description
    sortOrder
    translations {
      languageCode
      name
      description
    }
  }
}
"""
