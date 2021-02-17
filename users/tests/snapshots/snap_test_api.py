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
                        "email": "mperez@cox.com",
                        "firstName": "Sandra",
                        "lastName": "Meyer",
                        "phoneNumber": "(727)708-9817",
                        "relationships": {
                            "edges": [
                                {
                                    "node": {
                                        "child": {
                                            "birthdate": "2020-11-22",
                                            "firstName": "Christopher",
                                            "lastName": "Jones",
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
                        "email": "ramirezandrew@burns.com",
                        "firstName": "Guardian having children in own and another project",
                        "lastName": "Should be visible 1/2",
                        "phoneNumber": "638.034.6697x2701",
                        "relationships": {
                            "edges": [
                                {
                                    "node": {
                                        "child": {
                                            "birthdate": "2020-09-05",
                                            "firstName": "Craig",
                                            "lastName": "Oneill",
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
                        "email": "mperez@cox.com",
                        "firstName": "Another project own guardian",
                        "lastName": "Should be visible 2/2",
                        "phoneNumber": "708-981-7101",
                        "relationships": {
                            "edges": [
                                {
                                    "node": {
                                        "child": {
                                            "birthdate": "2020-04-08",
                                            "firstName": "Elizabeth",
                                            "lastName": "Jackson",
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
                                "publish": False,
                            },
                            "name": "Helsingin kaupunginorkesteri",
                        }
                    },
                    {
                        "node": {
                            "myPermissions": {
                                "manageEventGroups": True,
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
                    {
                        "node": {
                            "myPermissions": {
                                "manageEventGroups": True,
                                "publish": False,
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
            "email": "mperez@cox.com",
            "firstName": "Robin",
            "language": "FI",
            "languagesSpokenAtHome": {"edges": []},
            "lastName": "Moses",
            "phoneNumber": "910-232-0281",
            "relationships": {
                "edges": [
                    {
                        "node": {
                            "child": {
                                "birthdate": "2020-03-01",
                                "firstName": "Jason",
                                "lastName": "Owens",
                                "postalCode": "70898",
                            },
                            "type": "ADVOCATE",
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
