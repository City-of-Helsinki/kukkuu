# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_guardians_query_staff_user 1"] = {
    "data": {
        "guardians": {
            "edges": [
                {
                    "node": {
                        "email": "ramirezandrew@burns.com",
                        "firstName": "Christy",
                        "lastName": "Jenkins",
                        "phoneNumber": "001-803-466-9727x0117",
                        "relationships": {
                            "edges": [
                                {
                                    "node": {
                                        "child": {
                                            "birthdate": "2020-02-14",
                                            "firstName": "Robin",
                                            "lastName": "Moses",
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

snapshots["test_my_profile_no_profile 1"] = {"data": {"myProfile": None}}

snapshots["test_update_my_profile_mutation 1"] = {
    "data": {
        "updateMyProfile": {
            "myProfile": {
                "firstName": "Updated First Name",
                "language": "EN",
                "lastName": "Updated Last Name",
                "phoneNumber": "Updated phone number",
            }
        }
    }
}

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

snapshots["test_my_profile_query 1"] = {
    "data": {
        "myProfile": {
            "email": "mperez@cox.com",
            "firstName": "Robin",
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

snapshots["test_my_admin_profile_project_admin 1"] = {
    "data": {
        "myAdminProfile": {
            "projects": {"edges": [{"node": {"name": "my only project"}}]}
        }
    }
}

snapshots["test_my_profile_query_email[guardian@example.com] 1"] = {
    "data": {"myProfile": {"email": "guardian@example.com"}}
}

snapshots["test_my_profile_query_email[] 1"] = {
    "data": {"myProfile": {"email": "user@example.com"}}
}

snapshots[
    "test_update_my_profile_mutation_email[guardian_updated@example.com-True] 1"
] = {
    "data": {
        "updateMyProfile": {"myProfile": {"email": "guardian_updated@example.com"}}
    }
}
