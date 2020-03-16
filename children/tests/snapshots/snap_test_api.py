# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_child_query 1"] = {
    "data": {
        "child": {
            "birthdate": "2020-09-07",
            "firstName": "John",
            "lastName": "Terrell",
            "postalCode": "77671",
            "relationships": {
                "edges": [
                    {
                        "node": {
                            "guardian": {
                                "email": "mperez@cox.com",
                                "firstName": "Gregory",
                                "lastName": "Cross",
                                "phoneNumber": "750-649-7638x0346",
                            },
                            "type": "OTHER_GUARDIAN",
                        }
                    }
                ]
            },
        }
    }
}

snapshots["test_children_query_normal_user 1"] = {
    "data": {
        "children": {
            "edges": [
                {
                    "node": {
                        "birthdate": "2020-03-01",
                        "firstName": "Jason",
                        "lastName": "Owens",
                        "postalCode": "70898",
                        "relationships": {
                            "edges": [
                                {
                                    "node": {
                                        "guardian": {
                                            "email": "mperez@cox.com",
                                            "firstName": "Selena",
                                            "lastName": "Roy",
                                            "phoneNumber": "123-447-4468",
                                        },
                                        "type": "OTHER_RELATION",
                                    }
                                }
                            ]
                        },
                    }
                }
            ]
        }
    }
}

snapshots["test_children_query_staff_user 1"] = {
    "data": {
        "children": {
            "edges": [
                {
                    "node": {
                        "birthdate": "2020-03-01",
                        "firstName": "Jason",
                        "lastName": "Owens",
                        "postalCode": "70898",
                        "relationships": {
                            "edges": [
                                {
                                    "node": {
                                        "guardian": {
                                            "email": "mperez@cox.com",
                                            "firstName": "Selena",
                                            "lastName": "Roy",
                                            "phoneNumber": "123-447-4468",
                                        },
                                        "type": "OTHER_RELATION",
                                    }
                                }
                            ]
                        },
                    }
                },
                {
                    "node": {
                        "birthdate": "2020-09-07",
                        "firstName": "John",
                        "lastName": "Terrell",
                        "postalCode": "77671",
                        "relationships": {
                            "edges": [
                                {
                                    "node": {
                                        "guardian": {
                                            "email": "kelly76@allen.com",
                                            "firstName": "Ashley",
                                            "lastName": "Castillo",
                                            "phoneNumber": "(117)159-1023x202",
                                        },
                                        "type": "OTHER_RELATION",
                                    }
                                }
                            ]
                        },
                    }
                },
            ]
        }
    }
}

snapshots["test_add_child_mutation 1"] = {
    "data": {
        "addChild": {
            "child": {
                "birthdate": "2020-11-11",
                "firstName": "Pekka",
                "lastName": "Perälä",
                "postalCode": "00820",
            }
        }
    }
}

snapshots["test_update_child_mutation 1"] = {
    "data": {
        "updateChild": {
            "child": {
                "birthdate": "2020-01-01",
                "firstName": "Matti",
                "lastName": "Mainio",
                "postalCode": "00840",
            }
        }
    }
}

snapshots["test_delete_child_mutation 1"] = {
    "data": {"deleteChild": {"__typename": "DeleteChildMutationPayload"}}
}

snapshots["test_child_query_not_own_child_staff_user 1"] = {
    "data": {
        "child": {
            "birthdate": "2020-09-07",
            "firstName": "John",
            "lastName": "Terrell",
            "postalCode": "77671",
            "relationships": {
                "edges": [
                    {
                        "node": {
                            "guardian": {
                                "email": "kelly76@allen.com",
                                "firstName": "Ashley",
                                "lastName": "Castillo",
                                "phoneNumber": "(117)159-1023x202",
                            },
                            "type": "OTHER_RELATION",
                        }
                    }
                ]
            },
        }
    }
}

snapshots["test_submit_children_and_guardian 1"] = {
    "data": {
        "submitChildrenAndGuardian": {
            "children": [
                {
                    "birthdate": "2020-01-01",
                    "firstName": "Matti",
                    "lastName": "Mainio",
                    "postalCode": "00840",
                    "relationships": {
                        "edges": [
                            {
                                "node": {
                                    "guardian": {
                                        "email": "mperez@cox.com",
                                        "firstName": "Gulle",
                                        "lastName": "Guardian",
                                        "phoneNumber": "777-777777",
                                    },
                                    "type": "OTHER_GUARDIAN",
                                }
                            }
                        ]
                    },
                },
                {
                    "birthdate": "2020-02-02",
                    "firstName": "Jussi",
                    "lastName": "Juonio",
                    "postalCode": "00820",
                    "relationships": {
                        "edges": [
                            {
                                "node": {
                                    "guardian": {
                                        "email": "mperez@cox.com",
                                        "firstName": "Gulle",
                                        "lastName": "Guardian",
                                        "phoneNumber": "777-777777",
                                    },
                                    "type": None,
                                }
                            }
                        ]
                    },
                },
            ],
            "guardian": {
                "email": "mperez@cox.com",
                "firstName": "Gulle",
                "lastName": "Guardian",
                "phoneNumber": "777-777777",
            },
        }
    }
}

snapshots["test_update_child_mutation_should_have_no_required_fields 1"] = {
    "data": {
        "updateChild": {
            "child": {
                "birthdate": "2020-09-05",
                "firstName": "Katherine",
                "lastName": "Wells",
                "postalCode": "15910",
            }
        }
    }
}

snapshots["test_get_available_events 1"] = {
    "data": {
        "child": {
            "availableEvents": {
                "edges": [
                    {
                        "node": {
                            "createdAt": "2020-12-12T00:00:00+00:00",
                            "occurrences": {
                                "edges": [{"node": {"remainingCapacity": 4}}]
                            },
                        }
                    }
                ]
            },
            "occurrences": {"edges": [{"node": {"time": "2020-12-12T00:00:00+00:00"}}]},
            "pastEvents": {"edges": []},
        }
    }
}

snapshots["test_get_past_events 1"] = {
    "data": {
        "child": {
            "availableEvents": {"edges": []},
            "occurrences": {"edges": [{"node": {"time": "1969-12-31T22:20:00+00:00"}}]},
            "pastEvents": {
                "edges": [
                    {
                        "node": {
                            "createdAt": "2020-12-12T00:00:00+00:00",
                            "occurrences": {
                                "edges": [{"node": {"remainingCapacity": 5}}]
                            },
                        }
                    }
                ]
            },
        }
    }
}
