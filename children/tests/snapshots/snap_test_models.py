# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_child_serialize 1"] = {
    "children": [
        {"key": "UUID", "value": "fa354000-3c0c-11eb-86c5-acde48001122"},
        {"key": "USERNAME", "value": "jeffersonkimberly"},
        {"key": "FIRST_NAME", "value": "Alexis"},
        {"key": "LAST_NAME", "value": "Black"},
        {"key": "EMAIL", "value": "michellewalker@example.net"},
        {
            "key": "ADMINISTERED_PROJECTS",
            "value": [
                {
                    "children": [
                        {"key": "YEAR", "value": 2020},
                        {
                            "key": "NAME_WITH_TRANSLATIONS",
                            "value": {"en": "", "fi": "Testiprojekti", "sv": ""},
                        },
                    ],
                    "key": "PROJECT",
                }
            ],
        },
        {"key": "LAST_LOGIN", "value": None},
        {"key": "DATE_JOINED", "value": "2020-11-11T12:00:00+00:00"},
        {
            "children": [
                {"key": "ID", "value": "8dff3da4-a329-4b81-971a-bc509df679b1"},
                {"key": "USER", "value": "Black Alexis (michellewalker@example.net)"},
                {"key": "FIRST_NAME", "value": "Michael"},
                {"key": "LAST_NAME", "value": "Patton"},
                {"key": "EMAIL", "value": "michellewalker@example.net"},
                {"key": "PHONE_NUMBER", "value": "355.777.6712x406"},
                {"key": "HAS_ACCEPTED_MARKETING", "value": False},
                {
                    "children": [
                        {
                            "children": [
                                {"key": "NAME", "value": "Katherine Gomez"},
                                {"key": "BIRTHYEAR", "value": 2023},
                                {"key": "POSTAL_CODE", "value": "49763"},
                                {
                                    "children": [
                                        {
                                            "children": [
                                                {
                                                    "key": "CHILD",
                                                    "value": "Katherine Gomez (2023)",
                                                },
                                                {
                                                    "children": [
                                                        {
                                                            "key": "TIME",
                                                            "value": "1986-01-08T08:26:19+00:00",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Hospital number lose least then. Beyond than trial western.",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                                {
                                                                    "key": "EVENT_GROUP",
                                                                    "value": None,
                                                                },
                                                                {
                                                                    "children": [
                                                                        {
                                                                            "key": "YEAR",
                                                                            "value": 2020,
                                                                        },
                                                                        {
                                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                                            "value": {
                                                                                "en": "",
                                                                                "fi": "Testiprojekti",
                                                                                "sv": "",
                                                                            },
                                                                        },
                                                                    ],
                                                                    "key": "PROJECT",
                                                                },
                                                                {
                                                                    "key": "TICKET_SYSTEM",
                                                                    "value": "internal",
                                                                },
                                                            ],
                                                            "key": "EVENT",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Clearly middle moment strong hand.",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                                {
                                                                    "key": "ADDRESS_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": """779 Kevin Isle Suite 550
Jonathanburgh, AZ 30120""",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                            ],
                                                            "key": "VENUE",
                                                        },
                                                    ],
                                                    "key": "OCCURRENCE",
                                                },
                                            ],
                                            "key": "ENROLMENT",
                                        },
                                        {
                                            "children": [
                                                {
                                                    "key": "CHILD",
                                                    "value": "Katherine Gomez (2023)",
                                                },
                                                {
                                                    "children": [
                                                        {
                                                            "key": "TIME",
                                                            "value": "1974-05-30T15:30:48+00:00",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Include and individual effort indeed discuss challenge school.",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                                {
                                                                    "key": "EVENT_GROUP",
                                                                    "value": None,
                                                                },
                                                                {
                                                                    "children": [
                                                                        {
                                                                            "key": "YEAR",
                                                                            "value": 2020,
                                                                        },
                                                                        {
                                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                                            "value": {
                                                                                "en": "",
                                                                                "fi": "Testiprojekti",
                                                                                "sv": "",
                                                                            },
                                                                        },
                                                                    ],
                                                                    "key": "PROJECT",
                                                                },
                                                                {
                                                                    "key": "TICKET_SYSTEM",
                                                                    "value": "internal",
                                                                },
                                                            ],
                                                            "key": "EVENT",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Teach manager movie owner.",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                                {
                                                                    "key": "ADDRESS_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": """40241 Alexander Fields
West Rubenbury, MS 61495""",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                            ],
                                                            "key": "VENUE",
                                                        },
                                                    ],
                                                    "key": "OCCURRENCE",
                                                },
                                            ],
                                            "key": "ENROLMENT",
                                        },
                                        {
                                            "children": [
                                                {
                                                    "key": "CHILD",
                                                    "value": "Katherine Gomez (2023)",
                                                },
                                                {
                                                    "children": [
                                                        {
                                                            "key": "TIME",
                                                            "value": "2011-01-05T08:35:11+00:00",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Enjoy when one wonder fund nor white.",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                                {
                                                                    "key": "EVENT_GROUP",
                                                                    "value": None,
                                                                },
                                                                {
                                                                    "children": [
                                                                        {
                                                                            "key": "YEAR",
                                                                            "value": 2020,
                                                                        },
                                                                        {
                                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                                            "value": {
                                                                                "en": "",
                                                                                "fi": "Testiprojekti",
                                                                                "sv": "",
                                                                            },
                                                                        },
                                                                    ],
                                                                    "key": "PROJECT",
                                                                },
                                                                {
                                                                    "key": "TICKET_SYSTEM",
                                                                    "value": "internal",
                                                                },
                                                            ],
                                                            "key": "EVENT",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Available policy physical heavy scientist.",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                                {
                                                                    "key": "ADDRESS_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": """37849 Alejandra Rapid Apt. 294
South Mitchell, NC 30891""",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                            ],
                                                            "key": "VENUE",
                                                        },
                                                    ],
                                                    "key": "OCCURRENCE",
                                                },
                                            ],
                                            "key": "ENROLMENT",
                                        },
                                        {
                                            "children": [
                                                {
                                                    "key": "CHILD",
                                                    "value": "Katherine Gomez (2023)",
                                                },
                                                {
                                                    "children": [
                                                        {
                                                            "key": "TIME",
                                                            "value": "1972-02-01T22:06:34+00:00",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Affect money school military statement.",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                                {
                                                                    "key": "EVENT_GROUP",
                                                                    "value": None,
                                                                },
                                                                {
                                                                    "children": [
                                                                        {
                                                                            "key": "YEAR",
                                                                            "value": 2020,
                                                                        },
                                                                        {
                                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                                            "value": {
                                                                                "en": "",
                                                                                "fi": "Testiprojekti",
                                                                                "sv": "",
                                                                            },
                                                                        },
                                                                    ],
                                                                    "key": "PROJECT",
                                                                },
                                                                {
                                                                    "key": "TICKET_SYSTEM",
                                                                    "value": "internal",
                                                                },
                                                            ],
                                                            "key": "EVENT",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Because treatment sense left.",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                                {
                                                                    "key": "ADDRESS_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": """812 Russell Hollow Suite 792
Jessicatown, MN 66988""",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                            ],
                                                            "key": "VENUE",
                                                        },
                                                    ],
                                                    "key": "OCCURRENCE",
                                                },
                                            ],
                                            "key": "ENROLMENT",
                                        },
                                        {
                                            "children": [
                                                {
                                                    "key": "CHILD",
                                                    "value": "Katherine Gomez (2023)",
                                                },
                                                {
                                                    "children": [
                                                        {
                                                            "key": "TIME",
                                                            "value": "2014-12-23T16:25:42+00:00",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Wife message focus between.",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                                {
                                                                    "key": "EVENT_GROUP",
                                                                    "value": None,
                                                                },
                                                                {
                                                                    "children": [
                                                                        {
                                                                            "key": "YEAR",
                                                                            "value": 2020,
                                                                        },
                                                                        {
                                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                                            "value": {
                                                                                "en": "",
                                                                                "fi": "Testiprojekti",
                                                                                "sv": "",
                                                                            },
                                                                        },
                                                                    ],
                                                                    "key": "PROJECT",
                                                                },
                                                                {
                                                                    "key": "TICKET_SYSTEM",
                                                                    "value": "internal",
                                                                },
                                                            ],
                                                            "key": "EVENT",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Offer goal unit country call thus. By final design degree.",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                                {
                                                                    "key": "ADDRESS_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": """04194 Frederick Mill
Daniellechester, KS 04855""",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                            ],
                                                            "key": "VENUE",
                                                        },
                                                    ],
                                                    "key": "OCCURRENCE",
                                                },
                                            ],
                                            "key": "ENROLMENT",
                                        },
                                    ],
                                    "key": "ENROLMENTS",
                                },
                                {
                                    "children": [
                                        {
                                            "children": [
                                                {"key": "ASSIGNED_AT", "value": None},
                                                {"key": "VALUE", "value": "F@47o(Up&6"},
                                                {
                                                    "children": [
                                                        {
                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                            "value": {
                                                                "en": "",
                                                                "fi": "Court cultural speak condition her station must.",
                                                                "sv": "",
                                                            },
                                                        },
                                                        {
                                                            "key": "EVENT_GROUP",
                                                            "value": None,
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "YEAR",
                                                                    "value": 2020,
                                                                },
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Testiprojekti",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                            ],
                                                            "key": "PROJECT",
                                                        },
                                                        {
                                                            "key": "TICKET_SYSTEM",
                                                            "value": "internal",
                                                        },
                                                    ],
                                                    "key": "EVENT",
                                                },
                                                {
                                                    "key": "CHILD",
                                                    "value": "Katherine Gomez (2023)",
                                                },
                                            ],
                                            "key": "TICKETSYSTEMPASSWORD",
                                        },
                                        {
                                            "children": [
                                                {"key": "ASSIGNED_AT", "value": None},
                                                {"key": "VALUE", "value": "$jNvGUhi+8"},
                                                {
                                                    "children": [
                                                        {
                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                            "value": {
                                                                "en": "",
                                                                "fi": "I time bring third person. Resource certainly past pull.",
                                                                "sv": "",
                                                            },
                                                        },
                                                        {
                                                            "key": "EVENT_GROUP",
                                                            "value": None,
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "YEAR",
                                                                    "value": 2020,
                                                                },
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Testiprojekti",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                            ],
                                                            "key": "PROJECT",
                                                        },
                                                        {
                                                            "key": "TICKET_SYSTEM",
                                                            "value": "internal",
                                                        },
                                                    ],
                                                    "key": "EVENT",
                                                },
                                                {
                                                    "key": "CHILD",
                                                    "value": "Katherine Gomez (2023)",
                                                },
                                            ],
                                            "key": "TICKETSYSTEMPASSWORD",
                                        },
                                        {
                                            "children": [
                                                {"key": "ASSIGNED_AT", "value": None},
                                                {"key": "VALUE", "value": "0GX@55Bp(6"},
                                                {
                                                    "children": [
                                                        {
                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                            "value": {
                                                                "en": "",
                                                                "fi": "Bed add should computer. Degree share across.",
                                                                "sv": "",
                                                            },
                                                        },
                                                        {
                                                            "key": "EVENT_GROUP",
                                                            "value": None,
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "YEAR",
                                                                    "value": 2020,
                                                                },
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Testiprojekti",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                            ],
                                                            "key": "PROJECT",
                                                        },
                                                        {
                                                            "key": "TICKET_SYSTEM",
                                                            "value": "internal",
                                                        },
                                                    ],
                                                    "key": "EVENT",
                                                },
                                                {
                                                    "key": "CHILD",
                                                    "value": "Katherine Gomez (2023)",
                                                },
                                            ],
                                            "key": "TICKETSYSTEMPASSWORD",
                                        },
                                        {
                                            "children": [
                                                {"key": "ASSIGNED_AT", "value": None},
                                                {"key": "VALUE", "value": "PP$15MkwcE"},
                                                {
                                                    "children": [
                                                        {
                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                            "value": {
                                                                "en": "",
                                                                "fi": "Yeah question he risk military result building.",
                                                                "sv": "",
                                                            },
                                                        },
                                                        {
                                                            "key": "EVENT_GROUP",
                                                            "value": None,
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "YEAR",
                                                                    "value": 2020,
                                                                },
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Testiprojekti",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                            ],
                                                            "key": "PROJECT",
                                                        },
                                                        {
                                                            "key": "TICKET_SYSTEM",
                                                            "value": "internal",
                                                        },
                                                    ],
                                                    "key": "EVENT",
                                                },
                                                {
                                                    "key": "CHILD",
                                                    "value": "Katherine Gomez (2023)",
                                                },
                                            ],
                                            "key": "TICKETSYSTEMPASSWORD",
                                        },
                                        {
                                            "children": [
                                                {"key": "ASSIGNED_AT", "value": None},
                                                {"key": "VALUE", "value": "^4aK6a^8D8"},
                                                {
                                                    "children": [
                                                        {
                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                            "value": {
                                                                "en": "",
                                                                "fi": "Support apply mind arrive wish.",
                                                                "sv": "",
                                                            },
                                                        },
                                                        {
                                                            "key": "EVENT_GROUP",
                                                            "value": None,
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "YEAR",
                                                                    "value": 2020,
                                                                },
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Testiprojekti",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                            ],
                                                            "key": "PROJECT",
                                                        },
                                                        {
                                                            "key": "TICKET_SYSTEM",
                                                            "value": "internal",
                                                        },
                                                    ],
                                                    "key": "EVENT",
                                                },
                                                {
                                                    "key": "CHILD",
                                                    "value": "Katherine Gomez (2023)",
                                                },
                                            ],
                                            "key": "TICKETSYSTEMPASSWORD",
                                        },
                                    ],
                                    "key": "TICKET_SYSTEM_PASSWORDS",
                                },
                                {
                                    "children": [],
                                    "key": "FREE_SPOT_NOTIFICATION_SUBSCRIPTIONS",
                                },
                            ],
                            "key": "CHILD",
                        }
                    ],
                    "key": "CHILDREN",
                },
            ],
            "key": "GUARDIAN",
        },
    ],
    "key": "USER",
}
