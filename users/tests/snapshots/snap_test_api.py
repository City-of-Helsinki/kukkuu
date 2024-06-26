# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_guardians_query_normal_user 1"] = {
    "data": {
        "guardians": {
            "edges": [
                {
                    "node": {
                        "email": "michellewalker@example.net",
                        "firstName": "Steve",
                        "lastName": "Hutchinson",
                        "phoneNumber": "001-117-159-1023x20281",
                        "relationships": {
                            "edges": [
                                {
                                    "node": {
                                        "child": {
                                            "birthyear": 2023,
                                            "name": "John Moore",
                                            "project": {"year": 2020},
                                        },
                                        "type": "PARENT",
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

snapshots["test_guardians_query_project_user 1"] = {
    "data": {
        "guardians": {
            "edges": [
                {
                    "node": {
                        "email": "debbie77@example.com",
                        "firstName": "Guardian having children in own and another project",
                        "lastName": "Should be visible 1/2",
                        "phoneNumber": "(712)406-7506x4976",
                        "relationships": {
                            "edges": [
                                {
                                    "node": {
                                        "child": {
                                            "birthyear": 2019,
                                            "name": "Cynthia Holmes",
                                            "project": {"year": 2020},
                                        },
                                        "type": "PARENT",
                                    }
                                }
                            ]
                        },
                    }
                },
                {
                    "node": {
                        "email": "michellewalker@example.net",
                        "firstName": "Another project own guardian",
                        "lastName": "Should be visible 2/2",
                        "phoneNumber": "202.813.0727",
                        "relationships": {
                            "edges": [
                                {
                                    "node": {
                                        "child": {
                                            "birthyear": 2022,
                                            "name": "Sara Johnson",
                                            "project": {"year": 2030},
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

snapshots["test_my_admin_profile_project_admin[has_also_model_perm] 1"] = {
    "data": {
        "myAdminProfile": {
            "projects": {
                "edges": [
                    {
                        "node": {
                            "myPermissions": {
                                "manageEventGroups": True,
                                "publish": True,
                            },
                            "name": "Helsingin kaupunginorkesteri",
                        }
                    },
                    {
                        "node": {
                            "myPermissions": {
                                "manageEventGroups": True,
                                "publish": True,
                            },
                            "name": "project where base admin object perm but no other object perms",
                        }
                    },
                    {
                        "node": {
                            "myPermissions": {
                                "manageEventGroups": True,
                                "publish": True,
                            },
                            "name": "project where base admin object perm and other object perms",
                        }
                    },
                    {
                        "node": {
                            "myPermissions": {
                                "manageEventGroups": True,
                                "publish": True,
                            },
                            "name": "project where no object perms",
                        }
                    },
                ]
            }
        }
    }
}

snapshots["test_my_admin_profile_project_admin[no_model_perm] 1"] = {
    "data": {
        "myAdminProfile": {
            "projects": {
                "edges": [
                    {
                        "node": {
                            "myPermissions": {
                                "manageEventGroups": False,
                                "publish": False,
                            },
                            "name": "project where base admin object perm but no other object perms",
                        }
                    },
                    {
                        "node": {
                            "myPermissions": {
                                "manageEventGroups": True,
                                "publish": True,
                            },
                            "name": "project where base admin object perm and other object perms",
                        }
                    },
                ]
            }
        }
    }
}

snapshots["test_my_communication_subscriptions_query_as_logged_in[False] 1"] = {
    "data": {
        "myCommunicationSubscriptions": {
            "firstName": "Michael",
            "hasAcceptedCommunication": False,
            "language": "fi",
            "lastName": "Patton",
        }
    }
}

snapshots["test_my_communication_subscriptions_query_as_logged_in[True] 1"] = {
    "data": {
        "myCommunicationSubscriptions": {
            "firstName": "Michael",
            "hasAcceptedCommunication": True,
            "language": "fi",
            "lastName": "Patton",
        }
    }
}

snapshots[
    "test_my_communication_subscriptions_query_with_auth_verification_token 1"
] = {
    "data": {
        "myCommunicationSubscriptions": {
            "firstName": "Michael",
            "hasAcceptedCommunication": True,
            "language": "fi",
            "lastName": "Patton",
        }
    }
}

snapshots["test_my_profile_no_profile 1"] = {"data": {"myProfile": None}}

snapshots["test_my_profile_query 1"] = {
    "data": {
        "myProfile": {
            "email": "michellewalker@example.net",
            "firstName": "Timothy",
            "hasAcceptedCommunication": False,
            "language": "FI",
            "languagesSpokenAtHome": {"edges": []},
            "lastName": "Baldwin",
            "phoneNumber": "803.466.9727",
            "relationships": {
                "edges": [
                    {
                        "node": {
                            "child": {
                                "birthyear": 2018,
                                "name": "Stephen Charles",
                                "postalCode": "71591",
                            },
                            "type": "OTHER_GUARDIAN",
                        }
                    }
                ]
            },
        }
    }
}

snapshots["test_my_profile_query_email[] 1"] = {
    "data": {"myProfile": {"email": "user@example.com"}}
}

snapshots["test_my_profile_query_email[guardian@example.com] 1"] = {
    "data": {"myProfile": {"email": "guardian@example.com"}}
}

snapshots["test_request_email_change_token_mutation 1"] = {
    "data": {
        "requestEmailUpdateToken": {
            "email": "new-email@kummilapset.fi",
            "emailUpdateTokenRequested": True,
        }
    }
}

snapshots["test_update_my_communication_subscriptions_as_logged_in[False] 1"] = {
    "data": {
        "updateMyCommunicationSubscriptions": {
            "guardian": {
                "firstName": "Michael",
                "hasAcceptedCommunication": True,
                "language": "fi",
                "lastName": "Patton",
            }
        }
    }
}

snapshots["test_update_my_communication_subscriptions_as_logged_in[True] 1"] = {
    "data": {
        "updateMyCommunicationSubscriptions": {
            "guardian": {
                "firstName": "Michael",
                "hasAcceptedCommunication": False,
                "language": "fi",
                "lastName": "Patton",
            }
        }
    }
}

snapshots[
    "test_update_my_communication_subscriptions_returns_errors_without_required_args[variables0] 1"
] = {
    "errors": [
        {
            "extensions": {"code": "GENERAL_ERROR"},
            "locations": [{"column": 3, "line": 3}],
            "message": """Variable "$input" got invalid value {}.
In field "hasAcceptedCommunication": Expected "Boolean!", found null.""",
        }
    ]
}

snapshots[
    "test_update_my_communication_subscriptions_returns_errors_without_required_args[variables1] 1"
] = {
    "errors": [
        {
            "extensions": {"code": "GENERAL_ERROR"},
            "locations": [{"column": 3, "line": 3}],
            "message": 'Variable "$input" of required type "UpdateMyCommunicationSubscriptionsMutationInput!" was not provided.',
        }
    ]
}

snapshots[
    "test_update_my_communication_subscriptions_returns_errors_without_required_args[variables2] 1"
] = {
    "errors": [
        {
            "extensions": {"code": "GENERAL_ERROR"},
            "locations": [{"column": 3, "line": 3}],
            "message": """Variable "$input" got invalid value {"authToken": "what ever"}.
In field "hasAcceptedCommunication": Expected "Boolean!", found null.""",
        }
    ]
}

snapshots[
    "test_update_my_communication_subscriptions_with_auth_verification_token[False] 1"
] = {
    "data": {
        "updateMyCommunicationSubscriptions": {
            "guardian": {
                "firstName": "Michael",
                "hasAcceptedCommunication": True,
                "language": "fi",
                "lastName": "Patton",
            }
        }
    }
}

snapshots[
    "test_update_my_communication_subscriptions_with_auth_verification_token[True] 1"
] = {
    "data": {
        "updateMyCommunicationSubscriptions": {
            "guardian": {
                "firstName": "Michael",
                "hasAcceptedCommunication": False,
                "language": "fi",
                "lastName": "Patton",
            }
        }
    }
}

snapshots["test_update_my_email_mutation[changed-email@kummilapset.fi-True] 1"] = {
    "data": {"updateMyEmail": {"myProfile": {"email": "changed-email@kummilapset.fi"}}}
}

snapshots["test_update_my_profile_mutation 1"] = {
    "data": {
        "updateMyProfile": {
            "myProfile": {
                "firstName": "Updated First Name",
                "hasAcceptedCommunication": False,
                "language": "EN",
                "languagesSpokenAtHome": {
                    "edges": [
                        {"node": {"alpha3Code": "swe"}},
                        {"node": {"alpha3Code": "fin"}},
                    ]
                },
                "lastName": "Updated Last Name",
                "phoneNumber": "Updated phone number",
            }
        }
    }
}
