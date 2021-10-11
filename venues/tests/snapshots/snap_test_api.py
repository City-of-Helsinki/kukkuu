# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_add_venue_project_user 1"] = {
    "data": {
        "addVenue": {
            "venue": {
                "project": {"year": 2020},
                "translations": [
                    {
                        "accessibilityInfo": "Accessibility info",
                        "additionalInfo": "Additional info",
                        "address": "Address",
                        "arrivalInstructions": "Arrival instruction",
                        "description": "Venue description",
                        "languageCode": "FI",
                        "name": "Venue name",
                        "wcAndFacilities": "WC & Facilities",
                        "wwwUrl": "www.url.com",
                    }
                ],
            }
        }
    }
}

snapshots["test_update_venue_project_user 1"] = {
    "data": {
        "updateVenue": {
            "venue": {
                "project": {"year": 2020},
                "translations": [
                    {
                        "accessibilityInfo": "Accessibility info",
                        "additionalInfo": "Additional info",
                        "address": "Address",
                        "arrivalInstructions": "Arrival instruction",
                        "description": "Venue description",
                        "languageCode": "FI",
                        "name": "Venue name",
                        "wcAndFacilities": "WC & Facilities",
                        "wwwUrl": "www.url.com",
                    }
                ],
            }
        }
    }
}

snapshots["test_venue_query_normal_user 1"] = {
    "data": {
        "venue": {
            "accessibilityInfo": """Sit enter stand himself from daughter order. Sign discover eight.
Scientist service wonder everything pay. Moment strong hand push book and interesting sit.""",
            "additionalInfo": "Training thought price. Effort clear and local challenge box. Care figure mention wrong when lead involve.",
            "address": """04883 Mary Corner
Port Mikeview, IN 23956""",
            "arrivalInstructions": "Benefit treat final central. Past ready join enjoy. Huge get this success commercial recently from.",
            "description": """Together history perform. Respond draw military dog hospital number. Certainly again thought summer because serious listen.
Page box child care any concern. Defense level church use.""",
            "name": "Poor lawyer treat free heart significant.",
            "occurrences": {"edges": []},
            "project": {"year": 2020},
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
                    "wcAndFacilities": """State social believe policy. Score think turn argue present.
Prevent pressure point. Voice radio happen color scene.
Assume training seek full several. Authority develop identify ready.""",
                    "wwwUrl": "http://www.brooks.com/",
                }
            ],
            "wcAndFacilities": """State social believe policy. Score think turn argue present.
Prevent pressure point. Voice radio happen color scene.
Assume training seek full several. Authority develop identify ready.""",
            "wwwUrl": "http://www.brooks.com/",
        }
    }
}

snapshots["test_venues_project_filter 1"] = {
    "data": {"venues": {"edges": [{"node": {"name": "Should be returned"}}]}}
}

snapshots["test_venues_query_normal_user 1"] = {
    "data": {
        "venues": {
            "edges": [
                {
                    "node": {
                        "accessibilityInfo": """Sit enter stand himself from daughter order. Sign discover eight.
Scientist service wonder everything pay. Moment strong hand push book and interesting sit.""",
                        "additionalInfo": "Training thought price. Effort clear and local challenge box. Care figure mention wrong when lead involve.",
                        "address": """04883 Mary Corner
Port Mikeview, IN 23956""",
                        "arrivalInstructions": "Benefit treat final central. Past ready join enjoy. Huge get this success commercial recently from.",
                        "description": """Together history perform. Respond draw military dog hospital number. Certainly again thought summer because serious listen.
Page box child care any concern. Defense level church use.""",
                        "name": "Poor lawyer treat free heart significant.",
                        "occurrences": {"edges": []},
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
                        ],
                        "wcAndFacilities": """State social believe policy. Score think turn argue present.
Prevent pressure point. Voice radio happen color scene.
Assume training seek full several. Authority develop identify ready.""",
                        "wwwUrl": "http://www.brooks.com/",
                    }
                }
            ]
        }
    }
}

snapshots["test_venues_query_ordering[en] 1"] = {
    "data": {
        "venues": {
            "edges": [
                {"node": {"name": "2 in Finnish"}},
                {"node": {"name": "1 in English"}},
                {"node": {"name": "4 in Finnish"}},
            ]
        }
    }
}

snapshots["test_venues_query_ordering[fi] 1"] = {
    "data": {
        "venues": {
            "edges": [
                {"node": {"name": "2 in Finnish"}},
                {"node": {"name": "3 in Finnish"}},
                {"node": {"name": "4 in Finnish"}},
            ]
        }
    }
}
