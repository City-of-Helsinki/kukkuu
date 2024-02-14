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
                        "firstName": "Dustin",
                        "lastName": "Smith",
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
                                            "birthyear": 2019,
                                            "name": "Cynthia Holmes",
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
                        "phoneNumber": "2320281307",
                        "relationships": {
                            "edges": [
                                {
                                    "node": {
                                        "child": {
                                            "birthyear": 2021,
                                            "name": "Jodi Douglas",
                                            "project": {"year": 2030},
                                        },
                                        "type": "PARENT",
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
                                "birthyear": 2018,
                                "name": "Stephen Charles",
                                "postalCode": "71591",
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

snapshots["test_request_email_change_token_mutation 1"] = {
    "data": {
        "requestEmailUpdateToken": {
            "email": "new-email@kummilapset.fi",
            "emailUpdateTokenRequested": True,
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
