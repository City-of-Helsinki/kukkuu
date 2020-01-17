# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_venues_query_normal_user 1"] = {
    "data": {
        "venues": {
            "edges": [
                {
                    "node": {
                        "occurrences": {
                            "edges": [
                                {
                                    "node": {
                                        "event": {
                                            "capacityPerOccurrence": 805,
                                            "duration": 181,
                                            "image": "spring.jpg",
                                            "participantsPerInvite": "FAMILY",
                                            "publishedAt": "1986-02-27T01:22:35+00:00",
                                            "translations": [
                                                {
                                                    "description": """Least then top sing. Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                                                    "languageCode": "FI",
                                                    "name": "Worker position late leg him president.",
                                                    "shortDescription": "Together history perform.",
                                                }
                                            ],
                                        },
                                        "time": "1986-12-12T16:40:48+00:00",
                                    }
                                }
                            ]
                        },
                        "translations": [
                            {
                                "accessibilityInfo": "Enjoy office water those notice medical. Already name likely behind mission network. Think significant land especially can quite.",
                                "additionalInfo": """Prevent pressure point. Voice radio happen color scene.
Assume training seek full several. Authority develop identify ready.""",
                                "address": """1449 Hill Squares
South Zacharyborough, CO 33337""",
                                "arrivalInstructions": """Last appear experience seven. Throw wrong party wall agency customer clear. Control as receive cup.
Family around year off. Sense person the probably.""",
                                "description": "Later evening southern would according strong. Analysis season project executive entire.",
                                "languageCode": "FI",
                                "name": "Subject town range.",
                                "wwwUrl": "http://brooks.org/",
                            }
                        ],
                    }
                }
            ]
        }
    }
}

snapshots["test_venue_query_normal_user 1"] = {
    "data": {
        "venue": {
            "occurrences": {
                "edges": [
                    {
                        "node": {
                            "event": {
                                "capacityPerOccurrence": 805,
                                "duration": 181,
                                "image": "spring.jpg",
                                "participantsPerInvite": "FAMILY",
                                "publishedAt": "1986-02-27T01:22:35+00:00",
                                "translations": [
                                    {
                                        "description": """Least then top sing. Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                                        "languageCode": "FI",
                                        "name": "Worker position late leg him president.",
                                        "shortDescription": "Together history perform.",
                                    }
                                ],
                            },
                            "time": "1986-12-12T16:40:48+00:00",
                        }
                    }
                ]
            },
            "translations": [
                {
                    "accessibilityInfo": "Enjoy office water those notice medical. Already name likely behind mission network. Think significant land especially can quite.",
                    "additionalInfo": """Prevent pressure point. Voice radio happen color scene.
Assume training seek full several. Authority develop identify ready.""",
                    "address": """1449 Hill Squares
South Zacharyborough, CO 33337""",
                    "arrivalInstructions": """Last appear experience seven. Throw wrong party wall agency customer clear. Control as receive cup.
Family around year off. Sense person the probably.""",
                    "description": "Later evening southern would according strong. Analysis season project executive entire.",
                    "languageCode": "FI",
                    "name": "Subject town range.",
                    "wwwUrl": "http://brooks.org/",
                }
            ],
        }
    }
}

snapshots["test_add_venue_staff_user 1"] = {
    "data": {
        "addVenue": {
            "venue": {
                "translations": [
                    {
                        "accessibilityInfo": "Accessibility info",
                        "additionalInfo": "Additional info",
                        "address": "Address",
                        "arrivalInstructions": "Arrival instruction",
                        "description": "Venue description",
                        "languageCode": "FI",
                        "name": "Venue name",
                        "wwwUrl": "www.url.com",
                    }
                ]
            }
        }
    }
}
