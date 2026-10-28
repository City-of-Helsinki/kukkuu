<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Tags](#tags)
  - [Models](#models)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Tags

The `tags` app provides translatable tags that can be attached to models. `Tag` is an abstract base model, and each
kind of tag is a concrete model deriving from it with its own table.

## Models

- `Tag`: The abstract base model.
  - `slug`: The primary key, e.g. `rhythm`. Should remain stable after creating.
  - `sort_order`: Optional. Tags without a sort order are listed last. The default ordering is `sort_order`, `slug`.
- `ThemePath`: A tag used for classifying events, e.g. "rhythm" or "story".
  - Translated `name` and `description` to Finnish, Swedish and English.
  - Linked to events through the `EventThemePath` model of the `events` app. A theme path that is used by an event
    cannot be deleted.
