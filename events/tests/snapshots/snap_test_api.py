# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_add_event_group[model_perm] 1"] = {
    "data": {
        "addEventGroup": {
            "eventGroup": {
                "image": "",
                "imageAltText": "Image alt text",
                "project": {"year": 2020},
                "publishedAt": None,
                "translations": [
                    {
                        "description": "desc",
                        "imageAltText": "Image alt text",
                        "languageCode": "FI",
                        "name": "Event group test",
                        "shortDescription": "Short desc",
                    }
                ],
            }
        }
    }
}

snapshots["test_add_event_group[object_perm] 1"] = {
    "data": {
        "addEventGroup": {
            "eventGroup": {
                "image": "",
                "imageAltText": "Image alt text",
                "project": {"year": 2020},
                "publishedAt": None,
                "translations": [
                    {
                        "description": "desc",
                        "imageAltText": "Image alt text",
                        "languageCode": "FI",
                        "name": "Event group test",
                        "shortDescription": "Short desc",
                    }
                ],
            }
        }
    }
}

snapshots["test_add_event_project_user 1"] = {
    "data": {
        "addEvent": {
            "event": {
                "capacityPerOccurrence": 30,
                "duration": 1000,
                "image": "",
                "imageAltText": "Image alt text",
                "participantsPerInvite": "FAMILY",
                "project": {"year": 2020},
                "publishedAt": None,
                "readyForEventGroupPublishing": False,
                "ticketSystem": {"type": "INTERNAL"},
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

snapshots["test_add_occurrence_project_user 1"] = {
    "data": {
        "addOccurrence": {
            "occurrence": {
                "capacity": 35,
                "capacityOverride": None,
                "event": {"createdAt": "2020-12-12T00:00:00+00:00"},
                "occurrenceLanguage": "FI",
                "ticketSystem": {"type": "INTERNAL"},
                "time": "1986-12-12T16:40:48+00:00",
                "venue": {"createdAt": "2020-12-12T00:00:00+00:00"},
            }
        }
    }
}

snapshots["test_add_occurrence_ticket_system_url 1"] = {
    "data": {
        "addOccurrence": {
            "occurrence": {
                "capacity": 9,
                "capacityOverride": None,
                "event": {"createdAt": "2020-12-12T00:00:00+00:00"},
                "occurrenceLanguage": "FI",
                "ticketSystem": {"type": "TICKETMASTER", "url": "https://example.com"},
                "time": "1986-12-12T16:40:48+00:00",
                "venue": {"createdAt": "2020-12-12T00:00:00+00:00"},
            }
        }
    }
}

snapshots["test_add_ticketmaster_event 1"] = {
    "data": {"addEvent": {"event": {"ticketSystem": {"type": "TICKETMASTER"}}}}
}

snapshots["test_assign_ticket_system_password 1"] = {
    "data": {
        "assignTicketSystemPassword": {
            "child": {"firstName": "Joshua", "lastName": "Jensen"},
            "event": {"name": "Dog hospital number."},
            "password": "the correct password",
        }
    }
}

snapshots["test_child_enrol_occurence_from_different_project 1"] = {
    "data": {
        "enrolOccurrence": {
            "enrolment": {
                "child": {"firstName": "Brandon"},
                "createdAt": "2020-12-12T00:00:00+00:00",
                "occurrence": {"time": "2020-12-12T00:00:00+00:00"},
            }
        }
    }
}

snapshots["test_delete_event_group[model_perm] 1"] = {
    "data": {"deleteEventGroup": {"__typename": "DeleteEventGroupMutationPayload"}}
}

snapshots["test_delete_event_group[object_perm] 1"] = {
    "data": {"deleteEventGroup": {"__typename": "DeleteEventGroupMutationPayload"}}
}

snapshots["test_enrol_limit_reached[False-0-False] 1"] = {
    "data": {
        "enrolOccurrence": {
            "enrolment": {
                "child": {"firstName": "Brandon"},
                "createdAt": "2020-11-11T00:00:00+00:00",
                "occurrence": {"time": "2020-11-11T00:00:00+00:00"},
            }
        }
    }
}

snapshots["test_enrol_limit_reached[False-1-False] 1"] = {
    "data": {
        "enrolOccurrence": {
            "enrolment": {
                "child": {"firstName": "Brandon"},
                "createdAt": "2020-11-11T00:00:00+00:00",
                "occurrence": {"time": "2020-11-11T00:00:00+00:00"},
            }
        }
    }
}

snapshots["test_enrol_limit_reached[True-0-False] 1"] = {
    "data": {
        "enrolOccurrence": {
            "enrolment": {
                "child": {"firstName": "Brandon"},
                "createdAt": "2020-11-11T00:00:00+00:00",
                "occurrence": {"time": "2020-11-11T00:00:00+00:00"},
            }
        }
    }
}

snapshots["test_enrol_limit_reached[True-1-False] 1"] = {
    "data": {
        "enrolOccurrence": {
            "enrolment": {
                "child": {"firstName": "Brandon"},
                "createdAt": "2020-11-11T00:00:00+00:00",
                "occurrence": {"time": "2020-11-11T00:00:00+00:00"},
            }
        }
    }
}

snapshots["test_enrol_occurrence 1"] = {
    "data": {
        "enrolOccurrence": {
            "enrolment": {
                "child": {"firstName": "Brandy"},
                "createdAt": "2020-12-12T00:00:00+00:00",
                "occurrence": {"time": "2020-12-12T00:00:00+00:00"},
            }
        }
    }
}

snapshots["test_enrolment_visibility 1"] = {
    "data": {
        "occurrence": {
            "enrolmentCount": 4,
            "enrolments": {"edges": [{"node": {"child": {"firstName": "Brandy"}}}]},
            "event": {
                "capacityPerOccurrence": 25,
                "duration": 1,
                "image": "http://testserver/media/series.jpg",
                "participantsPerInvite": "CHILD_AND_1_OR_2_GUARDIANS",
                "publishedAt": "2020-12-12T00:00:00+00:00",
                "translations": [
                    {
                        "description": "Law ago respond yard door indicate country. Direction traditional whether serious sister work. Beat pressure unit toward movie by.",
                        "languageCode": "FI",
                        "name": "Detail audience campaign college career fight data.",
                        "shortDescription": "Last in able local garden modern they.",
                    }
                ],
            },
            "occurrenceLanguage": "FI",
            "remainingCapacity": 21,
            "ticketSystem": {"type": "INTERNAL"},
            "time": "2020-12-12T00:00:00+00:00",
            "venue": {
                "translations": [
                    {
                        "accessibilityInfo": "Theory go home memory respond improve office. Near increase process truth list pressure. Capital city sing himself yard stuff. Option PM put matter benefit.",
                        "additionalInfo": """Policy data control as receive.
Teacher subject family around year. Space speak sense person the probably deep.
Social believe policy security score. Turn argue present throw spend prevent.""",
                        "address": """404 Figueroa Trace
Pollardview, RI 68038""",
                        "arrivalInstructions": """Significant land especially can quite industry relationship. Which president smile staff country actually generation. Age member whatever open effort clear.
Local challenge box myself last.""",
                        "description": """Page box child care any concern. Defense level church use.
Never news behind. Beat at success decade either enter everything. Newspaper force newspaper business himself exist.""",
                        "languageCode": "FI",
                        "name": "Dog hospital number.",
                        "wwwUrl": "https://www.beck-sherman.com/",
                    }
                ]
            },
        }
    }
}

snapshots["test_enrolment_visibility_project_user 1"] = {
    "data": {
        "occurrence": {
            "enrolments": {"edges": [{"node": {"child": {"firstName": "ME ME ME"}}}]}
        }
    }
}

snapshots["test_erroneous_ticket_verification 1"] = {
    "data": {"verifyTicket": None},
    "errors": [
        {
            "extensions": {"code": "GENERAL_ERROR"},
            "locations": [{"column": 5, "line": 3}],
            "message": "Could not decode the enrolment id",
            "path": ["verifyTicket"],
        }
    ],
}

snapshots["test_event_filter_by_project 1"] = {
    "data": {"events": {"edges": [{"node": {"name": "Should be visible"}}]}}
}

snapshots["test_event_group_events_filtering_by_available_for_child_id 1"] = {
    "data": {"eventGroup": {"events": {"edges": [{"node": {"name": "ME ME ME"}}]}}}
}

snapshots["test_event_group_events_filtering_by_available_for_child_id 2"] = {
    "data": {
        "eventGroup": {
            "events": {
                "edges": [
                    {
                        "node": {
                            "name": "Performance race story capital city sing himself."
                        }
                    },
                    {"node": {"name": "ME ME ME"}},
                ]
            }
        }
    }
}

snapshots["test_event_group_query_normal_user_and_project_user[False] 1"] = {
    "data": {"eventGroup": None}
}

snapshots["test_event_group_query_normal_user_and_project_user[False] 2"] = {
    "data": {
        "eventGroup": {
            "createdAt": "2020-12-12T00:00:00+00:00",
            "description": """Page box child care any concern. Defense level church use.
Never news behind. Beat at success decade either enter everything. Newspaper force newspaper business himself exist.""",
            "events": {"edges": []},
            "image": "thank.jpg",
            "imageAltText": "",
            "name": "Lead behind everyone agency start majority.",
            "project": {"year": 2020},
            "publishedAt": None,
            "shortDescription": "Answer entire increase thank certainly again thought.",
            "translations": [
                {
                    "description": """Page box child care any concern. Defense level church use.
Never news behind. Beat at success decade either enter everything. Newspaper force newspaper business himself exist.""",
                    "imageAltText": "",
                    "languageCode": "FI",
                    "name": "Lead behind everyone agency start majority.",
                    "shortDescription": "Answer entire increase thank certainly again thought.",
                }
            ],
            "updatedAt": "2020-12-12T00:00:00+00:00",
        }
    }
}

snapshots["test_event_group_query_normal_user_and_project_user[True] 1"] = {
    "data": {
        "eventGroup": {
            "createdAt": "2020-12-12T00:00:00+00:00",
            "description": """Page box child care any concern. Defense level church use.
Never news behind. Beat at success decade either enter everything. Newspaper force newspaper business himself exist.""",
            "events": {"edges": []},
            "image": "thank.jpg",
            "imageAltText": "",
            "name": "Lead behind everyone agency start majority.",
            "project": {"year": 2020},
            "publishedAt": "2020-12-12T00:00:00+00:00",
            "shortDescription": "Answer entire increase thank certainly again thought.",
            "translations": [
                {
                    "description": """Page box child care any concern. Defense level church use.
Never news behind. Beat at success decade either enter everything. Newspaper force newspaper business himself exist.""",
                    "imageAltText": "",
                    "languageCode": "FI",
                    "name": "Lead behind everyone agency start majority.",
                    "shortDescription": "Answer entire increase thank certainly again thought.",
                }
            ],
            "updatedAt": "2020-12-12T00:00:00+00:00",
        }
    }
}

snapshots["test_event_group_query_normal_user_and_project_user[True] 2"] = {
    "data": {
        "eventGroup": {
            "createdAt": "2020-12-12T00:00:00+00:00",
            "description": """Page box child care any concern. Defense level church use.
Never news behind. Beat at success decade either enter everything. Newspaper force newspaper business himself exist.""",
            "events": {"edges": []},
            "image": "thank.jpg",
            "imageAltText": "",
            "name": "Lead behind everyone agency start majority.",
            "project": {"year": 2020},
            "publishedAt": "2020-12-12T00:00:00+00:00",
            "shortDescription": "Answer entire increase thank certainly again thought.",
            "translations": [
                {
                    "description": """Page box child care any concern. Defense level church use.
Never news behind. Beat at success decade either enter everything. Newspaper force newspaper business himself exist.""",
                    "imageAltText": "",
                    "languageCode": "FI",
                    "name": "Lead behind everyone agency start majority.",
                    "shortDescription": "Answer entire increase thank certainly again thought.",
                }
            ],
            "updatedAt": "2020-12-12T00:00:00+00:00",
        }
    }
}

snapshots["test_event_group_query_wrong_project 1"] = {"data": {"eventGroup": None}}

snapshots["test_event_query_normal_user 1"] = {
    "data": {
        "event": {
            "capacityPerOccurrence": 35,
            "createdAt": "2020-12-12T00:00:00+00:00",
            "description": """Least then top sing. Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
            "duration": 181,
            "image": "http://testserver/media/teacher.jpg",
            "imageAltText": "",
            "name": "Poor lawyer treat free heart significant.",
            "occurrences": {
                "edges": [
                    {
                        "node": {
                            "enrolmentCount": 0,
                            "remainingCapacity": 35,
                            "ticketSystem": {"type": "INTERNAL"},
                            "time": "1971-04-30T08:38:26+00:00",
                            "venue": {
                                "translations": [
                                    {
                                        "description": "Later evening southern would according strong. Analysis season project executive entire.",
                                        "languageCode": "FI",
                                        "name": "Skill down subject town range north skin.",
                                    }
                                ]
                            },
                        }
                    }
                ]
            },
            "participantsPerInvite": "CHILD_AND_1_OR_2_GUARDIANS",
            "project": {"year": 2020},
            "publishedAt": "2020-12-12T00:00:00+00:00",
            "shortDescription": "Together history perform.",
            "ticketSystem": {"type": "INTERNAL"},
            "translations": [
                {
                    "description": """Least then top sing. Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                    "imageAltText": "",
                    "languageCode": "FI",
                    "name": "Poor lawyer treat free heart significant.",
                    "shortDescription": "Together history perform.",
                }
            ],
            "updatedAt": "2020-12-12T00:00:00+00:00",
        }
    }
}

snapshots["test_event_ticket_system_password_assignation 1"] = {
    "data": {
        "event": {
            "ticketSystem": {
                "childPassword": "the correct password",
                "type": "TICKETMASTER",
            }
        }
    }
}

snapshots["test_event_ticket_system_password_assignation 2"] = {
    "data": {
        "event": {
            "ticketSystem": {
                "childPassword": "the correct password",
                "type": "TICKETMASTER",
            }
        }
    }
}

snapshots["test_events_and_event_groups_query_normal_user 1"] = {
    "data": {
        "eventsAndEventGroups": {
            "edges": [
                {"node": {"__typename": "EventNode", "name": "Published Event"}},
                {
                    "node": {
                        "__typename": "EventGroupNode",
                        "name": "Published EventGroup",
                    }
                },
            ]
        }
    }
}

snapshots[
    "test_events_and_event_groups_query_project_filtering First project in filter, permission to see both projects"
] = {
    "data": {
        "eventsAndEventGroups": {
            "edges": [
                {"node": {"__typename": "EventNode", "name": "The project's Event"}},
                {
                    "node": {
                        "__typename": "EventGroupNode",
                        "name": "The project's EventGroup",
                    }
                },
            ]
        }
    }
}

snapshots[
    "test_events_and_event_groups_query_project_filtering No filter, no permission to see another project"
] = {
    "data": {
        "eventsAndEventGroups": {
            "edges": [
                {"node": {"__typename": "EventNode", "name": "The project's Event"}},
                {
                    "node": {
                        "__typename": "EventGroupNode",
                        "name": "The project's EventGroup",
                    }
                },
            ]
        }
    }
}

snapshots[
    "test_events_and_event_groups_query_project_filtering No filter, permission to see both projects"
] = {
    "data": {
        "eventsAndEventGroups": {
            "edges": [
                {"node": {"__typename": "EventNode", "name": "The project's Event"}},
                {
                    "node": {
                        "__typename": "EventNode",
                        "name": "Another project's Event",
                    }
                },
                {
                    "node": {
                        "__typename": "EventGroupNode",
                        "name": "The project's EventGroup",
                    }
                },
                {
                    "node": {
                        "__typename": "EventGroupNode",
                        "name": "Another project's EventGroup",
                    }
                },
            ]
        }
    }
}

snapshots["test_events_and_event_groups_query_project_user 1"] = {
    "data": {
        "eventsAndEventGroups": {
            "edges": [
                {"node": {"__typename": "EventNode", "name": "I should be the first"}},
                {
                    "node": {
                        "__typename": "EventGroupNode",
                        "name": "I should be the in the middle",
                    }
                },
                {"node": {"__typename": "EventNode", "name": "I should be the last"}},
            ]
        }
    }
}

snapshots["test_events_and_event_groups_query_upcoming_filter[False] 1"] = {
    "data": {
        "eventsAndEventGroups": {
            "edges": [{"node": {"__typename": "EventNode", "name": "In the future"}}]
        }
    }
}

snapshots["test_events_and_event_groups_query_upcoming_filter[True] 1"] = {
    "data": {
        "eventsAndEventGroups": {
            "edges": [
                {"node": {"__typename": "EventGroupNode", "name": "In the future"}}
            ]
        }
    }
}

snapshots["test_events_query_normal_user 1"] = {
    "data": {
        "events": {
            "edges": [
                {
                    "node": {
                        "capacityPerOccurrence": 35,
                        "createdAt": "2020-12-12T00:00:00+00:00",
                        "description": """Least then top sing. Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                        "duration": 181,
                        "image": "http://testserver/media/teacher.jpg",
                        "imageAltText": "",
                        "name": "Poor lawyer treat free heart significant.",
                        "occurrences": {
                            "edges": [
                                {
                                    "node": {
                                        "enrolmentCount": 0,
                                        "remainingCapacity": 35,
                                        "ticketSystem": {"type": "INTERNAL"},
                                        "time": "1971-04-30T08:38:26+00:00",
                                        "venue": {
                                            "translations": [
                                                {
                                                    "description": "Later evening southern would according strong. Analysis season project executive entire.",
                                                    "languageCode": "FI",
                                                    "name": "Skill down subject town range north skin.",
                                                }
                                            ]
                                        },
                                    }
                                }
                            ]
                        },
                        "participantsPerInvite": "CHILD_AND_1_OR_2_GUARDIANS",
                        "project": {"year": 2020},
                        "publishedAt": "2020-12-12T00:00:00+00:00",
                        "shortDescription": "Together history perform.",
                        "ticketSystem": {"type": "INTERNAL"},
                        "translations": [
                            {
                                "description": """Least then top sing. Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                                "imageAltText": "",
                                "languageCode": "FI",
                                "name": "Poor lawyer treat free heart significant.",
                                "shortDescription": "Together history perform.",
                            }
                        ],
                        "updatedAt": "2020-12-12T00:00:00+00:00",
                    }
                }
            ]
        }
    }
}

snapshots["test_events_query_project_user 1"] = {
    "data": {
        "events": {
            "edges": [
                {
                    "node": {
                        "capacityPerOccurrence": 35,
                        "createdAt": "2020-12-12T00:00:00+00:00",
                        "description": """Least then top sing. Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                        "duration": 181,
                        "image": "http://testserver/media/teacher.jpg",
                        "imageAltText": "",
                        "name": "Poor lawyer treat free heart significant.",
                        "occurrences": {
                            "edges": [
                                {
                                    "node": {
                                        "enrolmentCount": 0,
                                        "remainingCapacity": 35,
                                        "ticketSystem": {"type": "INTERNAL"},
                                        "time": "2014-01-28T14:12:00+00:00",
                                        "venue": {
                                            "translations": [
                                                {
                                                    "description": "Training thought price. Effort clear and local challenge box. Care figure mention wrong when lead involve.",
                                                    "languageCode": "FI",
                                                    "name": "Land especially can quite industry relationship very.",
                                                }
                                            ]
                                        },
                                    }
                                }
                            ]
                        },
                        "participantsPerInvite": "CHILD_AND_1_OR_2_GUARDIANS",
                        "project": {"year": 2020},
                        "publishedAt": "2020-12-12T00:00:00+00:00",
                        "shortDescription": "Together history perform.",
                        "ticketSystem": {"type": "INTERNAL"},
                        "translations": [
                            {
                                "description": """Least then top sing. Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                                "imageAltText": "",
                                "languageCode": "FI",
                                "name": "Poor lawyer treat free heart significant.",
                                "shortDescription": "Together history perform.",
                            }
                        ],
                        "updatedAt": "2020-12-12T00:00:00+00:00",
                    }
                },
                {
                    "node": {
                        "capacityPerOccurrence": 49,
                        "createdAt": "2020-12-12T00:00:00+00:00",
                        "description": """Wonder everything pay parent theory go home. Book and interesting sit future dream party. Truth list pressure stage history.
If his their best. Election stay every something base.""",
                        "duration": 42,
                        "image": "http://testserver/media/us.jpg",
                        "imageAltText": "",
                        "name": "Skill down subject town range north skin.",
                        "occurrences": {
                            "edges": [
                                {
                                    "node": {
                                        "enrolmentCount": 0,
                                        "remainingCapacity": 49,
                                        "ticketSystem": {"type": "INTERNAL"},
                                        "time": "2001-12-31T04:39:12+00:00",
                                        "venue": {
                                            "translations": [
                                                {
                                                    "description": "Training thought price. Effort clear and local challenge box. Care figure mention wrong when lead involve.",
                                                    "languageCode": "FI",
                                                    "name": "Land especially can quite industry relationship very.",
                                                }
                                            ]
                                        },
                                    }
                                }
                            ]
                        },
                        "participantsPerInvite": "CHILD_AND_1_OR_2_GUARDIANS",
                        "project": {"year": 2020},
                        "publishedAt": None,
                        "shortDescription": "Later evening southern would according strong.",
                        "ticketSystem": {"type": "INTERNAL"},
                        "translations": [
                            {
                                "description": """Wonder everything pay parent theory go home. Book and interesting sit future dream party. Truth list pressure stage history.
If his their best. Election stay every something base.""",
                                "imageAltText": "",
                                "languageCode": "FI",
                                "name": "Skill down subject town range north skin.",
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

snapshots["test_import_ticket_system_passwords 1"] = {
    "data": {
        "importTicketSystemPasswords": {
            "errors": None,
            "event": {"name": "Poor lawyer treat free heart significant."},
            "passwords": ["123", "asd", "xyz321"],
        }
    }
}

snapshots["test_import_ticket_system_passwords_errors_with_integrity_errors 1"] = {
    "data": {
        "importTicketSystemPasswords": {
            "errors": {
                "passwords": [
                    ["Could not import password", "123"],
                    ["Could not import password", "asd"],
                    ["Could not import password", "xyz321"],
                ]
            },
            "event": {"name": "Poor lawyer treat free heart significant."},
            "passwords": ["more", "passwords", "to", "test", "errors"],
        }
    }
}

snapshots["test_occurrence_available_capacity_and_enrolment_count 1"] = {
    "data": {
        "occurrence": {
            "enrolmentCount": 3,
            "enrolments": {"edges": []},
            "event": {
                "capacityPerOccurrence": 9,
                "duration": 1,
                "image": "http://testserver/media/law.jpg",
                "participantsPerInvite": "FAMILY",
                "publishedAt": "2020-12-12T00:00:00+00:00",
                "translations": [
                    {
                        "description": "Able last in able local. Quite nearly gun two born land. Yeah trouble method yard campaign former model.",
                        "languageCode": "FI",
                        "name": "Always sport return student light a point.",
                        "shortDescription": "Who Mrs public east site chance.",
                    }
                ],
            },
            "occurrenceLanguage": "FI",
            "remainingCapacity": 6,
            "ticketSystem": {"type": "INTERNAL"},
            "time": "2020-12-12T00:00:00+00:00",
            "venue": {
                "translations": [
                    {
                        "accessibilityInfo": """Sit enter stand himself from daughter order. Sign discover eight.
Scientist service wonder everything pay. Moment strong hand push book and interesting sit.""",
                        "additionalInfo": "Training thought price. Effort clear and local challenge box. Care figure mention wrong when lead involve.",
                        "address": """04883 Mary Corner
Port Mikeview, IN 23956""",
                        "arrivalInstructions": "Benefit treat final central. Past ready join enjoy. Huge get this success commercial recently from.",
                        "description": """Together history perform. Respond draw military dog hospital number. Certainly again thought summer because serious listen.
Page box child care any concern. Defense level church use.""",
                        "languageCode": "FI",
                        "name": "Poor lawyer treat free heart significant.",
                        "wwwUrl": "http://www.brooks.com/",
                    }
                ]
            },
        }
    }
}

snapshots["test_occurrence_capacity[0-0] 1"] = {
    "data": {
        "occurrence": {
            "capacity": 0,
            "capacityOverride": 0,
            "enrolmentCount": 0,
            "remainingCapacity": 0,
        }
    }
}

snapshots["test_occurrence_capacity[5-0] 1"] = {
    "data": {
        "occurrence": {
            "capacity": 5,
            "capacityOverride": 5,
            "enrolmentCount": 0,
            "remainingCapacity": 5,
        }
    }
}

snapshots["test_occurrence_capacity[5-4] 1"] = {
    "data": {
        "occurrence": {
            "capacity": 5,
            "capacityOverride": 5,
            "enrolmentCount": 4,
            "remainingCapacity": 1,
        }
    }
}

snapshots["test_occurrence_capacity[5-5] 1"] = {
    "data": {
        "occurrence": {
            "capacity": 5,
            "capacityOverride": 5,
            "enrolmentCount": 5,
            "remainingCapacity": 0,
        }
    }
}

snapshots["test_occurrence_capacity[5-6] 1"] = {
    "data": {
        "occurrence": {
            "capacity": 5,
            "capacityOverride": 5,
            "enrolmentCount": 6,
            "remainingCapacity": 0,
        }
    }
}

snapshots["test_occurrence_capacity[None-0] 1"] = {
    "data": {
        "occurrence": {
            "capacity": 10,
            "capacityOverride": None,
            "enrolmentCount": 0,
            "remainingCapacity": 10,
        }
    }
}

snapshots["test_occurrence_capacity[None-10] 1"] = {
    "data": {
        "occurrence": {
            "capacity": 10,
            "capacityOverride": None,
            "enrolmentCount": 10,
            "remainingCapacity": 0,
        }
    }
}

snapshots["test_occurrence_capacity[None-11] 1"] = {
    "data": {
        "occurrence": {
            "capacity": 10,
            "capacityOverride": None,
            "enrolmentCount": 11,
            "remainingCapacity": 0,
        }
    }
}

snapshots["test_occurrence_capacity[None-9] 1"] = {
    "data": {
        "occurrence": {
            "capacity": 10,
            "capacityOverride": None,
            "enrolmentCount": 9,
            "remainingCapacity": 1,
        }
    }
}

snapshots["test_occurrence_query_normal_user 1"] = {
    "data": {
        "occurrence": {
            "enrolmentCount": 0,
            "enrolments": {"edges": []},
            "event": {
                "capacityPerOccurrence": 9,
                "duration": 1,
                "image": "http://testserver/media/law.jpg",
                "participantsPerInvite": "FAMILY",
                "publishedAt": "2020-12-12T00:00:00+00:00",
                "translations": [
                    {
                        "description": "Able last in able local. Quite nearly gun two born land. Yeah trouble method yard campaign former model.",
                        "languageCode": "FI",
                        "name": "Always sport return student light a point.",
                        "shortDescription": "Who Mrs public east site chance.",
                    }
                ],
            },
            "occurrenceLanguage": "FI",
            "remainingCapacity": 9,
            "ticketSystem": {"type": "INTERNAL"},
            "time": "2020-12-12T00:00:00+00:00",
            "venue": {
                "translations": [
                    {
                        "accessibilityInfo": """Sit enter stand himself from daughter order. Sign discover eight.
Scientist service wonder everything pay. Moment strong hand push book and interesting sit.""",
                        "additionalInfo": "Training thought price. Effort clear and local challenge box. Care figure mention wrong when lead involve.",
                        "address": """04883 Mary Corner
Port Mikeview, IN 23956""",
                        "arrivalInstructions": "Benefit treat final central. Past ready join enjoy. Huge get this success commercial recently from.",
                        "description": """Together history perform. Respond draw military dog hospital number. Certainly again thought summer because serious listen.
Page box child care any concern. Defense level church use.""",
                        "languageCode": "FI",
                        "name": "Poor lawyer treat free heart significant.",
                        "wwwUrl": "http://www.brooks.com/",
                    }
                ]
            },
        }
    }
}

snapshots["test_occurrence_ticket_system 1"] = {
    "data": {
        "occurrence": {
            "ticketSystem": {"type": "TICKETMASTER", "url": "https://example.com"}
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

snapshots["test_occurrences_filter_by_event 1"] = {
    "data": {
        "occurrences": {
            "edges": [
                {"node": {"time": "1970-01-01T12:00:00+00:00"}},
                {"node": {"time": "1970-01-01T12:00:00+00:00"}},
            ]
        }
    }
}

snapshots["test_occurrences_filter_by_language 1"] = {
    "data": {
        "occurrences": {
            "edges": [
                {"node": {"time": "2005-09-07T17:47:05+00:00"}},
                {"node": {"time": "2016-04-25T18:13:39+00:00"}},
            ]
        }
    }
}

snapshots["test_occurrences_filter_by_project 1"] = {
    "data": {
        "occurrences": {"edges": [{"node": {"time": "1970-01-01T12:00:00+00:00"}}]}
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

snapshots["test_occurrences_filter_by_upcoming_with_leeway[False] 1"] = {
    "data": {
        "occurrences": {
            "edges": [
                {"node": {"time": "2020-12-11T23:29:00+00:00"}},
                {"node": {"time": "2020-12-11T23:31:00+00:00"}},
            ]
        }
    }
}

snapshots["test_occurrences_filter_by_upcoming_with_leeway[True] 1"] = {
    "data": {
        "occurrences": {"edges": [{"node": {"time": "2020-12-11T23:31:00+00:00"}}]}
    }
}

snapshots["test_occurrences_filter_by_upcoming_with_ongoing[False] 1"] = {
    "data": {
        "occurrences": {
            "edges": [
                {"node": {"time": "2020-12-11T22:29:00+00:00"}},
                {"node": {"time": "2020-12-11T22:31:00+00:00"}},
            ]
        }
    }
}

snapshots["test_occurrences_filter_by_upcoming_with_ongoing[True] 1"] = {
    "data": {
        "occurrences": {"edges": [{"node": {"time": "2020-12-11T22:31:00+00:00"}}]}
    }
}

snapshots["test_occurrences_filter_by_venue 1"] = {
    "data": {
        "occurrences": {
            "edges": [
                {"node": {"time": "1998-11-25T00:15:59+00:00"}},
                {"node": {"time": "2016-01-01T13:37:17+00:00"}},
                {"node": {"time": "2018-03-30T01:34:27+00:00"}},
            ]
        }
    }
}

snapshots["test_occurrences_query_normal_user 1"] = {
    "data": {
        "occurrences": {
            "edges": [
                {
                    "node": {
                        "enrolmentCount": 0,
                        "event": {
                            "capacityPerOccurrence": 9,
                            "duration": 1,
                            "image": "http://testserver/media/law.jpg",
                            "participantsPerInvite": "FAMILY",
                            "publishedAt": "2020-12-12T00:00:00+00:00",
                            "translations": [
                                {
                                    "description": "Able last in able local. Quite nearly gun two born land. Yeah trouble method yard campaign former model.",
                                    "languageCode": "FI",
                                    "name": "Always sport return student light a point.",
                                    "shortDescription": "Who Mrs public east site chance.",
                                }
                            ],
                        },
                        "remainingCapacity": 9,
                        "ticketSystem": {"type": "INTERNAL"},
                        "time": "2020-12-12T00:00:00+00:00",
                        "venue": {
                            "translations": [
                                {
                                    "accessibilityInfo": """Sit enter stand himself from daughter order. Sign discover eight.
Scientist service wonder everything pay. Moment strong hand push book and interesting sit.""",
                                    "additionalInfo": "Training thought price. Effort clear and local challenge box. Care figure mention wrong when lead involve.",
                                    "address": """04883 Mary Corner
Port Mikeview, IN 23956""",
                                    "arrivalInstructions": "Benefit treat final central. Past ready join enjoy. Huge get this success commercial recently from.",
                                    "description": """Together history perform. Respond draw military dog hospital number. Certainly again thought summer because serious listen.
Page box child care any concern. Defense level church use.""",
                                    "languageCode": "FI",
                                    "name": "Poor lawyer treat free heart significant.",
                                    "wwwUrl": "http://www.brooks.com/",
                                }
                            ]
                        },
                    }
                }
            ]
        }
    }
}

snapshots["test_occurrences_query_project_user 1"] = {
    "data": {
        "occurrences": {
            "edges": [
                {
                    "node": {
                        "enrolmentCount": 0,
                        "event": {
                            "capacityPerOccurrence": 9,
                            "duration": 1,
                            "image": "http://testserver/media/law.jpg",
                            "participantsPerInvite": "FAMILY",
                            "publishedAt": "2020-12-12T00:00:00+00:00",
                            "translations": [
                                {
                                    "description": "Able last in able local. Quite nearly gun two born land. Yeah trouble method yard campaign former model.",
                                    "languageCode": "FI",
                                    "name": "Always sport return student light a point.",
                                    "shortDescription": "Who Mrs public east site chance.",
                                }
                            ],
                        },
                        "remainingCapacity": 9,
                        "ticketSystem": {"type": "INTERNAL"},
                        "time": "2020-12-12T00:00:00+00:00",
                        "venue": {
                            "translations": [
                                {
                                    "accessibilityInfo": """Sit enter stand himself from daughter order. Sign discover eight.
Scientist service wonder everything pay. Moment strong hand push book and interesting sit.""",
                                    "additionalInfo": "Training thought price. Effort clear and local challenge box. Care figure mention wrong when lead involve.",
                                    "address": """04883 Mary Corner
Port Mikeview, IN 23956""",
                                    "arrivalInstructions": "Benefit treat final central. Past ready join enjoy. Huge get this success commercial recently from.",
                                    "description": """Together history perform. Respond draw military dog hospital number. Certainly again thought summer because serious listen.
Page box child care any concern. Defense level church use.""",
                                    "languageCode": "FI",
                                    "name": "Poor lawyer treat free heart significant.",
                                    "wwwUrl": "http://www.brooks.com/",
                                }
                            ]
                        },
                    }
                },
                {
                    "node": {
                        "enrolmentCount": 0,
                        "event": {
                            "capacityPerOccurrence": 47,
                            "duration": 245,
                            "image": "http://testserver/media/answer.jpg",
                            "participantsPerInvite": "CHILD_AND_1_OR_2_GUARDIANS",
                            "publishedAt": None,
                            "translations": [
                                {
                                    "description": """Indeed discuss challenge school rule wish. Along hear follow sometimes.
Far magazine on summer.""",
                                    "languageCode": "FI",
                                    "name": "Notice rule huge realize at rather.",
                                    "shortDescription": "Once strong artist save decide listen.",
                                }
                            ],
                        },
                        "remainingCapacity": 47,
                        "ticketSystem": {"type": "INTERNAL"},
                        "time": "2020-12-12T06:00:00+00:00",
                        "venue": {
                            "translations": [
                                {
                                    "accessibilityInfo": """Sit enter stand himself from daughter order. Sign discover eight.
Scientist service wonder everything pay. Moment strong hand push book and interesting sit.""",
                                    "additionalInfo": "Training thought price. Effort clear and local challenge box. Care figure mention wrong when lead involve.",
                                    "address": """04883 Mary Corner
Port Mikeview, IN 23956""",
                                    "arrivalInstructions": "Benefit treat final central. Past ready join enjoy. Huge get this success commercial recently from.",
                                    "description": """Together history perform. Respond draw military dog hospital number. Certainly again thought summer because serious listen.
Page box child care any concern. Defense level church use.""",
                                    "languageCode": "FI",
                                    "name": "Poor lawyer treat free heart significant.",
                                    "wwwUrl": "http://www.brooks.com/",
                                }
                            ]
                        },
                    }
                },
            ]
        }
    }
}

snapshots["test_publish_event[model_perm] 1"] = {
    "data": {"publishEvent": {"event": {"publishedAt": "2020-12-12T00:00:00+00:00"}}}
}

snapshots["test_publish_event[object_perm] 1"] = {
    "data": {"publishEvent": {"event": {"publishedAt": "2020-12-12T00:00:00+00:00"}}}
}

snapshots["test_publish_event_group[model_perm] 1"] = {
    "data": {
        "publishEventGroup": {
            "eventGroup": {
                "events": {
                    "edges": [{"node": {"publishedAt": "2020-12-12T00:00:00+00:00"}}]
                },
                "publishedAt": "2020-12-12T00:00:00+00:00",
            }
        }
    }
}

snapshots["test_publish_event_group[object_perm] 1"] = {
    "data": {
        "publishEventGroup": {
            "eventGroup": {
                "events": {
                    "edges": [{"node": {"publishedAt": "2020-12-12T00:00:00+00:00"}}]
                },
                "publishedAt": "2020-12-12T00:00:00+00:00",
            }
        }
    }
}

snapshots["test_publish_ticketmaster_event[model_perm-False] 1"] = {
    "data": {"publishEvent": {"event": {"publishedAt": "2020-12-12T00:00:00+00:00"}}}
}

snapshots["test_publish_ticketmaster_event[object_perm-False] 1"] = {
    "data": {"publishEvent": {"event": {"publishedAt": "2020-12-12T00:00:00+00:00"}}}
}

snapshots["test_republish_event_group[model_perm-True] 1"] = {
    "data": {
        "publishEventGroup": {
            "eventGroup": {
                "events": {
                    "edges": [
                        {"node": {"publishedAt": "2020-12-11T00:00:00+00:00"}},
                        {"node": {"publishedAt": "2020-12-12T00:00:00+00:00"}},
                    ]
                },
                "publishedAt": "2020-12-12T00:00:00+00:00",
            }
        }
    }
}

snapshots["test_republish_event_group[object_perm-True] 1"] = {
    "data": {
        "publishEventGroup": {
            "eventGroup": {
                "events": {
                    "edges": [
                        {"node": {"publishedAt": "2020-12-11T00:00:00+00:00"}},
                        {"node": {"publishedAt": "2020-12-12T00:00:00+00:00"}},
                    ]
                },
                "publishedAt": "2020-12-12T00:00:00+00:00",
            }
        }
    }
}

snapshots["test_required_translation 1"] = {
    "data": {
        "addEvent": {
            "event": {
                "capacityPerOccurrence": 30,
                "duration": 1000,
                "image": "",
                "imageAltText": "Image alt text",
                "participantsPerInvite": "FAMILY",
                "project": {"year": 2020},
                "publishedAt": None,
                "readyForEventGroupPublishing": False,
                "ticketSystem": {"type": "INTERNAL"},
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

snapshots["test_set_enrolment_attendance[None] 1"] = {
    "data": {"setEnrolmentAttendance": {"enrolment": {"attended": None}}}
}

snapshots["test_set_enrolment_attendance[True] 1"] = {
    "data": {"setEnrolmentAttendance": {"enrolment": {"attended": True}}}
}

snapshots["test_unenrol_occurrence 1"] = {
    "data": {
        "unenrolOccurrence": {
            "child": {"firstName": "Robert"},
            "occurrence": {"time": "2020-12-12T00:00:00+00:00"},
        }
    }
}

snapshots["test_update_event_group[model_perm] 1"] = {
    "data": {
        "updateEventGroup": {
            "eventGroup": {
                "image": "teacher.jpg",
                "translations": [
                    {
                        "description": "desc",
                        "imageAltText": "Image alt text",
                        "languageCode": "FI",
                        "name": "Event group test in suomi",
                        "shortDescription": "Short desc",
                    },
                    {
                        "description": "desc",
                        "imageAltText": "Image alt text",
                        "languageCode": "SV",
                        "name": "Event group test in swedish",
                        "shortDescription": "Short desc",
                    },
                ],
            }
        }
    }
}

snapshots["test_update_event_group[object_perm] 1"] = {
    "data": {
        "updateEventGroup": {
            "eventGroup": {
                "image": "teacher.jpg",
                "translations": [
                    {
                        "description": "desc",
                        "imageAltText": "Image alt text",
                        "languageCode": "FI",
                        "name": "Event group test in suomi",
                        "shortDescription": "Short desc",
                    },
                    {
                        "description": "desc",
                        "imageAltText": "Image alt text",
                        "languageCode": "SV",
                        "name": "Event group test in swedish",
                        "shortDescription": "Short desc",
                    },
                ],
            }
        }
    }
}

snapshots["test_update_event_project_user 1"] = {
    "data": {
        "updateEvent": {
            "event": {
                "capacityPerOccurrence": 30,
                "duration": 1000,
                "image": "http://testserver/media/teacher.jpg",
                "imageAltText": "Image alt text",
                "occurrences": {"edges": []},
                "participantsPerInvite": "FAMILY",
                "readyForEventGroupPublishing": True,
                "ticketSystem": {"type": "INTERNAL"},
                "translations": [
                    {
                        "description": "desc",
                        "imageAltText": "Image alt text",
                        "languageCode": "FI",
                        "name": "Event test in suomi",
                        "shortDescription": "Short desc",
                    },
                    {
                        "description": "desc",
                        "imageAltText": "Image alt text",
                        "languageCode": "SV",
                        "name": "Event test in swedish",
                        "shortDescription": "Short desc",
                    },
                ],
            }
        }
    }
}

snapshots["test_update_event_ready_for_event_group_publishing 1"] = {
    "data": {
        "updateEvent": {
            "event": {
                "capacityPerOccurrence": 35,
                "duration": 181,
                "image": "http://testserver/media/teacher.jpg",
                "imageAltText": "",
                "occurrences": {"edges": []},
                "participantsPerInvite": "CHILD_AND_1_OR_2_GUARDIANS",
                "readyForEventGroupPublishing": True,
                "ticketSystem": {"type": "INTERNAL"},
                "translations": [
                    {
                        "description": """Least then top sing. Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                        "imageAltText": "",
                        "languageCode": "FI",
                        "name": "Poor lawyer treat free heart significant.",
                        "shortDescription": "Together history perform.",
                    }
                ],
            }
        }
    }
}

snapshots["test_update_internal_ticket_system_event_capacity_required 1"] = {
    "data": {
        "updateEvent": {
            "event": {
                "capacityPerOccurrence": 5,
                "duration": 181,
                "image": "http://testserver/media/teacher.jpg",
                "imageAltText": "",
                "occurrences": {"edges": []},
                "participantsPerInvite": "CHILD_AND_1_OR_2_GUARDIANS",
                "readyForEventGroupPublishing": True,
                "ticketSystem": {"type": "INTERNAL"},
                "translations": [
                    {
                        "description": """Least then top sing. Serious listen police shake. Page box child care any concern.
Agree room laugh prevent make. Our very television beat at success decade.""",
                        "imageAltText": "",
                        "languageCode": "FI",
                        "name": "Poor lawyer treat free heart significant.",
                        "shortDescription": "Together history perform.",
                    }
                ],
            }
        }
    }
}

snapshots["test_update_occurrence_different_year[True] 1"] = {
    "data": {
        "updateOccurrence": {
            "occurrence": {
                "capacity": 5,
                "capacityOverride": 5,
                "enrolmentCount": 0,
                "event": {"createdAt": "2020-12-12T00:00:00+00:00"},
                "occurrenceLanguage": "SV",
                "remainingCapacity": 5,
                "ticketSystem": {"type": "INTERNAL"},
                "time": "2021-12-12T00:00:00+00:00",
                "venue": {"createdAt": "2020-12-12T00:00:00+00:00"},
            }
        }
    }
}

snapshots["test_update_occurrence_project_user 1"] = {
    "data": {
        "updateOccurrence": {
            "occurrence": {
                "capacity": 5,
                "capacityOverride": 5,
                "enrolmentCount": 0,
                "event": {"createdAt": "2020-12-12T00:00:00+00:00"},
                "occurrenceLanguage": "SV",
                "remainingCapacity": 5,
                "ticketSystem": {"type": "INTERNAL"},
                "time": "1986-12-12T16:40:48+00:00",
                "venue": {"createdAt": "2020-12-12T00:00:00+00:00"},
            }
        }
    }
}

snapshots["test_update_occurrence_ticket_system_url[False-False] 1"] = {
    "data": {
        "updateOccurrence": {
            "occurrence": {
                "capacity": 5,
                "capacityOverride": 5,
                "enrolmentCount": 0,
                "event": {"createdAt": "2020-12-12T00:00:00+00:00"},
                "occurrenceLanguage": "SV",
                "remainingCapacity": 5,
                "ticketSystem": {
                    "type": "TICKETMASTER",
                    "url": "https://updated.example.com",
                },
                "time": "1986-12-12T16:40:48+00:00",
                "venue": {"createdAt": "2020-12-12T00:00:00+00:00"},
            }
        }
    }
}

snapshots["test_update_occurrence_ticket_system_url[False-True] 1"] = {
    "data": {
        "updateOccurrence": {
            "occurrence": {
                "capacity": 5,
                "capacityOverride": 5,
                "enrolmentCount": 0,
                "event": {"createdAt": "2020-12-12T00:00:00+00:00"},
                "occurrenceLanguage": "SV",
                "remainingCapacity": 5,
                "ticketSystem": {"type": "TICKETMASTER", "url": ""},
                "time": "1986-12-12T16:40:48+00:00",
                "venue": {"createdAt": "2020-12-12T00:00:00+00:00"},
            }
        }
    }
}

snapshots["test_update_occurrence_ticket_system_url[True-False] 1"] = {
    "data": {
        "updateOccurrence": {
            "occurrence": {
                "capacity": 5,
                "capacityOverride": 5,
                "enrolmentCount": 0,
                "event": {"createdAt": "2020-12-12T00:00:00+00:00"},
                "occurrenceLanguage": "SV",
                "remainingCapacity": 5,
                "ticketSystem": {
                    "type": "TICKETMASTER",
                    "url": "https://updated.example.com",
                },
                "time": "1986-12-12T16:40:48+00:00",
                "venue": {"createdAt": "2020-12-12T00:00:00+00:00"},
            }
        }
    }
}

snapshots["test_update_ticketmaster_event[False] 1"] = {
    "data": {"updateEvent": {"event": {"ticketSystem": {"type": "TICKETMASTER"}}}}
}

snapshots["test_verify_invalid_ticket 1"] = {
    "data": {
        "verifyTicket": {
            "eventName": "Record card my. Sure sister return.",
            "occurrenceTime": "2020-12-11T00:00:00+00:00",
            "validity": False,
            "venueName": "Remember stay public high concern glass person.",
        }
    }
}

snapshots["test_verify_valid_ticket 1"] = {
    "data": {
        "verifyTicket": {
            "eventName": "Record card my. Sure sister return.",
            "occurrenceTime": "2020-12-12T00:00:00+00:00",
            "validity": True,
            "venueName": "Remember stay public high concern glass person.",
        }
    }
}
