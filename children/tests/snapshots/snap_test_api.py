# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_active_internal_and_ticketmaster_enrolments 1'] = {
    'data': {
        'child': {
            'activeInternalAndTicketSystemEnrolments': {
                'edges': [
                    {
                        'node': {
                            '__typename': 'TicketmasterEnrolmentNode',
                            'createdAt': '2020-12-12T00:00:00+00:00',
                            'event': {
                                'name': '1/5'
                            }
                        }
                    },
                    {
                        'node': {
                            '__typename': 'EnrolmentNode',
                            'occurrence': {
                                'event': {
                                    'name': '2/5'
                                }
                            }
                        }
                    },
                    {
                        'node': {
                            '__typename': 'TicketmasterEnrolmentNode',
                            'createdAt': '2020-12-12T00:00:00+00:00',
                            'event': {
                                'name': '3/5'
                            }
                        }
                    },
                    {
                        'node': {
                            '__typename': 'EnrolmentNode',
                            'occurrence': {
                                'event': {
                                    'name': '4/5'
                                }
                            }
                        }
                    },
                    {
                        'node': {
                            '__typename': 'TicketmasterEnrolmentNode',
                            'createdAt': '2020-12-12T00:00:00+00:00',
                            'event': {
                                'name': '5/5'
                            }
                        }
                    }
                ]
            }
        }
    }
}

snapshots['test_add_child_mutation 1'] = {
    'data': {
        'addChild': {
            'child': {
                'birthyear': 2020,
                'name': 'Pekka',
                'postalCode': '00820'
            }
        }
    }
}

snapshots['test_available_events_and_event_groups 1'] = {
    'data': {
        'child': {
            'availableEventsAndEventGroups': {
                'edges': [
                    {
                        'node': {
                            '__typename': 'EventGroupNode',
                            'name': 'this should be the first'
                        }
                    },
                    {
                        'node': {
                            '__typename': 'EventNode',
                            'name': 'this should be the second'
                        }
                    },
                    {
                        'node': {
                            '__typename': 'EventGroupNode',
                            'name': 'this should be the third'
                        }
                    },
                    {
                        'node': {
                            '__typename': 'EventNode',
                            'name': 'this should be the fourth'
                        }
                    }
                ]
            }
        }
    }
}

snapshots['test_child_query 1'] = {
    'data': {
        'child': {
            'birthyear': 2019,
            'name': 'Richard Hayes',
            'postalCode': '57776',
            'relationships': {
                'edges': [
                    {
                        'node': {
                            'guardian': {
                                'email': 'michellewalker@example.net',
                                'firstName': 'Denise',
                                'lastName': 'Thompson',
                                'phoneNumber': '001-206-575-0649x7638'
                            },
                            'type': 'OTHER_RELATION'
                        }
                    }
                ]
            }
        }
    }
}

snapshots['test_child_query_not_own_child_project_user 1'] = {
    'data': {
        'child': {
            'birthyear': 2019,
            'name': 'Richard Hayes',
            'postalCode': '57776',
            'relationships': {
                'edges': [
                    {
                        'node': {
                            'guardian': {
                                'email': 'blake64@example.net',
                                'firstName': 'Timothy',
                                'lastName': 'Baldwin',
                                'phoneNumber': '480.934.6697'
                            },
                            'type': 'PARENT'
                        }
                    }
                ]
            }
        }
    }
}

snapshots['test_children_offset_pagination[10-None] 1'] = {
    'data': {
        'children': {
            'edges': [
                {
                    'node': {
                        'name': '1'
                    }
                },
                {
                    'node': {
                        'name': '2'
                    }
                },
                {
                    'node': {
                        'name': '3'
                    }
                },
                {
                    'node': {
                        'name': '4'
                    }
                },
                {
                    'node': {
                        'name': '5'
                    }
                }
            ]
        }
    }
}

snapshots['test_children_offset_pagination[2-2] 1'] = {
    'data': {
        'children': {
            'edges': [
                {
                    'node': {
                        'name': '3'
                    }
                },
                {
                    'node': {
                        'name': '4'
                    }
                }
            ]
        }
    }
}

snapshots['test_children_offset_pagination[2-None] 1'] = {
    'data': {
        'children': {
            'edges': [
                {
                    'node': {
                        'name': '1'
                    }
                },
                {
                    'node': {
                        'name': '2'
                    }
                }
            ]
        }
    }
}

snapshots['test_children_offset_pagination[None-2] 1'] = {
    'data': {
        'children': {
            'edges': [
                {
                    'node': {
                        'name': '3'
                    }
                },
                {
                    'node': {
                        'name': '4'
                    }
                },
                {
                    'node': {
                        'name': '5'
                    }
                }
            ]
        }
    }
}

snapshots['test_children_offset_pagination[None-5] 1'] = {
    'data': {
        'children': {
            'edges': [
            ]
        }
    }
}

snapshots['test_children_project_filter 1'] = {
    'data': {
        'children': {
            'edges': [
                {
                    'node': {
                        'name': 'Only I should be returned'
                    }
                }
            ]
        }
    }
}

snapshots['test_children_query_ordering 1'] = {
    'data': {
        'children': {
            'edges': [
                {
                    'node': {
                        'createdAt': '2020-11-11T00:00:00+00:00',
                        'name': ''
                    }
                },
                {
                    'node': {
                        'createdAt': '2020-12-12T00:00:00+00:00',
                        'name': ''
                    }
                },
                {
                    'node': {
                        'createdAt': '2020-12-12T00:00:00+00:00',
                        'name': 'Alpha'
                    }
                },
                {
                    'node': {
                        'createdAt': '2020-12-12T00:00:00+00:00',
                        'name': 'Bravo'
                    }
                },
                {
                    'node': {
                        'createdAt': '2020-12-12T00:00:00+00:00',
                        'name': 'Bravo'
                    }
                },
                {
                    'node': {
                        'createdAt': '2020-11-11T00:00:00+00:00',
                        'name': 'Charlie'
                    }
                },
                {
                    'node': {
                        'createdAt': '2020-12-12T00:00:00+00:00',
                        'name': 'Charlie'
                    }
                },
                {
                    'node': {
                        'createdAt': '2020-12-12T00:00:00+00:00',
                        'name': 'Delta'
                    }
                }
            ]
        }
    }
}

snapshots['test_children_query_project_user_with_global_view_families_perm 1'] = {
    'data': {
        'children': {
            'edges': [
                {
                    'node': {
                        'birthyear': 2020,
                        'name': 'Same project - Should be returned 1/1',
                        'postalCode': '73557',
                        'relationships': {
                            'edges': [
                                {
                                    'node': {
                                        'guardian': {
                                            'email': 'funderwood@example.com',
                                            'firstName': 'Blake',
                                            'lastName': 'Newton',
                                            'phoneNumber': '497-963-8034x6697'
                                        },
                                        'type': 'PARENT'
                                    }
                                }
                            ]
                        }
                    }
                }
            ]
        }
    }
}

snapshots['test_children_total_count[None] 1'] = {
    'data': {
        'children': {
            'count': 5
        }
    }
}

snapshots['test_children_total_count[first] 1'] = {
    'data': {
        'children': {
            'count': 5
        }
    }
}

snapshots['test_children_total_count[limit] 1'] = {
    'data': {
        'children': {
            'count': 5
        }
    }
}

snapshots['test_delete_child_mutation 1'] = {
    'data': {
        'deleteChild': {
            '__typename': 'DeleteChildMutationPayload'
        }
    }
}

snapshots['test_get_available_events 1'] = {
    'data': {
        'child': {
            'availableEvents': {
                'edges': [
                    {
                        'node': {
                            'createdAt': '2020-12-12T00:00:00+00:00',
                            'occurrences': {
                                'edges': [
                                    {
                                        'node': {
                                            'remainingCapacity': 46
                                        }
                                    }
                                ]
                            }
                        }
                    }
                ]
            },
            'occurrences': {
                'edges': [
                    {
                        'node': {
                            'time': '2020-12-12T00:00:00+00:00'
                        }
                    }
                ]
            },
            'pastEvents': {
                'edges': [
                ]
            }
        }
    }
}

snapshots['test_get_past_events 1'] = {
    'data': {
        'child': {
            'availableEvents': {
                'edges': [
                ]
            },
            'occurrences': {
                'edges': [
                    {
                        'node': {
                            'time': '2020-12-11T22:59:00+00:00'
                        }
                    },
                    {
                        'node': {
                            'time': '2020-12-11T23:01:00+00:00'
                        }
                    }
                ]
            },
            'pastEvents': {
                'edges': [
                    {
                        'node': {
                            'createdAt': '2020-12-12T00:00:00+00:00',
                            'name': 'enrolled occurrence in the past',
                            'occurrences': {
                                'edges': [
                                    {
                                        'node': {
                                            'remainingCapacity': 12
                                        }
                                    },
                                    {
                                        'node': {
                                            'remainingCapacity': 13
                                        }
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        }
    }
}

snapshots['test_get_past_events_including_external_ticket_system_events 1'] = {
    'data': {
        'child': {
            'pastEvents': {
                'edges': [
                    {
                        'node': {
                            'name': 'Expected as 1/4'
                        }
                    },
                    {
                        'node': {
                            'name': 'Expected as 2/4'
                        }
                    },
                    {
                        'node': {
                            'name': 'Expected as 3/4'
                        }
                    },
                    {
                        'node': {
                            'name': 'Expected as 4/4'
                        }
                    }
                ]
            }
        }
    }
}

snapshots['test_submit_children_and_guardian 1'] = {
    'data': {
        'submitChildrenAndGuardian': {
            'children': [
                {
                    'birthyear': 2020,
                    'name': 'Matti',
                    'postalCode': '00840',
                    'relationships': {
                        'edges': [
                            {
                                'node': {
                                    'guardian': {
                                        'email': 'michellewalker@example.net',
                                        'firstName': 'Gulle',
                                        'lastName': 'Guardian',
                                        'phoneNumber': '777-777777'
                                    },
                                    'type': 'OTHER_GUARDIAN'
                                }
                            }
                        ]
                    }
                },
                {
                    'birthyear': 2020,
                    'name': 'Jussi',
                    'postalCode': '00820',
                    'relationships': {
                        'edges': [
                            {
                                'node': {
                                    'guardian': {
                                        'email': 'michellewalker@example.net',
                                        'firstName': 'Gulle',
                                        'lastName': 'Guardian',
                                        'phoneNumber': '777-777777'
                                    },
                                    'type': None
                                }
                            }
                        ]
                    }
                }
            ],
            'guardian': {
                'email': 'michellewalker@example.net',
                'firstName': 'Gulle',
                'languagesSpokenAtHome': {
                    'edges': [
                        {
                            'node': {
                                'alpha3Code': 'swe'
                            }
                        },
                        {
                            'node': {
                                'alpha3Code': 'fin'
                            }
                        }
                    ]
                },
                'lastName': 'Guardian',
                'phoneNumber': '777-777777'
            }
        }
    }
}

snapshots['test_submit_children_and_guardian_with_falsy_email[None] 1'] = {
    'data': {
        'submitChildrenAndGuardian': {
            'children': [
                {
                    'birthyear': 2020,
                    'name': 'Matti',
                    'postalCode': '00840',
                    'relationships': {
                        'edges': [
                            {
                                'node': {
                                    'guardian': {
                                        'email': 'michellewalker@example.net',
                                        'firstName': 'Gulle',
                                        'lastName': 'Guardian',
                                        'phoneNumber': '777-777777'
                                    },
                                    'type': 'OTHER_GUARDIAN'
                                }
                            }
                        ]
                    }
                },
                {
                    'birthyear': 2020,
                    'name': 'Jussi',
                    'postalCode': '00820',
                    'relationships': {
                        'edges': [
                            {
                                'node': {
                                    'guardian': {
                                        'email': 'michellewalker@example.net',
                                        'firstName': 'Gulle',
                                        'lastName': 'Guardian',
                                        'phoneNumber': '777-777777'
                                    },
                                    'type': None
                                }
                            }
                        ]
                    }
                }
            ],
            'guardian': {
                'email': 'michellewalker@example.net',
                'firstName': 'Gulle',
                'languagesSpokenAtHome': {
                    'edges': [
                    ]
                },
                'lastName': 'Guardian',
                'phoneNumber': '777-777777'
            }
        }
    }
}

snapshots['test_submit_children_and_guardian_with_falsy_email[] 1'] = {
    'data': {
        'submitChildrenAndGuardian': {
            'children': [
                {
                    'birthyear': 2020,
                    'name': 'Matti',
                    'postalCode': '00840',
                    'relationships': {
                        'edges': [
                            {
                                'node': {
                                    'guardian': {
                                        'email': 'michellewalker@example.net',
                                        'firstName': 'Gulle',
                                        'lastName': 'Guardian',
                                        'phoneNumber': '777-777777'
                                    },
                                    'type': 'OTHER_GUARDIAN'
                                }
                            }
                        ]
                    }
                },
                {
                    'birthyear': 2020,
                    'name': 'Jussi',
                    'postalCode': '00820',
                    'relationships': {
                        'edges': [
                            {
                                'node': {
                                    'guardian': {
                                        'email': 'michellewalker@example.net',
                                        'firstName': 'Gulle',
                                        'lastName': 'Guardian',
                                        'phoneNumber': '777-777777'
                                    },
                                    'type': None
                                }
                            }
                        ]
                    }
                }
            ],
            'guardian': {
                'email': 'michellewalker@example.net',
                'firstName': 'Gulle',
                'languagesSpokenAtHome': {
                    'edges': [
                    ]
                },
                'lastName': 'Guardian',
                'phoneNumber': '777-777777'
            }
        }
    }
}

snapshots['test_submit_children_and_guardian_with_user_email 1'] = {
    'data': {
        'submitChildrenAndGuardian': {
            'children': [
                {
                    'birthyear': 2020,
                    'name': 'Matti',
                    'postalCode': '00840',
                    'relationships': {
                        'edges': [
                            {
                                'node': {
                                    'guardian': {
                                        'email': 'michellewalker@example.net',
                                        'firstName': 'Gulle',
                                        'lastName': 'Guardian',
                                        'phoneNumber': '777-777777'
                                    },
                                    'type': 'OTHER_GUARDIAN'
                                }
                            }
                        ]
                    }
                },
                {
                    'birthyear': 2020,
                    'name': 'Jussi',
                    'postalCode': '00820',
                    'relationships': {
                        'edges': [
                            {
                                'node': {
                                    'guardian': {
                                        'email': 'michellewalker@example.net',
                                        'firstName': 'Gulle',
                                        'lastName': 'Guardian',
                                        'phoneNumber': '777-777777'
                                    },
                                    'type': None
                                }
                            }
                        ]
                    }
                }
            ],
            'guardian': {
                'email': 'michellewalker@example.net',
                'firstName': 'Gulle',
                'languagesSpokenAtHome': {
                    'edges': [
                    ]
                },
                'lastName': 'Guardian',
                'phoneNumber': '777-777777'
            }
        }
    }
}

snapshots['test_submit_children_and_guardian_without_email 1'] = {
    'data': {
        'submitChildrenAndGuardian': {
            'children': [
                {
                    'birthyear': 2020,
                    'name': 'Matti',
                    'postalCode': '00840',
                    'relationships': {
                        'edges': [
                            {
                                'node': {
                                    'guardian': {
                                        'email': 'michellewalker@example.net',
                                        'firstName': 'Gulle',
                                        'lastName': 'Guardian',
                                        'phoneNumber': '777-777777'
                                    },
                                    'type': 'OTHER_GUARDIAN'
                                }
                            }
                        ]
                    }
                },
                {
                    'birthyear': 2020,
                    'name': 'Jussi',
                    'postalCode': '00820',
                    'relationships': {
                        'edges': [
                            {
                                'node': {
                                    'guardian': {
                                        'email': 'michellewalker@example.net',
                                        'firstName': 'Gulle',
                                        'lastName': 'Guardian',
                                        'phoneNumber': '777-777777'
                                    },
                                    'type': None
                                }
                            }
                        ]
                    }
                }
            ],
            'guardian': {
                'email': 'michellewalker@example.net',
                'firstName': 'Gulle',
                'languagesSpokenAtHome': {
                    'edges': [
                    ]
                },
                'lastName': 'Guardian',
                'phoneNumber': '777-777777'
            }
        }
    }
}

snapshots['test_upcoming_events_and_event_groups 1'] = {
    'data': {
        'child': {
            'upcomingEventsAndEventGroups': {
                'edges': [
                    {
                        'node': {
                            '__typename': 'EventGroupNode',
                            'canChildEnroll': True,
                            'name': 'This should be the 1/8'
                        }
                    },
                    {
                        'node': {
                            '__typename': 'EventNode',
                            'canChildEnroll': True,
                            'name': 'This should be 2/8'
                        }
                    },
                    {
                        'node': {
                            '__typename': 'EventNode',
                            'canChildEnroll': True,
                            'name': 'This should be 3/8'
                        }
                    },
                    {
                        'node': {
                            '__typename': 'EventNode',
                            'canChildEnroll': True,
                            'name': 'This should be 4/8'
                        }
                    },
                    {
                        'node': {
                            '__typename': 'EventNode',
                            'canChildEnroll': True,
                            'name': 'This should be 5/8'
                        }
                    },
                    {
                        'node': {
                            '__typename': 'EventGroupNode',
                            'canChildEnroll': True,
                            'name': 'This should be 6/8'
                        }
                    },
                    {
                        'node': {
                            '__typename': 'EventNode',
                            'canChildEnroll': False,
                            'name': 'This should be 7/8'
                        }
                    },
                    {
                        'node': {
                            '__typename': 'EventGroupNode',
                            'canChildEnroll': False,
                            'name': 'This should be 8/8'
                        }
                    }
                ]
            }
        }
    }
}

snapshots['test_update_child_mutation 1'] = {
    'data': {
        'updateChild': {
            'child': {
                'birthyear': 2021,
                'name': 'Matti',
                'postalCode': '00840'
            }
        }
    }
}

snapshots['test_update_child_mutation_should_have_no_required_fields 1'] = {
    'data': {
        'updateChild': {
            'child': {
                'birthyear': 2021,
                'name': 'Derek Perry',
                'postalCode': '70117'
            }
        }
    }
}
