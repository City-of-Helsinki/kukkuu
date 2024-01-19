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
                        "firstName": "Ashley",
                        "lastName": "Castillo",
                        "phoneNumber": "011.715.9102x320",
                        "relationships": {
                            "edges": [
                                {
                                    "node": {
                                        "child": {
                                            "birthdate": "2020-07-21",
                                            "firstName": "Sandra",
                                            "project": {"year": 2020},
                                        },
                                        "type": "ADVOCATE",
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
                                            "birthdate": "2020-04-02",
                                            "firstName": "Jennifer",
                                            "project": {"year": 2020},
                                        },
                                        "type": "ADVOCATE",
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
                        "phoneNumber": "+1-102-320-2813x072",
                        "relationships": {
                            "edges": [
                                {
                                    "node": {
                                        "child": {
                                            "birthdate": "2020-09-11",
                                            "firstName": "Shawn",
                                            "project": {"year": 2030},
                                        },
                                        "type": "ADVOCATE",
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

snapshots["test_my_profile_no_profile 1"] = {"data": {"myProfile": None}}

snapshots["test_my_profile_query 1"] = {
    "data": {
        "myProfile": {
            "email": "michellewalker@example.net",
            "firstName": "Timothy",
            "language": "FI",
            "languagesSpokenAtHome": {"edges": []},
            "lastName": "Baldwin",
            "phoneNumber": "803.466.9727",
            "relationships": {
                "edges": [
                    {
                        "node": {
                            "child": {
                                "birthdate": "2020-12-10",
                                "firstName": "Andrew",
                                "postalCode": "17159",
                            },
                            "type": "PARENT",
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

snapshots["test_update_my_profile_mutation 1"] = {
    "data": {
        "updateMyProfile": {
            "myProfile": {
                "firstName": "Updated First Name",
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

snapshots[
    "test_update_my_profile_mutation_email[guardian_updated@example.com-True] 1"
] = {
    "data": {
        "updateMyProfile": {"myProfile": {"email": "guardian_updated@example.com"}}
    }
}
