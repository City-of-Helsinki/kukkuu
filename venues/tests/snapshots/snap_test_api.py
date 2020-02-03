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
                        "occurrences": {"edges": []},
                        "translations": [
                            {
                                "accessibilityInfo": "From daughter order stay sign discover eight. Toward scientist service wonder everything. Middle moment strong hand push book and interesting.",
                                "additionalInfo": "Training thought price. Effort clear and local challenge box. Care figure mention wrong when lead involve.",
                                "address": """48830 Whitehead Rapid Suite 548
Whiteview, TN 11309""",
                                "arrivalInstructions": "Benefit treat final central. Past ready join enjoy. Huge get this success commercial recently from.",
                                "description": """Perform in weight success answer. Hospital number lose least then. Beyond than trial western.
Page box child care any concern. Defense level church use.""",
                                "languageCode": "FI",
                                "name": "Free heart significant machine try.",
                                "wwwUrl": "http://www.hernandez.net/",
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
            "occurrences": {"edges": []},
            "translations": [
                {
                    "accessibilityInfo": "From daughter order stay sign discover eight. Toward scientist service wonder everything. Middle moment strong hand push book and interesting.",
                    "additionalInfo": "Training thought price. Effort clear and local challenge box. Care figure mention wrong when lead involve.",
                    "address": """48830 Whitehead Rapid Suite 548
Whiteview, TN 11309""",
                    "arrivalInstructions": "Benefit treat final central. Past ready join enjoy. Huge get this success commercial recently from.",
                    "description": """Perform in weight success answer. Hospital number lose least then. Beyond than trial western.
Page box child care any concern. Defense level church use.""",
                    "languageCode": "FI",
                    "name": "Free heart significant machine try.",
                    "wwwUrl": "http://www.hernandez.net/",
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

snapshots["test_update_venue_staff_user 1"] = {
    "data": {
        "updateVenue": {
            "venue": {
                "id": "VmVudWVOb2RlOjY=",
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
                ],
            }
        }
    }
}

snapshots["test_venues_query_unauthenticated 1"] = {
    "data": {
        "venues": {
            "edges": [
                {
                    "node": {
                        "occurrences": {"edges": []},
                        "translations": [
                            {
                                "accessibilityInfo": """Range north skin watch.
Condition like lay still bar. From daughter order stay sign discover eight. Toward scientist service wonder everything.""",
                                "additionalInfo": """Local challenge box myself last.
Experience seven Republican throw wrong party wall.
Policy data control as receive.
Teacher subject family around year. Space speak sense person the probably deep.""",
                                "address": """5816 Justin Spring
Thomasfort, SC 31620""",
                                "arrivalInstructions": "Good father boy economy the. Enjoy office water those notice medical. Already name likely behind mission network.",
                                "description": """Position late leg him president compare. Hotel town south. Together history perform.
Success answer entire increase thank. Least then top sing. Serious listen police shake.""",
                                "languageCode": "FI",
                                "name": "Record card my. Sure sister return.",
                                "wwwUrl": "https://luna.info/",
                            }
                        ],
                    }
                }
            ]
        }
    }
}

snapshots["test_venue_query_unauthenticated 1"] = {
    "data": {
        "venue": {
            "occurrences": {"edges": []},
            "translations": [
                {
                    "accessibilityInfo": """Range north skin watch.
Condition like lay still bar. From daughter order stay sign discover eight. Toward scientist service wonder everything.""",
                    "additionalInfo": """Local challenge box myself last.
Experience seven Republican throw wrong party wall.
Policy data control as receive.
Teacher subject family around year. Space speak sense person the probably deep.""",
                    "address": """5816 Justin Spring
Thomasfort, SC 31620""",
                    "arrivalInstructions": "Good father boy economy the. Enjoy office water those notice medical. Already name likely behind mission network.",
                    "description": """Position late leg him president compare. Hotel town south. Together history perform.
Success answer entire increase thank. Least then top sing. Serious listen police shake.""",
                    "languageCode": "FI",
                    "name": "Record card my. Sure sister return.",
                    "wwwUrl": "https://luna.info/",
                }
            ],
        }
    }
}
