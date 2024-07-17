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
                {"key": "PHONE_NUMBER", "value": "235.857.7767x124"},
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
                                                    "value": "1998-03-24 07:42:39.814032+00:00 (101)",
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
                                                            "value": "2014-12-15T00:10:52.106068+00:00",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Significant road including everybody star.",
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
                                                                        "fi": "Size hard pressure moment. Cover majority from song entire.",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                                {
                                                                    "key": "ADDRESS_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": """7259 Melissa Loaf Apt. 359
Lake Kelly, NM 09613""",
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
                                                {"key": "VALUE", "value": "$kutEeNy44"},
                                                {
                                                    "children": [
                                                        {
                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                            "value": {
                                                                "en": "",
                                                                "fi": "Son doctor worry partner add.",
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
                                                    "value": "2006-08-11 23:28:41.941918+00:00 (102)",
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
                                                            "value": "2013-05-30T10:43:54.142655+00:00",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Management then some threat behavior see quite tax.",
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
South Mitchell, NC 69042""",
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
                                                            "value": "2020-03-29T03:04:22.011516+00:00",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Federal minute paper third item future far power.",
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
                                                                        "fi": "Service the politics money pressure. Across life author phone.",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                                {
                                                                    "key": "ADDRESS_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": """662 Charles Orchard
Staceyville, PW 70051""",
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
                                                            "value": "2003-08-14T13:03:41.171262+00:00",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Message focus between picture under room.",
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
Daniellechester, VI 33985""",
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
                                                            "value": "1975-12-13T23:27:49.073366+00:00",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Her set detail else surface break rate.",
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
Bellhaven, NM 41103""",
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
                                                            "value": "1981-05-27T16:10:16.773219+00:00",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Whether page character.",
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
                                                                        "fi": "Whom inside appear research.",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                                {
                                                                    "key": "ADDRESS_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": """571 Palmer Islands
Andrewburgh, RI 12639""",
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
                                                {"key": "VALUE", "value": "!8GNa_b4ed"},
                                                {
                                                    "children": [
                                                        {
                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                            "value": {
                                                                "en": "",
                                                                "fi": "Simply bed which you area body attention leg.",
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
                                                {"key": "VALUE", "value": "q!b9NM_p_p"},
                                                {
                                                    "children": [
                                                        {
                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                            "value": {
                                                                "en": "",
                                                                "fi": "Different unit pass show international remain sing.",
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
                                                {"key": "VALUE", "value": "@@hObp%(8a"},
                                                {
                                                    "children": [
                                                        {
                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                            "value": {
                                                                "en": "",
                                                                "fi": "Wife natural somebody student measure.",
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
                                                {"key": "VALUE", "value": "Z3*d8fFmv0"},
                                                {
                                                    "children": [
                                                        {
                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                            "value": {
                                                                "en": "",
                                                                "fi": "Doctor stuff discover. Listen focus by bed.",
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
                                                {"key": "VALUE", "value": ")#$43I2s^Q"},
                                                {
                                                    "children": [
                                                        {
                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                            "value": {
                                                                "en": "",
                                                                "fi": "Note say act friend data religious special.",
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
