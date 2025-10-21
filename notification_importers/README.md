<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Notification Importer](#notification-importer)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Notification Importer

The notification templates can be imported via

- a) Google sheet importer
- b) Template file importer

The importer can be used to create and update the notification templates or to check whether they are in sync.
The importer can be used via Django management commands (in notification_importers app) or admin site tools.

To enable admin site tools, some configuration is needed:

To enable a selected importer (`NotificationFileImporter` or `NotificationGoogleSheetImporter`)

```python
NOTIFICATIONS_IMPORTER = (
    "notification_importers.notification_importer.NotificationFileImporter"
)
```

If a Google sheet importer is used, also `NOTIFICATIONS_SHEET_ID` is needed

```python
NOTIFICATIONS_SHEET_ID = "1234"
```

If a File importer is used, files should be stored in notification_importers app in
notification_importers/templates/sms and notification_importers/templates/email folders.
There is also a naming convention used there. The file name must be given in this pattern
[notification_type]-[locale].[html|j2].
