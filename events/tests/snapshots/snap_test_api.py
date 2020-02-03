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
                        "publishedAt": "1986-02-27T01:22:35+00:00",
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
            "publishedAt": "1986-02-27T01:22:35+00:00",
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
                                    "name": "Subject town range.",
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
                        "name": "Subject town range.",
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
                "publishedAt": "1986-12-12T16:40:48+00:00",
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
                "event": {"id": "RXZlbnROb2RlOjEw"},
                "time": "1986-12-12T16:40:48+00:00",
                "venue": {"id": "VmVudWVOb2RlOjU="},
            }
        }
    }
}

snapshots["test_update_occurrence_staff_user 1"] = {
    "data": {
        "updateOccurrence": {
            "occurrence": {
                "event": {"id": "RXZlbnROb2RlOjEx"},
                "id": "T2NjdXJyZW5jZU5vZGU6Ng==",
                "time": "1986-12-12T16:40:48+00:00",
                "venue": {"id": "VmVudWVOb2RlOjY="},
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
                "id": "RXZlbnROb2RlOjEz",
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

snapshots["test_events_query_unauthenticated 1"] = {
    "data": {
        "events": {
            "edges": [
                {
                    "node": {
                        "capacityPerOccurrence": 394,
                        "createdAt": "2020-12-12T00:00:00+00:00",
                        "duration": 170,
                        "image": "enter.jpg",
                        "occurrences": {"edges": []},
                        "participantsPerInvite": "CHILD_AND_GUARDIAN",
                        "publishedAt": "2007-12-04T20:40:56+00:00",
                        "translations": [
                            {
                                "description": "Success answer entire increase thank. Least then top sing. Serious listen police shake.",
                                "languageCode": "FI",
                                "name": "Record card my. Sure sister return.",
                                "shortDescription": "Position late leg him president compare. Hotel town south.",
                            }
                        ],
                        "updatedAt": "2020-12-12T00:00:00+00:00",
                    }
                }
            ]
        }
    }
}

snapshots["test_event_query_unauthenticated 1"] = {
    "data": {
        "event": {
            "capacityPerOccurrence": 394,
            "createdAt": "2020-12-12T00:00:00+00:00",
            "duration": 170,
            "image": "enter.jpg",
            "occurrences": {"edges": []},
            "participantsPerInvite": "CHILD_AND_GUARDIAN",
            "publishedAt": "2007-12-04T20:40:56+00:00",
            "translations": [
                {
                    "description": "Success answer entire increase thank. Least then top sing. Serious listen police shake.",
                    "languageCode": "FI",
                    "name": "Record card my. Sure sister return.",
                    "shortDescription": "Position late leg him president compare. Hotel town south.",
                }
            ],
            "updatedAt": "2020-12-12T00:00:00+00:00",
        }
    }
}

snapshots["test_occurrences_query_unauthenticated 1"] = {
    "data": {
        "occurrences": {
            "edges": [
                {
                    "node": {
                        "event": {
                            "capacityPerOccurrence": 805,
                            "duration": 12,
                            "image": "spring.jpg",
                            "participantsPerInvite": "FAMILY",
                            "publishedAt": "1986-02-27T01:22:35+00:00",
                            "translations": [
                                {
                                    "description": """Least then top sing. Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                                    "languageCode": "FI",
                                    "name": "Card my side sure sister return ten. Exactly guy site late eat.",
                                    "shortDescription": "Start majority government together history perform.",
                                }
                            ],
                        },
                        "time": "1970-12-20T22:29:18+00:00",
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
                                    "name": "Subject town range.",
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

snapshots["test_occurrence_query_unauthenticated 1"] = {
    "data": {
        "occurrence": {
            "event": {
                "capacityPerOccurrence": 805,
                "duration": 12,
                "image": "spring.jpg",
                "participantsPerInvite": "FAMILY",
                "publishedAt": "1986-02-27T01:22:35+00:00",
                "translations": [
                    {
                        "description": """Least then top sing. Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                        "languageCode": "FI",
                        "name": "Card my side sure sister return ten. Exactly guy site late eat.",
                        "shortDescription": "Start majority government together history perform.",
                    }
                ],
            },
            "time": "1970-12-20T22:29:18+00:00",
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
                        "name": "Subject town range.",
                        "wwwUrl": "http://brooks.org/",
                    }
                ]
            },
        }
    }
}
