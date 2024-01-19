# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_children_endpoint 1"] = [
    {
        "birth_year": 2020,
        "child_birthyear_postal_code_guardian_emails_hash": "3b78fc2b60381829414bd2bd9ea53e90123d9cd7faeb35f86f5038d669dd96e0",
        "child_name_birthyear_postal_code_guardian_emails_hash": "bd94f9a87d842f6889f10aa72528a273c27fb864fe7b14b7b38b2b37a59b615a",
        "contact_language": "eng",
        "languages_spoken_at_home": [],
        "postal_code": "33333",
        "registration_date": "2021-04-05",
    },
    {
        "birth_year": 2021,
        "child_birthyear_postal_code_guardian_emails_hash": "d9653e3210babd7c8d6094f069ddfbf790d6b16d368d0b14e0d4f9d1d2eed8aa",
        "child_name_birthyear_postal_code_guardian_emails_hash": "cde8b66cfb17f9dd1e3a27b34ced099567555c09ac53ab8d96eb6f108b481a78",
        "contact_language": "fin",
        "languages_spoken_at_home": ["fin", "__OTHER__"],
        "postal_code": "11111",
        "registration_date": "2021-02-02",
    },
    {
        "birth_year": 2021,
        "child_birthyear_postal_code_guardian_emails_hash": "73471fad7bbcffa243a695f211ffd2c0ddb89531d747548709c3677ecbe4a0cc",
        "child_name_birthyear_postal_code_guardian_emails_hash": "c056d2e1b6ca2ab0189ce068567cb6d3951928283e8ebbb384ec20d3a85f632e",
        "contact_language": "swe",
        "languages_spoken_at_home": ["__OTHER__"],
        "postal_code": "22222",
        "registration_date": "2021-03-03",
    },
    {
        "birth_year": 2020,
        "child_birthyear_postal_code_guardian_emails_hash": "f1694b9c7d7a45c8606d9506f171025079940fcc97d5e125e1cc73495461f378",
        "child_name_birthyear_postal_code_guardian_emails_hash": "92d10305295a1210620ae3158c5aeecc24d9018be279042e8226d120cbfdb978",
        "contact_language": "eng",
        "languages_spoken_at_home": [],
        "postal_code": "44444",
        "registration_date": "2021-04-06",
    },
]
