# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_add_event_staff_user 1"] = {
    "data": {
        "addEvent": {
            "event": {
                "capacityPerOccurrence": 30,
                "duration": 1000,
                "image": "",
                "imageAltText": "Image alt text",
                "participantsPerInvite": "FAMILY",
                "publishedAt": None,
                "translations": [
                    {
                        "description": "desc",
                        "imageAltText": "Image alt text",
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
                "event": {"createdAt": "2020-12-12T00:00:00+00:00"},
                "time": "1986-12-12T16:40:48+00:00",
                "venue": {"createdAt": "2020-12-12T00:00:00+00:00"},
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
                "image": "http://testserver/media/spring.jpg",
                "imageAltText": "",
                "occurrences": {"edges": []},
                "participantsPerInvite": "FAMILY",
                "translations": [
                    {
                        "description": "desc",
                        "imageAltText": "Image alt text",
                        "languageCode": "SV",
                        "name": "Event test in suomi",
                        "shortDescription": "Short desc",
                    },
                    {
                        "description": """Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                        "imageAltText": "",
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
    "data": {"publishEvent": {"event": {"publishedAt": "2020-12-12T00:00:00+00:00"}}}
}

snapshots["test_occurrence_query_normal_user 1"] = {
    "data": {
        "occurrence": {
            "enrolments": {"edges": []},
            "event": {
                "capacityPerOccurrence": 50,
                "duration": 197,
                "image": "http://testserver/media/spring.jpg",
                "participantsPerInvite": "FAMILY",
                "publishedAt": "2020-12-12T00:00:00+00:00",
                "translations": [
                    {
                        "description": """Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                        "languageCode": "FI",
                        "name": "Free heart significant machine try.",
                        "shortDescription": "Perform in weight success answer.",
                    }
                ],
            },
            "remainingCapacity": 50,
            "time": "2020-12-12T00:00:00+00:00",
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
                        "wwwUrl": "http://www.smith-woods.com/",
                    }
                ]
            },
        }
    }
}

snapshots["test_update_occurrence_staff_user 1"] = {
    "data": {
        "updateOccurrence": {
            "occurrence": {
                "event": {"createdAt": "2020-12-12T00:00:00+00:00"},
                "time": "1986-12-12T16:40:48+00:00",
                "venue": {"createdAt": "2020-12-12T00:00:00+00:00"},
            }
        }
    }
}

snapshots["test_enrol_occurrence 1"] = {
    "data": {
        "enrolOccurrence": {
            "enrolment": {
                "child": {"firstName": "Robert"},
                "createdAt": "2020-12-12T00:00:00+00:00",
                "occurrence": {"time": "2020-12-12T00:00:00+00:00"},
            }
        }
    }
}

snapshots["test_occurrences_filter_by_date 1"] = {
    "data": {
        "occurrences": {
            "edges": [
                {"node": {"time": "1970-01-02T00:00:00+00:00"}},
                {"node": {"time": "1970-01-02T00:00:00+00:00"}},
            ]
        }
    }
}

snapshots["test_occurrences_filter_by_time 1"] = {
    "data": {
        "occurrences": {
            "edges": [
                {"node": {"time": "1970-01-01T11:00:00+00:00"}},
                {"node": {"time": "1970-01-02T11:00:00+00:00"}},
            ]
        }
    }
}

snapshots["test_occurrence_available_capacity 1"] = {
    "data": {
        "occurrence": {
            "enrolments": {"edges": []},
            "event": {
                "capacityPerOccurrence": 50,
                "duration": 197,
                "image": "http://testserver/media/spring.jpg",
                "participantsPerInvite": "FAMILY",
                "publishedAt": "2020-12-12T00:00:00+00:00",
                "translations": [
                    {
                        "description": """Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                        "languageCode": "EN",
                        "name": "Free heart significant machine try.",
                        "shortDescription": "Perform in weight success answer.",
                    }
                ],
            },
            "remainingCapacity": 47,
            "time": "2020-12-12T00:00:00+00:00",
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
                        "languageCode": "EN",
                        "name": "Able process base sing according.",
                        "wwwUrl": "http://www.smith-woods.com/",
                    }
                ]
            },
        }
    }
}

snapshots["test_enrolment_visibility 1"] = {
    "data": {
        "occurrence": {
            "enrolments": {"edges": [{"node": {"child": {"firstName": "James"}}}]},
            "event": {
                "capacityPerOccurrence": 22,
                "duration": 255,
                "image": "http://testserver/media/parent.jpg",
                "participantsPerInvite": "FAMILY",
                "publishedAt": "2020-12-12T00:00:00+00:00",
                "translations": [
                    {
                        "description": """Glass person along age else. Skill down subject town range north skin.
Watch condition like lay still bar later. Daughter order stay sign discover.""",
                        "languageCode": "EN",
                        "name": "Trial western break page box child care. Tv minute defense.",
                        "shortDescription": "Address prove color effort.",
                    }
                ],
            },
            "remainingCapacity": 18,
            "time": "2020-12-12T00:00:00+00:00",
            "venue": {
                "translations": [
                    {
                        "accessibilityInfo": """Data control as receive. End available avoid girl middle.
Sense person the probably. Simply state social believe policy. Score think turn argue present.""",
                        "additionalInfo": "Tough plant traditional after born up always. Return student light a point charge.",
                        "address": """18274 Justin Skyway
Patriciashire, WV 03644""",
                        "arrivalInstructions": "Assume training seek full several. Authority develop identify ready.",
                        "description": """City sing himself yard. Election stay every something base.
Final central situation past ready join enjoy. Huge get this success commercial recently from. Name likely behind mission network who.""",
                        "languageCode": "EN",
                        "name": "Home memory respond improve office table.",
                        "wwwUrl": "http://www.fischer-wolf.com/",
                    }
                ]
            },
        }
    }
}

snapshots["test_events_query_normal_user 1"] = {
    "data": {
        "events": {
            "edges": [
                {
                    "node": {
                        "capacityPerOccurrence": 50,
                        "createdAt": "2020-12-12T00:00:00+00:00",
                        "description": """Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                        "duration": 197,
                        "image": "http://testserver/media/spring.jpg",
                        "imageAltText": "",
                        "name": "Free heart significant machine try.",
                        "occurrences": {
                            "edges": [
                                {
                                    "node": {
                                        "remainingCapacity": 50,
                                        "time": "1986-02-27T01:22:35+00:00",
                                        "venue": {
                                            "translations": [
                                                {
                                                    "description": "Later evening southern would according strong. Analysis season project executive entire.",
                                                    "languageCode": "FI",
                                                    "name": "Subject town range.",
                                                }
                                            ]
                                        },
                                    }
                                }
                            ]
                        },
                        "participantsPerInvite": "FAMILY",
                        "publishedAt": "2020-12-12T00:00:00+00:00",
                        "shortDescription": "Perform in weight success answer.",
                        "translations": [
                            {
                                "description": """Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                                "imageAltText": "",
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
            "capacityPerOccurrence": 50,
            "createdAt": "2020-12-12T00:00:00+00:00",
            "description": """Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
            "duration": 197,
            "image": "http://testserver/media/spring.jpg",
            "imageAltText": "",
            "name": "Free heart significant machine try.",
            "occurrences": {
                "edges": [
                    {
                        "node": {
                            "remainingCapacity": 50,
                            "time": "1986-02-27T01:22:35+00:00",
                            "venue": {
                                "translations": [
                                    {
                                        "description": "Later evening southern would according strong. Analysis season project executive entire.",
                                        "languageCode": "FI",
                                        "name": "Subject town range.",
                                    }
                                ]
                            },
                        }
                    }
                ]
            },
            "participantsPerInvite": "FAMILY",
            "publishedAt": "2020-12-12T00:00:00+00:00",
            "shortDescription": "Perform in weight success answer.",
            "translations": [
                {
                    "description": """Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                    "imageAltText": "",
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
                            "capacityPerOccurrence": 50,
                            "duration": 197,
                            "image": "http://testserver/media/spring.jpg",
                            "participantsPerInvite": "FAMILY",
                            "publishedAt": "2020-12-12T00:00:00+00:00",
                            "translations": [
                                {
                                    "description": """Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                                    "languageCode": "FI",
                                    "name": "Free heart significant machine try.",
                                    "shortDescription": "Perform in weight success answer.",
                                }
                            ],
                        },
                        "remainingCapacity": 50,
                        "time": "2020-12-12T00:00:00+00:00",
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
                                    "wwwUrl": "http://www.smith-woods.com/",
                                }
                            ]
                        },
                    }
                }
            ]
        }
    }
}

snapshots["test_occurrences_filter_by_upcoming 1"] = {
    "data": {
        "occurrences": {
            "edges": [
                {"node": {"time": "1970-01-01T00:00:00+00:00"}},
                {"node": {"time": "2020-12-12T00:00:00+00:00"}},
            ]
        }
    }
}

snapshots["test_events_query_staff_user 1"] = {
    "data": {
        "events": {
            "edges": [
                {
                    "node": {
                        "capacityPerOccurrence": 50,
                        "createdAt": "2020-12-12T00:00:00+00:00",
                        "description": """Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                        "duration": 197,
                        "image": "http://testserver/media/spring.jpg",
                        "imageAltText": "",
                        "name": "Free heart significant machine try.",
                        "occurrences": {
                            "edges": [
                                {
                                    "node": {
                                        "remainingCapacity": 50,
                                        "time": "2009-07-12T04:07:58+00:00",
                                        "venue": {
                                            "translations": [
                                                {
                                                    "description": "Training thought price. Effort clear and local challenge box. Care figure mention wrong when lead involve.",
                                                    "languageCode": "FI",
                                                    "name": "Thank realize staff staff read.",
                                                }
                                            ]
                                        },
                                    }
                                }
                            ]
                        },
                        "participantsPerInvite": "FAMILY",
                        "publishedAt": "2020-12-12T00:00:00+00:00",
                        "shortDescription": "Perform in weight success answer.",
                        "translations": [
                            {
                                "description": """Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                                "imageAltText": "",
                                "languageCode": "FI",
                                "name": "Free heart significant machine try.",
                                "shortDescription": "Perform in weight success answer.",
                            }
                        ],
                        "updatedAt": "2020-12-12T00:00:00+00:00",
                    }
                },
                {
                    "node": {
                        "capacityPerOccurrence": 28,
                        "createdAt": "2020-12-12T00:00:00+00:00",
                        "description": """Wonder everything pay parent theory go home. Book and interesting sit future dream party. Truth list pressure stage history.
If his their best. Election stay every something base.""",
                        "duration": 42,
                        "image": "http://testserver/media/think.jpg",
                        "imageAltText": "",
                        "name": "Able process base sing according.",
                        "occurrences": {
                            "edges": [
                                {
                                    "node": {
                                        "remainingCapacity": 28,
                                        "time": "1975-04-27T11:57:31+00:00",
                                        "venue": {
                                            "translations": [
                                                {
                                                    "description": """Work early property your stage receive. Determine sort under car.
Check word style also attention word. Throw three girl capital no situation. Explain page practice sing every.""",
                                                    "languageCode": "FI",
                                                    "name": "Including believe eye dog education spend.",
                                                }
                                            ]
                                        },
                                    }
                                }
                            ]
                        },
                        "participantsPerInvite": "FAMILY",
                        "publishedAt": None,
                        "shortDescription": "Later evening southern would according strong.",
                        "translations": [
                            {
                                "description": """Wonder everything pay parent theory go home. Book and interesting sit future dream party. Truth list pressure stage history.
If his their best. Election stay every something base.""",
                                "imageAltText": "",
                                "languageCode": "FI",
                                "name": "Able process base sing according.",
                                "shortDescription": "Later evening southern would according strong.",
                            }
                        ],
                        "updatedAt": "2020-12-12T00:00:00+00:00",
                    }
                },
            ]
        }
    }
}

snapshots["test_occurrences_query_staff_user 1"] = {
    "data": {
        "occurrences": {
            "edges": [
                {
                    "node": {
                        "event": {
                            "capacityPerOccurrence": 50,
                            "duration": 197,
                            "image": "http://testserver/media/spring.jpg",
                            "participantsPerInvite": "FAMILY",
                            "publishedAt": "2020-12-12T00:00:00+00:00",
                            "translations": [
                                {
                                    "description": """Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                                    "languageCode": "FI",
                                    "name": "Free heart significant machine try.",
                                    "shortDescription": "Perform in weight success answer.",
                                }
                            ],
                        },
                        "remainingCapacity": 50,
                        "time": "2020-12-12T00:00:00+00:00",
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
                                    "wwwUrl": "http://www.smith-woods.com/",
                                }
                            ]
                        },
                    }
                },
                {
                    "node": {
                        "event": {
                            "capacityPerOccurrence": 2,
                            "duration": 194,
                            "image": "http://testserver/media/whom.jpg",
                            "participantsPerInvite": "CHILD_AND_GUARDIAN",
                            "publishedAt": None,
                            "translations": [
                                {
                                    "description": "No society evidence answer need benefit ready. Notice rule huge realize at rather. Place against moment tax group.",
                                    "languageCode": "FI",
                                    "name": "Nearly gun two born land military first.",
                                    "shortDescription": "Natural direction traditional whether serious.",
                                }
                            ],
                        },
                        "remainingCapacity": 2,
                        "time": "2020-12-12T00:00:00+00:00",
                        "venue": {
                            "translations": [
                                {
                                    "accessibilityInfo": """Manager movie owner long own personal into. Toward race five least.
I task moment want write her. Pm large benefit occur eat discuss quickly.""",
                                    "additionalInfo": "Account heart feeling before modern consumer discussion. Put close term where up. Order trip a into hold project month.",
                                    "address": """869 Reed Crescent Suite 449
Jenniferhaven, AL 47756""",
                                    "arrivalInstructions": """Six feel real fast.
Key crime trial investment difference. Let join might player example environment.
Offer organization model remember. Morning culture late oil sell.""",
                                    "description": """Conference thing much like test.
Tonight including believe eye. Range bit college question animal. Treatment suggest ask choice modern particular specific. Free anyone floor office.""",
                                    "languageCode": "FI",
                                    "name": "Minute rest two special far magazine.",
                                    "wwwUrl": "https://www.johnson.net/",
                                }
                            ]
                        },
                    }
                },
            ]
        }
    }
}

snapshots["test_occurrences_filter_by_venue 1"] = {
    "data": {
        "occurrences": {
            "edges": [
                {"node": {"time": "1970-01-05T18:13:40+00:00"}},
                {"node": {"time": "1990-03-28T12:56:55+00:00"}},
                {"node": {"time": "1999-02-16T07:12:13+00:00"}},
            ]
        }
    }
}
