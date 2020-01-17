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
                                            "duration": 362,
                                            "translations": [
                                                {
                                                    "description": """Least then top sing. Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
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
                        "seatCount": 88,
                        "translations": [
                            {
                                "description": "Later evening southern would according strong. Analysis season project executive entire.",
                                "languageCode": "FI",
                                "name": "Never skill down subject town.",
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
                                "duration": 362,
                                "translations": [
                                    {
                                        "description": """Least then top sing. Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                                        "languageCode": "FI",
                                        "name": "Worker position late leg him president.",
                                    }
                                ],
                            },
                            "time": "1986-12-12T16:40:48+00:00",
                        }
                    }
                ]
            },
            "seatCount": 88,
            "translations": [
                {
                    "description": "Later evening southern would according strong. Analysis season project executive entire.",
                    "languageCode": "FI",
                    "name": "Never skill down subject town.",
                }
            ],
        }
    }
}

snapshots["test_add_venue_staff_user 1"] = {
    "data": {
        "addVenue": {
            "venue": {
                "seatCount": 1000,
                "translations": [
                    {
                        "description": "Venue description",
                        "languageCode": "FI",
                        "name": "Venue name",
                    }
                ],
            }
        }
    }
}
