# Register all models by default
AUDITLOG_INCLUDE_ALL_MODELS = True

# Exclude the IP address from logging?
# When using AuditlogMiddleware, the IP address is logged by default
AUDITLOG_DISABLE_REMOTE_ADDR = False

# Disables logging during raw save. (I.e. for instance using loaddata)
# M2M operations will still be logged, since they’re never considered raw.
AUDITLOG_DISABLE_ON_RAW_SAVE = True

# Exclude models in registration process.
# This setting will only be considered when AUDITLOG_INCLUDE_ALL_MODELS is True.
AUDITLOG_EXCLUDE_TRACKING_MODELS = (
    "admin.logentry",  # excluded by default
    "auditlog.logentry",  # excluded by default
    "contenttypes.contenttype",  # system model
    "sessions.session",  # auth model
    "helusers.oidcbackchannellogoutevent",  # auth model
    "languages.language",  # system
    "mailer.dontsendentry",  # system
    "mailer.message",  # system
    "mailer.messagelog",  # system
    # social-auth-app-django models
    # https://github.com/python-social-auth/social-app-django/blob/master/social_django/models.py
    "social_django.association",  # auth model
    "social_django.code",  # auth model
    "social_django.nonce",  # auth model
    "social_django.partial",  # auth model
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
    "django_ilmoitin.notificationtemplate_admins_to_notify",
    "guardian.groupobjectpermission",
    "guardian.userobjectpermission",
    {
        # social-auth-app-django UserSocialAuth model, see
        # https://github.com/python-social-auth/social-app-django/blob/master/social_django/models.py
        "model": "social_django.usersocialauth",
        "serialize_data": True,
    },
    {
        "model": "users.user",
        "exclude_fields": [
            "last_login",  # don't write log of every request
        ],
        "serialize_data": True,
    },
    {
        "model": "users.guardian",
        "serialize_data": True,
    },
    {
        "model": "children.child",
        "serialize_data": True,
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
    # secondary
    "django_ilmoitin.notificationtemplatetranslation",
    "projects.projecttranslation",
    "events.eventtranslation",
    "events.eventgrouptranslation",
    "venues.venuetranslation",
    "languages.languagetranslation",
    "messaging.messagetranslation",
    "messaging.message_occurrences",
    "users.guardian_languages_spoken_at_home",
    "children.child_languages_spoken_at_home",
)
