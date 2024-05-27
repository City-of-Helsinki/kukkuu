# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_user_serialize 1"] = {
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
                {"key": "HAS_ACCEPTED_COMMUNICATION", "value": False},
                {
                    "children": [
                        {
                            "children": [
                                {"key": "NAME", "value": "Dalton Castaneda"},
                                {"key": "BIRTHYEAR", "value": 2019},
                                {"key": "POSTAL_CODE", "value": "30727"},
                                {"children": [], "key": "ENROLMENTS"},
                                {"children": [], "key": "TICKET_SYSTEM_PASSWORDS"},
                                {
                                    "children": [
                                        {
                                            "children": [
                                                {
                                                    "key": "CREATED_AT",
                                                    "value": "2020-11-11T12:00:00+00:00",
                                                },
                                                {
                                                    "key": "CHILD",
                                                    "value": "Dalton Castaneda (2019)",
                                                },
                                                {
                                                    "key": "OCCURRENCE",
                                                    "value": "2007-10-07 00:42:30+00:00 (589)",
                                                },
                                            ],
                                            "key": "FREESPOTNOTIFICATIONSUBSCRIPTION",
                                        }
                                    ],
                                    "key": "FREE_SPOT_NOTIFICATION_SUBSCRIPTIONS",
                                },
                                {
                                    "key": "NOTES",
                                    "value": """Longer test notes
with multiple lines.""",
                                },
                            ],
                            "key": "CHILD",
                        },
                        {
                            "children": [
                                {"key": "NAME", "value": "Jason Berg"},
                                {"key": "BIRTHYEAR", "value": 2019},
                                {"key": "POSTAL_CODE", "value": "01171"},
                                {
                                    "children": [
                                        {
                                            "children": [
                                                {
                                                    "key": "CHILD",
                                                    "value": "Jason Berg (2019)",
                                                },
                                                {
                                                    "children": [
                                                        {
                                                            "key": "TIME",
                                                            "value": "1978-01-13T09:04:50+00:00",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Rise item spend just imagine although dark.",
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
                                                                        "fi": "Medical price pick four moment body employee word.",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                                {
                                                                    "key": "ADDRESS_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": """49904 Roberts Island
Yorkview, OK 06572""",
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
                                        }
                                    ],
                                    "key": "ENROLMENTS",
                                },
                                {
                                    "children": [
                                        {
                                            "children": [
                                                {"key": "ASSIGNED_AT", "value": None},
                                                {"key": "VALUE", "value": "$5Y3Eytpg5"},
                                                {
                                                    "children": [
                                                        {
                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                            "value": {
                                                                "en": "",
                                                                "fi": "Thus need air shoulder it husband. More religious section.",
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
                                                    "value": "Jason Berg (2019)",
                                                },
                                            ],
                                            "key": "TICKETSYSTEMPASSWORD",
                                        }
                                    ],
                                    "key": "TICKET_SYSTEM_PASSWORDS",
                                },
                                {
                                    "children": [
                                        {
                                            "children": [
                                                {
                                                    "key": "CREATED_AT",
                                                    "value": "2020-11-11T12:00:00+00:00",
                                                },
                                                {
                                                    "key": "CHILD",
                                                    "value": "Jason Berg (2019)",
                                                },
                                                {
                                                    "key": "OCCURRENCE",
                                                    "value": "1974-05-30 15:30:48+00:00 (590)",
                                                },
                                            ],
                                            "key": "FREESPOTNOTIFICATIONSUBSCRIPTION",
                                        }
                                    ],
                                    "key": "FREE_SPOT_NOTIFICATION_SUBSCRIPTIONS",
                                },
                                {"key": "NOTES", "value": "Alternative test notes"},
                            ],
                            "key": "CHILD",
                        },
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
                                                            "value": "1977-12-17T06:50:34+00:00",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Political maintain there drive threat Mr.",
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
                                                                        "fi": "Option from change.",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                                {
                                                                    "key": "ADDRESS_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": """35141 Cruz Spring
Bellhaven, ME 48709""",
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
                                                            "value": "1997-06-16T18:04:26+00:00",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Out treat tell these dinner. Walk choice reality nothing.",
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
                                                                        "fi": "Maintain reveal strong develop two send.",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                                {
                                                                    "key": "ADDRESS_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": """494 Sanders Estates Suite 075
Jamestown, MT 39374""",
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
                                                {"key": "VALUE", "value": "G*Md1Co(!i"},
                                                {
                                                    "children": [
                                                        {
                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                            "value": {
                                                                "en": "",
                                                                "fi": "Ahead center town least style above. And others along hotel.",
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
                                                {"key": "VALUE", "value": "+9eHg7Fy!d"},
                                                {
                                                    "children": [
                                                        {
                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                            "value": {
                                                                "en": "",
                                                                "fi": "Determine girl the white statement authority.",
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
                                                {"key": "VALUE", "value": "(AKx8MvU7s"},
                                                {
                                                    "children": [
                                                        {
                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                            "value": {
                                                                "en": "",
                                                                "fi": "Right financial cut director organization nothing rest.",
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
                                                {"key": "VALUE", "value": "^P+f743d6x"},
                                                {
                                                    "children": [
                                                        {
                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                            "value": {
                                                                "en": "",
                                                                "fi": "Meeting woman or walk.",
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
                                                {"key": "VALUE", "value": "pU4KdAkN3)"},
                                                {
                                                    "children": [
                                                        {
                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                            "value": {
                                                                "en": "",
                                                                "fi": "Right science chair door suddenly paper. Drop street than.",
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
                                {"key": "NOTES", "value": ""},
                            ],
                            "key": "CHILD",
                        },
                    ],
                    "key": "CHILDREN",
                },
            ],
            "key": "GUARDIAN",
        },
    ],
    "key": "USER",
}
