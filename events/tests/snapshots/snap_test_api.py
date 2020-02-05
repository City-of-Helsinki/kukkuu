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
                        "capacityPerOccurrence": 805,
                        "createdAt": "2020-12-12T00:00:00+00:00",
                        "duration": 197,
                        "image": "spring.jpg",
                        "occurrences": {"edges": []},
                        "participantsPerInvite": "FAMILY",
                        "publishedAt": None,
                        "translations": [
                            {
                                "description": """Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                                "languageCode": "FI",
                                "name": "Free heart significant machine try.",
                                "shortDescription": "Perform in weight success answer.",
                            }
                        ],
                        "updatedAt": "2020-12-12T00:00:00+00:00",
                    }
                }
            ]
        }
    }
}

snapshots["test_event_query_normal_user 1"] = {
    "data": {
        "event": {
            "capacityPerOccurrence": 805,
            "createdAt": "2020-12-12T00:00:00+00:00",
            "duration": 197,
            "image": "spring.jpg",
            "occurrences": {"edges": []},
            "participantsPerInvite": "FAMILY",
            "publishedAt": None,
            "translations": [
                {
                    "description": """Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                    "languageCode": "FI",
                    "name": "Free heart significant machine try.",
                    "shortDescription": "Perform in weight success answer.",
                }
            ],
            "updatedAt": "2020-12-12T00:00:00+00:00",
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
                            "capacityPerOccurrence": 805,
                            "duration": 181,
                            "image": "spring.jpg",
                            "participantsPerInvite": "FAMILY",
                            "publishedAt": None,
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
                                    "name": "Able process base sing according.",
                                    "wwwUrl": "http://brooks.org/",
                                }
                            ]
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
                "capacityPerOccurrence": 805,
                "duration": 181,
                "image": "spring.jpg",
                "participantsPerInvite": "FAMILY",
                "publishedAt": None,
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
                        "name": "Able process base sing according.",
                        "wwwUrl": "http://brooks.org/",
                    }
                ]
            },
        }
    }
}

snapshots["test_add_event_staff_user 1"] = {
    "data": {
        "addEvent": {
            "event": {
                "capacityPerOccurrence": 30,
                "duration": 1000,
                "image": "",
                "participantsPerInvite": "FAMILY",
                "publishedAt": None,
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
                "venue": {"id": "VmVudWVOb2RlOjQ="},
            }
        }
    }
}

snapshots["test_update_occurrence_staff_user 1"] = {
    "data": {
        "updateOccurrence": {
            "occurrence": {
                "event": {"id": "RXZlbnROb2RlOjk="},
                "id": "T2NjdXJyZW5jZU5vZGU6NQ==",
                "time": "1986-12-12T16:40:48+00:00",
                "venue": {"id": "VmVudWVOb2RlOjU="},
            }
        }
    }
}

snapshots["test_update_event_staff_user 1"] = {
    "data": {
        "updateEvent": {
            "event": {
                "capacityPerOccurrence": 30,
                "duration": 1000,
                "id": "RXZlbnROb2RlOjEx",
                "occurrences": {"edges": []},
                "participantsPerInvite": "FAMILY",
                "translations": [
                    {
                        "description": "desc",
                        "languageCode": "SV",
                        "name": "Event test in suomi",
                        "shortDescription": "Short desc",
                    },
                    {
                        "description": """Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                        "languageCode": "FI",
                        "name": "Free heart significant machine try.",
                        "shortDescription": "Perform in weight success answer.",
                    },
                ],
            }
        }
    }
}

snapshots["test_staff_publish_event 1"] = {
    "data": {
        "publishEvent": {
            "event": {
                "id": "RXZlbnROb2RlOjE1",
                "publishedAt": "2020-12-12T02:00:00+02:00",
            }
        }
    }
}
