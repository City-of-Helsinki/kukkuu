# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_get_profile_data_from_gdpr_api 1"] = {
    "children": [
        {"key": "UUID", "value": "fa354000-3c0c-11eb-86c5-acde48001122"},
        {"key": "USERNAME", "value": "jeffersonkimberly"},
        {"key": "FIRST_NAME", "value": "Alexis"},
        {"key": "LAST_NAME", "value": "Black"},
        {"key": "EMAIL", "value": "michellewalker@example.net"},
        {"key": "ADMINISTERED_PROJECTS", "value": []},
        {"key": "LAST_LOGIN", "value": "2020-12-12T00:00:00+00:00"},
        {"key": "DATE_JOINED", "value": "2020-12-12T00:00:00+00:00"},
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
                                                            "value": "1981-12-29T15:28:25.080157+00:00",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Increase thank certainly again thought summer.",
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
Jonathanburgh, AK 06327""",
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
                                                            "value": "1973-04-20T19:20:51.908992+00:00",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Democratic focus significant kind various laugh.",
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
                                                                        "fi": "Medical check word style also. Question national throw three.",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                                {
                                                                    "key": "ADDRESS_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": """Unit 7738 Box 4455
DPO AE 93387""",
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
                                                            "value": "1983-12-14T10:41:44.139987+00:00",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Policy sport available.",
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
                                                                        "fi": "Person material alone throughout investment check increase.",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                                {
                                                                    "key": "ADDRESS_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": """18631 David Wells Apt. 018
South Mikeburgh, NH 37426""",
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
                                                            "value": "1989-06-15T22:58:14.498478+00:00",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Month score father middle brother station physical very.",
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
                                                                        "fi": "Moment apply president unit positive.",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                                {
                                                                    "key": "ADDRESS_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": """7921 Fischer Ranch
Port Timothy, MI 90086""",
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
                                                            "value": "1980-04-10T06:06:28.089342+00:00",
                                                        },
                                                        {
                                                            "children": [
                                                                {
                                                                    "key": "NAME_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": "Suggest claim PM they. South blue reach ask.",
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
                                                                        "fi": "Process who catch bad. Seven process determine call.",
                                                                        "sv": "",
                                                                    },
                                                                },
                                                                {
                                                                    "key": "ADDRESS_WITH_TRANSLATIONS",
                                                                    "value": {
                                                                        "en": "",
                                                                        "fi": """1235 Eric Route Suite 932
New Manuelshire, PR 28866""",
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
                                                {"key": "VALUE", "value": "jR1NWxHl(x"},
                                                {
                                                    "children": [
                                                        {
                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                            "value": {
                                                                "en": "",
                                                                "fi": "Half state four hear trouble among face three.",
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
                                                {"key": "VALUE", "value": ")1q1TpGzpE"},
                                                {
                                                    "children": [
                                                        {
                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                            "value": {
                                                                "en": "",
                                                                "fi": "Where official agree order just raise.",
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
                                                {"key": "VALUE", "value": "+2(bkVx7(8"},
                                                {
                                                    "children": [
                                                        {
                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                            "value": {
                                                                "en": "",
                                                                "fi": "Many happy better agree concern often almost.",
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
                                                {"key": "VALUE", "value": "&KXlatF20E"},
                                                {
                                                    "children": [
                                                        {
                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                            "value": {
                                                                "en": "",
                                                                "fi": "Program song couple central each color.",
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
                                                {"key": "VALUE", "value": "_O2oUJuK@V"},
                                                {
                                                    "children": [
                                                        {
                                                            "key": "NAME_WITH_TRANSLATIONS",
                                                            "value": {
                                                                "en": "",
                                                                "fi": "Bit other she chair cover whether.",
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
                                {
                                    "key": "NOTES",
                                    "value": "GDPR sensitive test notes for child",
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
