# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_events_query_normal_user 1"] = {
    "data": {
        "events": {
            "edges": [
                {
                    "node": {
                        "createdAt": "2019-12-12T00:00:00+00:00",
                        "duration": 362,
                        "occurrences": {
                            "edges": [
                                {
                                    "node": {
                                        "time": "1986-12-12T16:40:48+00:00",
                                        "venue": {
                                            "seatCount": 88,
                                            "translations": [
                                                {
                                                    "description": "Later evening southern would according strong. Analysis season project executive entire.",
                                                    "languageCode": "FI",
                                                    "name": "Never skill down subject town.",
                                                }
                                            ],
                                        },
                                    }
                                }
                            ]
                        },
                        "translations": [
                            {
                                "description": """Least then top sing. Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                                "languageCode": "FI",
                                "name": "Worker position late leg him president.",
                                "shortDescription": "Together history perform.",
                            }
                        ],
                        "updatedAt": "2019-12-12T00:00:00+00:00",
                    }
                }
            ]
        }
    }
}

snapshots["test_event_query_normal_user 1"] = {
    "data": {
        "event": {
            "createdAt": "2019-12-12T00:00:00+00:00",
            "duration": 760,
            "occurrences": {"edges": []},
            "translations": [
                {
                    "description": """Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                    "languageCode": "FI",
                    "name": "Free heart significant machine try.",
                    "shortDescription": "Fall long respond draw military dog.",
                }
            ],
            "updatedAt": "2019-12-12T00:00:00+00:00",
        }
    }
}

snapshots["test_occurrences_query_normal_user 1"] = {
    "data": {
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
                                    "shortDescription": "Together history perform.",
                                }
                            ],
                        },
                        "time": "1986-12-12T16:40:48+00:00",
                        "venue": {
                            "seatCount": 88,
                            "translations": [
                                {
                                    "description": "Later evening southern would according strong. Analysis season project executive entire.",
                                    "languageCode": "FI",
                                    "name": "Never skill down subject town.",
                                }
                            ],
                        },
                    }
                }
            ]
        }
    }
}

snapshots["test_occurrence_query_normal_user 1"] = {
    "data": {
        "occurrence": {
            "event": {
                "duration": 362,
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
            "venue": {
                "seatCount": 88,
                "translations": [
                    {
                        "description": "Later evening southern would according strong. Analysis season project executive entire.",
                        "languageCode": "FI",
                        "name": "Never skill down subject town.",
                    }
                ],
            },
        }
    }
}

snapshots["test_add_event_staff_user 1"] = {
    "data": {
        "addEvent": {
            "event": {
                "duration": 1000,
                "translations": [
                    {
                        "description": "desc",
                        "languageCode": "FI",
                        "name": "Event test",
                        "shortDescription": "Short desc",
                    }
                ],
            }
        }
    }
}

snapshots["test_add_occurrence_staff_user 1"] = {
    "data": {
        "addOccurrence": {
            "occurrence": {
                "event": {"id": "RXZlbnROb2RlOjg="},
                "time": "1986-12-12T16:40:48+00:00",
                "venue": {"id": "VmVudWVOb2RlOjU="},
            }
        }
    }
}
