# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_children_endpoint 1"] = [
    {
        "birth_year": 2020,
        "child_birthdate_postal_code_guardian_emails_hash": "b5b9eea93c3646a569ad517bab7ffc287fa331a3b07bfcda41f1936ff90f80c5",
        "child_name_birthdate_postal_code_guardian_emails_hash": "1ad9ef9b725a22b13ecbee9dc0945b1a468240d7492923ec2d7eb4c67f5703ee",
        "contact_language": "eng",
        "languages_spoken_at_home": [],
        "postal_code": "33333",
        "registration_date": "2021-04-05",
    },
    {
        "birth_year": 2021,
        "child_birthdate_postal_code_guardian_emails_hash": "72fa21cf7750f88d4085086b143a56ec6ba196c98693f1e4e7f39b76f9e2803e",
        "child_name_birthdate_postal_code_guardian_emails_hash": "68ef0bbeef51ca5ff6282ec476c68fde6125383fe843ee00fe26a9536ccedfd0",
        "contact_language": "fin",
        "languages_spoken_at_home": ["fin", "__OTHER__"],
        "postal_code": "11111",
        "registration_date": "2021-02-02",
    },
    {
        "birth_year": 2021,
        "child_birthdate_postal_code_guardian_emails_hash": "db91f2de11ce26e8e49e179cd27e77805acc984af98aabab9d45987cc45c255c",
        "child_name_birthdate_postal_code_guardian_emails_hash": "ff50591af6bd0de44d49c016d479c86b28c5180305548ca3a60be9d6621a2cac",
        "contact_language": "swe",
        "languages_spoken_at_home": ["__OTHER__"],
        "postal_code": "22222",
        "registration_date": "2021-03-03",
    },
    {
        "birth_year": 2020,
        "child_birthdate_postal_code_guardian_emails_hash": "0fcf4364217ea26d51ab38193066474515824eaaf3f387eca934375e36b16ee1",
        "child_name_birthdate_postal_code_guardian_emails_hash": "87161feae33c32f46815b856d80ec4c564fb00ec680941245553982b2bd70f8c",
        "contact_language": "eng",
        "languages_spoken_at_home": [],
        "postal_code": "33333",
        "registration_date": "2021-04-06",
    },
]
