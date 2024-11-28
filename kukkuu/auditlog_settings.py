# Register all models by default
AUDITLOG_INCLUDE_ALL_MODELS = True

# Exclude the IP address from logging.
# When using “AuditlogMiddleware”, the IP address is logged by default
AUDITLOG_DISABLE_REMOTE_ADDR = False

# Disables logging during raw save. (I.e. for instance using loaddata)
# M2M operations will still be logged, since they’re never considered raw.
AUDITLOG_DISABLE_ON_RAW_SAVE = True

# Exclude models in registration process.
# It will be considered when AUDITLOG_INCLUDE_ALL_MODELS is True.
AUDITLOG_EXCLUDE_TRACKING_MODELS = (
    "admin.logentry",  # excluded by default
    "auditlog.logentry",  # excluded by default
    "contenttypes.contenttype",
    "sessions.session",
    "helusers.oidcbackchannellogoutevent",
    "mailer.dontsendentry",
    "django_ilmoitin.notificationtemplatetranslation",
    "projects.projecttranslation",
    "events.eventtranslation",
    "events.eventgrouptranslation",
    "venues.venuetranslation",
    "languages.languagetranslation",
    "messaging.messagetranslation",
    "users.guardian_languages_spoken_at_home",
    "children.child_languages_spoken_at_home",
    "messaging.message_occurrences",
    "django_ilmoitin.notificationtemplate_admins_to_notify",
    "mailer.message",
    "mailer.messagelog",
    "languages.language",
)

# Configure models registration and other behaviours.
AUDITLOG_INCLUDE_TRACKING_MODELS = (
    "users.user_user_permissions",
    "users.user_groups",
    "users.user_ad_groups",
    "auth.group_permissions",
    "helusers.adgroup",
    "helusers.adgroupmapping",
    "auth.permission",
    "auth.group",
    "django_ilmoitin.notificationtemplate",
    "guardian.groupobjectpermission",
    "guardian.userobjectpermission",
    {
        "model": "users.user",
        "exclude_fields": [
            "last_login",
        ],
        "mask_fields": [
            "first_name",
            "last_name",
            "email",
        ],
        "serialize_data": True,
        "serialize_auditlog_fields_only": False,
    },
    {
        "model": "users.guardian",
        "mask_fields": ["first_name", "last_name", "email", "phone_number"],
        "serialize_data": True,
        "serialize_auditlog_fields_only": False,
    },
    {
        "model": "children.child",
        "mask_fields": [
            "name",
        ],
        "serialize_data": True,
        "serialize_auditlog_fields_only": False,
    },
    "children.relationship",
    "projects.project",
    "events.event",
    "events.occurrence",
    "events.enrolment",
    "events.eventgroup",
    "events.ticketsystempassword",
    "venues.venue",
    "subscriptions.freespotnotificationsubscription",
    "messaging.message",
    "reports.permission",
    "verification_tokens.verificationtoken",
)
