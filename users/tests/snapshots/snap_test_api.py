# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_guardians_query_project_user_with_global_view_families_perm 1'] = {
    'data': {
        'guardians': {
            'edges': [
                {
                    'node': {
                        'email': 'debbie77@example.com',
                        'firstName': 'Guardian having children in own and another project',
                        'lastName': 'Should be visible 1/2',
                        'phoneNumber': '(971)824-0675x0649',
                        'relationships': {
                            'edges': [
                                {
                                    'node': {
                                        'child': {
                                            'birthyear': 2019,
                                            'name': 'Cynthia Holmes',
                                            'project': {
                                                'year': 2020
                                            }
                                        },
                                        'type': 'PARENT'
                                    }
                                }
                            ]
                        }
                    }
                },
                {
                    'node': {
                        'email': 'michellewalker@example.net',
                        'firstName': 'Another project own guardian',
                        'lastName': 'Should be visible 2/2',
                        'phoneNumber': '420.928.1307',
                        'relationships': {
                            'edges': [
                                {
                                    'node': {
                                        'child': {
                                            'birthyear': 2022,
                                            'name': 'Sara Johnson',
                                            'project': {
                                                'year': 2030
                                            }
                                        },
                                        'type': 'OTHER_RELATION'
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

snapshots['test_my_admin_profile_project_admin[has_also_model_perm] 1'] = {
    'data': {
        'myAdminProfile': {
            'projects': {
                'edges': [
                    {
                        'node': {
                            'myPermissions': {
                                'canSendToAllInProject': True,
                                'manageEventGroups': True,
                                'publish': True
                            },
                            'name': 'Helsingin kaupunginorkesteri'
                        }
                    },
                    {
                        'node': {
                            'myPermissions': {
                                'canSendToAllInProject': True,
                                'manageEventGroups': True,
                                'publish': True
                            },
                            'name': 'Helsingin Kaupunginteatteri, Suomen Kansallisteatteri, Svenska Teatern, Teatteri ILMI Ö., Q-teatteri ja Nukketeatteri Sampo'
                        }
                    },
                    {
                        'node': {
                            'myPermissions': {
                                'canSendToAllInProject': True,
                                'manageEventGroups': True,
                                'publish': True
                            },
                            'name': 'Cirko - uuden sirkuksen keskus, Hotelli- ja ravintolamuseo, Suomen valokuvataiteen museo, Tanssin talo, Tanssiteatteri Hurjaruuth ja Teatterimuseo'
                        }
                    },
                    {
                        'node': {
                            'myPermissions': {
                                'canSendToAllInProject': True,
                                'manageEventGroups': True,
                                'publish': True
                            },
                            'name': 'Arkkitehtuurimuseo, Designmuseo, Helsingin kaupunginmuseo, Suomen kansallismuseo, Suomen kulttuuriperintökasvatuksen seura ja Tiedemuseo Liekki'
                        }
                    },
                    {
                        'node': {
                            'myPermissions': {
                                'canSendToAllInProject': True,
                                'manageEventGroups': True,
                                'publish': True
                            },
                            'name': 'Helsingin kirjasto- ja liikuntapalvelut'
                        }
                    },
                    {
                        'node': {
                            'myPermissions': {
                                'canSendToAllInProject': True,
                                'manageEventGroups': True,
                                'publish': True
                            },
                            'name': 'HAM Helsingin taidemuseo, Amos Rex, Sointi Jazz Orchestra, UMO Helsinki Jazz Orchestra ja Kansallisgalleria: Ateneumin taidemuseo, Nykytaiteen museo Kiasma ja Sinebrychoffin taidemuseo'
                        }
                    },
                    {
                        'node': {
                            'myPermissions': {
                                'canSendToAllInProject': True,
                                'manageEventGroups': True,
                                'publish': True
                            },
                            'name': 'project where no object perms'
                        }
                    },
                    {
                        'node': {
                            'myPermissions': {
                                'canSendToAllInProject': True,
                                'manageEventGroups': True,
                                'publish': True
                            },
                            'name': 'project where base admin object perm but no other object perms'
                        }
                    },
                    {
                        'node': {
                            'myPermissions': {
                                'canSendToAllInProject': True,
                                'manageEventGroups': True,
                                'publish': True
                            },
                            'name': 'project where base admin object perm and other object perms'
                        }
                    }
                ]
            }
        }
    }
}

snapshots['test_my_admin_profile_project_admin[no_model_perm] 1'] = {
    'data': {
        'myAdminProfile': {
            'projects': {
                'edges': [
                    {
                        'node': {
                            'myPermissions': {
                                'canSendToAllInProject': False,
                                'manageEventGroups': False,
                                'publish': False
                            },
                            'name': 'project where base admin object perm but no other object perms'
                        }
                    },
                    {
                        'node': {
                            'myPermissions': {
                                'canSendToAllInProject': True,
                                'manageEventGroups': True,
                                'publish': True
                            },
                            'name': 'project where base admin object perm and other object perms'
                        }
                    }
                ]
            }
        }
    }
}

snapshots['test_my_communication_subscriptions_query_as_logged_in[False] 1'] = {
    'data': {
        'myCommunicationSubscriptions': {
            'firstName': 'Michael',
            'hasAcceptedCommunication': False,
            'language': 'fi',
            'lastName': 'Patton'
        }
    }
}

snapshots['test_my_communication_subscriptions_query_as_logged_in[True] 1'] = {
    'data': {
        'myCommunicationSubscriptions': {
            'firstName': 'Michael',
            'hasAcceptedCommunication': True,
            'language': 'fi',
            'lastName': 'Patton'
        }
    }
}

snapshots['test_my_communication_subscriptions_query_with_auth_verification_token 1'] = {
    'data': {
        'myCommunicationSubscriptions': {
            'firstName': 'Michael',
            'hasAcceptedCommunication': True,
            'language': 'fi',
            'lastName': 'Patton'
        }
    }
}

snapshots['test_my_profile_no_profile 1'] = {
    'data': {
        'myProfile': None
    }
}

snapshots['test_my_profile_query 1'] = {
    'data': {
        'myProfile': {
            'email': 'michellewalker@example.net',
            'firstName': 'Robert',
            'hasAcceptedCommunication': False,
            'language': 'FI',
            'languagesSpokenAtHome': {
                'edges': [
                ]
            },
            'lastName': 'Crane',
            'phoneNumber': '303.746.6972x70117',
            'relationships': {
                'edges': [
                    {
                        'node': {
                            'child': {
                                'birthyear': 2019,
                                'name': 'Ashley Hernandez',
                                'postalCode': '28130'
                            },
                            'type': 'OTHER_GUARDIAN'
                        }
                    }
                ]
            }
        }
    }
}

snapshots['test_my_profile_query_email[] 1'] = {
    'data': {
        'myProfile': {
            'email': 'user@example.com'
        }
    }
}

snapshots['test_my_profile_query_email[guardian@example.com] 1'] = {
    'data': {
        'myProfile': {
            'email': 'guardian@example.com'
        }
    }
}

snapshots['test_request_email_change_token_mutation 1'] = {
    'data': {
        'requestEmailUpdateToken': {
            'email': 'new-email@kummilapset.fi',
            'emailUpdateTokenRequested': True
        }
    }
}

snapshots['test_update_my_communication_subscriptions_as_logged_in[False] 1'] = {
    'data': {
        'updateMyCommunicationSubscriptions': {
            'guardian': {
                'firstName': 'Michael',
                'hasAcceptedCommunication': True,
                'language': 'fi',
                'lastName': 'Patton'
            }
        }
    }
}

snapshots['test_update_my_communication_subscriptions_as_logged_in[True] 1'] = {
    'data': {
        'updateMyCommunicationSubscriptions': {
            'guardian': {
                'firstName': 'Michael',
                'hasAcceptedCommunication': False,
                'language': 'fi',
                'lastName': 'Patton'
            }
        }
    }
}

snapshots['test_update_my_communication_subscriptions_returns_errors_without_required_args[variables0] 1'] = {
    'data': None,
    'errors': [
        {
            'extensions': {
                'code': 'GENERAL_ERROR'
            },
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': "Variable '$input' got invalid value {}; Field 'hasAcceptedCommunication' of required type 'Boolean!' was not provided."
        }
    ]
}

snapshots['test_update_my_communication_subscriptions_returns_errors_without_required_args[variables1] 1'] = {
    'data': None,
    'errors': [
        {
            'extensions': {
                'code': 'GENERAL_ERROR'
            },
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': "Variable '$input' of required type 'UpdateMyCommunicationSubscriptionsMutationInput!' was not provided."
        }
    ]
}

snapshots['test_update_my_communication_subscriptions_returns_errors_without_required_args[variables2] 1'] = {
    'data': None,
    'errors': [
        {
            'extensions': {
                'code': 'GENERAL_ERROR'
            },
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': "Variable '$input' got invalid value {'authToken': 'what ever'}; Field 'hasAcceptedCommunication' of required type 'Boolean!' was not provided."
        }
    ]
}

snapshots['test_update_my_communication_subscriptions_with_auth_verification_token[False] 1'] = {
    'data': {
        'updateMyCommunicationSubscriptions': {
            'guardian': {
                'firstName': 'Michael',
                'hasAcceptedCommunication': True,
                'language': 'fi',
                'lastName': 'Patton'
            }
        }
    }
}

snapshots['test_update_my_communication_subscriptions_with_auth_verification_token[True] 1'] = {
    'data': {
        'updateMyCommunicationSubscriptions': {
            'guardian': {
                'firstName': 'Michael',
                'hasAcceptedCommunication': False,
                'language': 'fi',
                'lastName': 'Patton'
            }
        }
    }
}

snapshots['test_update_my_email_mutation[changed-email@kummilapset.fi-True] 1'] = {
    'data': {
        'updateMyEmail': {
            'myProfile': {
                'email': 'changed-email@kummilapset.fi'
            }
        }
    }
}

snapshots['test_update_my_profile_mutation 1'] = {
    'data': {
        'updateMyProfile': {
            'myProfile': {
                'firstName': 'Updated First Name',
                'hasAcceptedCommunication': False,
                'language': 'EN',
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
                'lastName': 'Updated Last Name',
                'phoneNumber': 'Updated phone number'
            }
        }
    }
}
