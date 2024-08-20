# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_add_message[None] 1"] = {
    "data": {
        "addMessage": {
            "message": {
                "event": None,
                "occurrences": {"edges": []},
                "project": {"year": 2020},
                "protocol": "EMAIL",
                "recipientCount": 0,
                "recipientSelection": "ALL",
                "sentAt": None,
                "translations": [
                    {
                        "bodyText": "Testiteksti",
                        "languageCode": "FI",
                        "subject": "Testiotsikko",
                    }
                ],
            }
        }
    }
}

snapshots["test_add_message[event] 1"] = {
    "data": {
        "addMessage": {
            "message": {
                "event": {"name": "Poor lawyer treat free heart significant."},
                "occurrences": {"edges": []},
                "project": {"year": 2020},
                "protocol": "EMAIL",
                "recipientCount": 0,
                "recipientSelection": "ALL",
                "sentAt": None,
                "translations": [
                    {
                        "bodyText": "Testiteksti",
                        "languageCode": "FI",
                        "subject": "Testiotsikko",
                    }
                ],
            }
        }
    }
}

snapshots["test_add_message[occurrences] 1"] = {
    "data": {
        "addMessage": {
            "message": {
                "event": {"name": "Poor lawyer treat free heart significant."},
                "occurrences": {
                    "edges": [
                        {"node": {"time": "1970-12-29T14:27:50.629900+00:00"}},
                        {"node": {"time": "1977-02-25T23:14:59.889967+00:00"}},
                        {"node": {"time": "1997-09-11T01:32:17.610651+00:00"}},
                    ]
                },
                "project": {"year": 2020},
                "protocol": "EMAIL",
                "recipientCount": 0,
                "recipientSelection": "ALL",
                "sentAt": None,
                "translations": [
                    {
                        "bodyText": "Testiteksti",
                        "languageCode": "FI",
                        "subject": "Testiotsikko",
                    }
                ],
            }
        }
    }
}

snapshots["test_cannot_do_message_query_unauthorized_wrong_project 1"] = {
    "data": {"message": None}
}

snapshots["test_delete_message 1"] = {
    "data": {"deleteMessage": {"clientMutationId": None}}
}

snapshots["test_message_query 1"] = {
    "data": {
        "message": {
            "bodyText": "Ruumisteksti.",
            "event": None,
            "occurrences": {"edges": []},
            "project": {"year": 2020},
            "recipientCount": 0,
            "recipientSelection": "ALL",
            "sentAt": None,
            "subject": "Otsikko",
        }
    }
}

snapshots["test_messages_query 1"] = {
    "data": {
        "messages": {
            "edges": [
                {
                    "node": {
                        "bodyText": "Ruumisteksti.",
                        "event": None,
                        "occurrences": {"edges": []},
                        "project": {"year": 2020},
                        "protocol": "EMAIL",
                        "recipientCount": 0,
                        "recipientSelection": "ALL",
                        "sentAt": None,
                        "subject": "Otsikko",
                    }
                }
            ]
        }
    }
}

snapshots["test_messages_query_occurrences_filter 1"] = {
    "data": {
        "messages": {
            "edges": [
                {
                    "node": {
                        "bodyText": "Free heart significant machine try. President compare room hotel town south among. Fall long respond draw military dog. Increase thank certainly again thought summer. Beyond than trial western.",
                        "event": None,
                        "occurrences": {
                            "edges": [
                                {"node": {"time": "1980-08-23T04:46:09.363315+00:00"}}
                            ]
                        },
                        "project": {"year": 2020},
                        "protocol": "EMAIL",
                        "recipientCount": 0,
                        "recipientSelection": "ALL",
                        "sentAt": None,
                        "subject": "Him question stay.",
                    }
                },
                {
                    "node": {
                        "bodyText": "Child care any. Minute defense level church. Alone our very television beat at success.",
                        "event": None,
                        "occurrences": {
                            "edges": [
                                {"node": {"time": "1980-08-23T04:46:09.363315+00:00"}}
                            ]
                        },
                        "project": {"year": 2020},
                        "protocol": "EMAIL",
                        "recipientCount": 0,
                        "recipientSelection": "ALL",
                        "sentAt": None,
                        "subject": "Business hot PM.",
                    }
                },
                {
                    "node": {
                        "bodyText": "Focus significant kind. Laugh smile behavior whom gas. Significant minute rest. Special far magazine.",
                        "event": None,
                        "occurrences": {
                            "edges": [
                                {"node": {"time": "2003-01-02T18:10:46.571751+00:00"}}
                            ]
                        },
                        "project": {"year": 2020},
                        "protocol": "EMAIL",
                        "recipientCount": 0,
                        "recipientSelection": "ALL",
                        "sentAt": None,
                        "subject": "Attention practice.",
                    }
                },
                {
                    "node": {
                        "bodyText": "Conference carry factor front Mr amount conference thing. Positive cold start rest tonight including believe. Respond range bit college question. Stop treatment suggest. Sometimes growth check court.",
                        "event": None,
                        "occurrences": {
                            "edges": [
                                {"node": {"time": "2003-01-02T18:10:46.571751+00:00"}}
                            ]
                        },
                        "project": {"year": 2020},
                        "protocol": "EMAIL",
                        "recipientCount": 0,
                        "recipientSelection": "ALL",
                        "sentAt": None,
                        "subject": "Past life thus.",
                    }
                },
            ]
        }
    }
}

snapshots["test_messages_query_project_filter 1"] = {
    "data": {
        "messages": {
            "edges": [
                {
                    "node": {
                        "bodyText": "Ruumisteksti.",
                        "event": None,
                        "occurrences": {"edges": []},
                        "project": {"year": 2020},
                        "protocol": "EMAIL",
                        "recipientCount": 0,
                        "recipientSelection": "ALL",
                        "sentAt": None,
                        "subject": "Otsikko",
                    }
                }
            ]
        }
    }
}

snapshots["test_messages_query_protocol_filter[email] 1"] = {
    "data": {
        "messages": {
            "edges": [
                {
                    "node": {
                        "bodyText": "Which president smile staff country actually generation. Age member whatever open effort clear. Difficult look can. Care figure mention wrong when lead involve. Event lay yes policy data control as receive.",
                        "event": None,
                        "occurrences": {"edges": []},
                        "project": {"year": 2020},
                        "protocol": "EMAIL",
                        "recipientCount": 0,
                        "recipientSelection": "ALL",
                        "sentAt": None,
                        "subject": "Partner exist true.",
                    }
                },
                {
                    "node": {
                        "bodyText": "Girl middle same space speak. Person the probably deep center develop character situation. Score think turn argue present.",
                        "event": None,
                        "occurrences": {"edges": []},
                        "project": {"year": 2020},
                        "protocol": "EMAIL",
                        "recipientCount": 0,
                        "recipientSelection": "ALL",
                        "sentAt": None,
                        "subject": "Decade every town.",
                    }
                },
                {
                    "node": {
                        "bodyText": "Voice radio happen color scene. Create state rock only. Several behavior media career decide season mission TV. Work head table city central deep response. Through resource professional debate produce college able.",
                        "event": None,
                        "occurrences": {"edges": []},
                        "project": {"year": 2020},
                        "protocol": "EMAIL",
                        "recipientCount": 0,
                        "recipientSelection": "ALL",
                        "sentAt": None,
                        "subject": "Walk fish teach.",
                    }
                },
                {
                    "node": {
                        "bodyText": "Sea something western research. Candidate century network bar hear quite wonder. Up always sport return. Light a point charge stand store. Generation able take food share.",
                        "event": None,
                        "occurrences": {"edges": []},
                        "project": {"year": 2020},
                        "protocol": "EMAIL",
                        "recipientCount": 0,
                        "recipientSelection": "ALL",
                        "sentAt": None,
                        "subject": "Product issue along.",
                    }
                },
                {
                    "node": {
                        "bodyText": "Site chance of performance. Hand cause receive kitchen middle. Step able last in able local garden. Nearly gun two born land military first.",
                        "event": None,
                        "occurrences": {"edges": []},
                        "project": {"year": 2020},
                        "protocol": "EMAIL",
                        "recipientCount": 0,
                        "recipientSelection": "ALL",
                        "sentAt": None,
                        "subject": "Discussion remain.",
                    }
                },
            ]
        }
    }
}

snapshots["test_messages_query_protocol_filter[sms] 1"] = {
    "data": {
        "messages": {
            "edges": [
                {
                    "node": {
                        "bodyText": "Free heart significant machine try. President compare room hotel town south among. Fall long respond draw military dog. Increase thank certainly again thought summer. Beyond than trial western.",
                        "event": None,
                        "occurrences": {"edges": []},
                        "project": {"year": 2020},
                        "protocol": "SMS",
                        "recipientCount": 0,
                        "recipientSelection": "ALL",
                        "sentAt": None,
                        "subject": "Him question stay.",
                    }
                },
                {
                    "node": {
                        "bodyText": "Child care any. Minute defense level church. Alone our very television beat at success.",
                        "event": None,
                        "occurrences": {"edges": []},
                        "project": {"year": 2020},
                        "protocol": "SMS",
                        "recipientCount": 0,
                        "recipientSelection": "ALL",
                        "sentAt": None,
                        "subject": "Business hot PM.",
                    }
                },
                {
                    "node": {
                        "bodyText": "Enter everything history remember stay public high. Exist shoulder write century. Never skill down subject town. According hard enough watch condition like lay.",
                        "event": None,
                        "occurrences": {"edges": []},
                        "project": {"year": 2020},
                        "protocol": "SMS",
                        "recipientCount": 0,
                        "recipientSelection": "ALL",
                        "sentAt": None,
                        "subject": "Detail.",
                    }
                },
                {
                    "node": {
                        "bodyText": "From daughter order stay sign discover eight. Toward scientist service wonder everything. Middle moment strong hand push book and interesting. Near increase process truth list pressure. Capital city sing himself yard stuff.",
                        "event": None,
                        "occurrences": {"edges": []},
                        "project": {"year": 2020},
                        "protocol": "SMS",
                        "recipientCount": 0,
                        "recipientSelection": "ALL",
                        "sentAt": None,
                        "subject": "Their tell.",
                    }
                },
                {
                    "node": {
                        "bodyText": "Base may middle good father boy economy. Fly discussion huge get this success. Science sort already name. Senior number scene today friend maintain marriage.",
                        "event": None,
                        "occurrences": {"edges": []},
                        "project": {"year": 2020},
                        "protocol": "SMS",
                        "recipientCount": 0,
                        "recipientSelection": "ALL",
                        "sentAt": None,
                        "subject": "Even perhaps that.",
                    }
                },
            ]
        }
    }
}

snapshots["test_send_message 1"] = {
    "data": {
        "sendMessage": {
            "message": {
                "protocol": "EMAIL",
                "recipientCount": 1,
                "sentAt": "2020-12-12T00:00:00+00:00",
                "subject": "Otsikko",
            }
        }
    }
}

snapshots["test_send_sms_message_sent_with_default_language 1"] = {
    "data": {
        "sendMessage": {
            "message": {
                "protocol": "SMS",
                "recipientCount": 1,
                "sentAt": "2020-12-12T00:00:00+00:00",
                "subject": "Otsikko",
            }
        }
    }
}

snapshots["test_update_message[None] 1"] = {
    "data": {
        "updateMessage": {
            "message": {
                "event": {"name": "Poor lawyer treat free heart significant."},
                "occurrences": {"edges": []},
                "project": {"year": 2020},
                "protocol": "SMS",
                "recipientCount": 0,
                "recipientSelection": "ATTENDED",
                "sentAt": None,
                "translations": [
                    {
                        "bodyText": "Päivitetty testiteksti.",
                        "languageCode": "FI",
                        "subject": "Päivitetty testiotsikko",
                    }
                ],
            }
        }
    }
}

snapshots["test_update_message[event] 1"] = {
    "data": {
        "updateMessage": {
            "message": {
                "event": {
                    "name": "Up property work indeed take. Popular care receive camera."
                },
                "occurrences": {"edges": []},
                "project": {"year": 2020},
                "protocol": "SMS",
                "recipientCount": 0,
                "recipientSelection": "ATTENDED",
                "sentAt": None,
                "translations": [
                    {
                        "bodyText": "Päivitetty testiteksti.",
                        "languageCode": "FI",
                        "subject": "Päivitetty testiotsikko",
                    }
                ],
            }
        }
    }
}

snapshots["test_update_message[event_and_occurrences] 1"] = {
    "data": {
        "updateMessage": {
            "message": {
                "event": {
                    "name": "Up property work indeed take. Popular care receive camera."
                },
                "occurrences": {
                    "edges": [{"node": {"time": "2016-08-16T07:10:00+00:00"}}]
                },
                "project": {"year": 2020},
                "protocol": "SMS",
                "recipientCount": 0,
                "recipientSelection": "ATTENDED",
                "sentAt": None,
                "translations": [
                    {
                        "bodyText": "Päivitetty testiteksti.",
                        "languageCode": "FI",
                        "subject": "Päivitetty testiotsikko",
                    }
                ],
            }
        }
    }
}
