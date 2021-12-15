# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_children_endpoint 1"] = [
    {
        "birth_year": 2021,
        "contact_language": "fin",
        "languages_spoken_at_home": ["fin", "__OTHER__"],
        "postal_code": "11111",
        "registration_date": "2021-02-02",
    },
    {
        "birth_year": 2021,
        "contact_language": "swe",
        "languages_spoken_at_home": ["__OTHER__"],
        "postal_code": "22222",
        "registration_date": "2021-03-03",
    },
    {
        "birth_year": 2020,
        "contact_language": "eng",
        "languages_spoken_at_home": [],
        "postal_code": "33333",
        "registration_date": "2021-04-05",
    },
]
